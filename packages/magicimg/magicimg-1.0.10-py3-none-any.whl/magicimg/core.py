"""
Xử lý và tiền xử lý ảnh cho hệ thống OCR
"""

import cv2
import numpy as np
import os
import logging
import time
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union
from dataclasses import dataclass
import json
import gc

# Thiết lập logging - chỉ set format nếu chưa có handler
if not logging.getLogger().handlers:
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ImageQualityMetrics:
    """Lưu trữ các chỉ số chất lượng ảnh"""
    blur_index: float
    dark_ratio: float
    brightness: float
    contrast: float
    resolution: Tuple[int, int]
    quality_score: float = 0.0
    warnings: List[str] = None
    
    def __post_init__(self):
        self.warnings = self.warnings or []
        
    def to_dict(self) -> Dict:
        return {
            "blur_index": self.blur_index,
            "dark_ratio": self.dark_ratio,
            "brightness": self.brightness,
            "contrast": self.contrast,
            "resolution": self.resolution,
            "quality_score": self.quality_score,
            "warnings": self.warnings
        }

@dataclass
class ProcessingResult:
    """Kết quả xử lý ảnh"""
    success: bool
    image: Optional[np.ndarray]
    quality_metrics: ImageQualityMetrics
    processing_steps: List[str]
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    debug_images: Dict[str, str] = None
    rotation_angle: float = 0.0
    
    def __post_init__(self):
        self.debug_images = self.debug_images or {}
        
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "quality_metrics": self.quality_metrics.to_dict(),
            "processing_steps": self.processing_steps,
            "output_path": self.output_path,
            "error_message": self.error_message,
            "debug_images": self.debug_images,
            "rotation_angle": self.rotation_angle
        }

class ImageProcessor:
    """Xử lý và tiền xử lý ảnh"""
    
    def __init__(self, debug_dir: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """Khởi tạo với cấu hình tùy chỉnh
        
        Args:
            debug_dir: Thư mục lưu ảnh debug, nếu None thì tắt chế độ debug
            config: Cấu hình tùy chỉnh cho xử lý ảnh
        """
        # Cấu hình mặc định
        self.config = {
            # Ngưỡng chất lượng
            "min_blur_index": 80.0,       # Giảm yêu cầu độ nét vì ảnh scan thường hơi mờ
            "max_dark_ratio": 0.2,        # Giảm ngưỡng pixel tối vì ảnh phiếu thường sáng
            "min_brightness": 180.0,      # Tăng yêu cầu độ sáng vì cần đọc text rõ ràng
            "min_contrast": 50.0,         # Tăng yêu cầu độ tương phản để phân biệt text và nền
            "min_resolution": (1000, 1400), # Tăng độ phân giải tối thiểu cho ảnh phiếu
            "min_quality_score": 0.7,     # Tăng yêu cầu chất lượng tổng thể
            
            # Ngưỡng xử lý
            "min_skew_angle": 0.3,        # Giảm ngưỡng phát hiện góc nghiêng
            "max_skew_angle": 30.0,       # Giảm góc nghiêng tối đa vì phiếu thường không bị nghiêng nhiều
            "min_rotation_confidence": 0.8,
            
            # Cấu hình debug
            "debug": debug_dir is not None,
            "debug_dir": debug_dir
        }
        
        # Cập nhật cấu hình từ tham số
        if config:
            self.config.update(config)
            
        # Tạo thư mục debug nếu cần
        if self.config["debug"] and self.config["debug_dir"]:
            os.makedirs(self.config["debug_dir"], exist_ok=True)
            
        # Ghi log cấu hình chỉ khi debug mode được bật
        if self.config["debug"]:
            logger.debug("Khởi tạo ImageProcessor với cấu hình:")
            for key, value in self.config.items():
                logger.debug(f"  - {key}: {value}")
        
        self.debug_dir = self.config["debug_dir"]
        self.debug = self.config["debug"]
        
        # Cập nhật từ khóa tiếng Việt
        self.keywords = self.config.get("ballot_keywords", []) + [
            # Từ khóa hành chính
            "bau cu", "dang", "cong hoa", "xa hoi", "viet nam",
            "phieu", "ho ten", "stt", "so thu tu", "chu ky",
            
            # Từ và họ phổ biến trong phiếu bầu
            "nguyen", "tran", "le", "pham", "hoang", "do",
            "thi", "van", "duc", "anh", "quang", "thanh"
        ]
        
        # Chữ cái đặc biệt để xác định hướng dựa trên contour
        self.orientation_chars = ['c', 'C', 'a', 'A', 'v', 'V', 'n', 'N', '9', '6', 'p', 'q', 'g']
        
    def __del__(self):
        """Giải phóng tài nguyên khi hủy đối tượng"""
        gc.collect()
        
    def _check_image_quality(self, image) -> ImageQualityMetrics:
        """Kiểm tra chất lượng ảnh và trả về metrics
        
        Args:
            image: Ảnh cần kiểm tra (numpy array)
            
        Returns:
            ImageQualityMetrics: Thông tin chất lượng ảnh
        """
        # Chuyển đổi sang ảnh xám nếu cần
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Tính các chỉ số chất lượng
        blur_index = cv2.Laplacian(gray, cv2.CV_64F).var()
        dark_pixels = np.sum(gray < 50)
        dark_ratio = dark_pixels / (gray.shape[0] * gray.shape[1])
        brightness = np.mean(gray)
        contrast = np.std(gray.astype(np.float32))
        resolution = image.shape[:2][::-1]  # width, height
        
        # Thu thập cảnh báo
        warnings = []
        if blur_index < self.config["min_blur_index"]:
            warnings.append("Ảnh quá mờ")
        if dark_ratio > self.config["max_dark_ratio"]:
            warnings.append("Ảnh quá tối")
        if brightness < self.config["min_brightness"]:
            warnings.append("Độ sáng không đủ")
        if contrast < self.config["min_contrast"]:
            warnings.append("Độ tương phản không đủ")
        if resolution[0] < self.config["min_resolution"][0] or resolution[1] < self.config["min_resolution"][1]:
            warnings.append("Độ phân giải không đủ")
            
        # Tính điểm chất lượng tổng hợp
        quality_score = (
            (min(blur_index / self.config["min_blur_index"], 2.0) * 0.3) +
            ((1 - dark_ratio / self.config["max_dark_ratio"]) * 0.2) +
            (min(brightness / self.config["min_brightness"], 1.5) * 0.25) +
            (min(contrast / self.config["min_contrast"], 1.5) * 0.25)
        )
        quality_score = min(1.0, max(0.0, quality_score))
        
        return ImageQualityMetrics(
            blur_index=blur_index,
            dark_ratio=dark_ratio,
            brightness=brightness,
            contrast=contrast,
            resolution=resolution,
            quality_score=quality_score,
            warnings=warnings
        )
        
    def check_quality(self, image, prefix=None):
        """Kiểm tra chất lượng ảnh
        
        Args:
            image: Ảnh cần kiểm tra
            prefix: Tiền tố cho tên file debug
            
        Returns:
            tuple: (is_good, quality_info, enhanced_image)
        """
        # Kiểm tra ảnh có hợp lệ không
        if image is None or image.size == 0:
            logger.error("Ảnh không hợp lệ hoặc trống")
            return False, {"error": "invalid_image"}, None
            
        # Chuyển đổi sang ảnh xám nếu cần
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Kiểm tra độ phân giải
        height, width = image.shape[:2]
        resolution_ok = width >= self.config["min_resolution"][0] and height >= self.config["min_resolution"][1]
        
        # Tính chỉ số mờ (blur index) sử dụng Laplacian variance
        blur_index = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Tính tỷ lệ pixel tối (dark pixel ratio)
        dark_pixels = np.sum(gray < 50)
        dark_ratio = dark_pixels / (gray.shape[0] * gray.shape[1])
        
        # Tính độ sáng trung bình
        brightness = np.mean(gray)
        
        # Tính độ tương phản
        contrast = np.std(gray.astype(np.float32))
        
        # Vẽ histogram để debug chỉ khi debug mode được bật
        if self.debug and prefix:
            plt_available = True
            try:
                import matplotlib.pyplot as plt
            except ImportError:
                plt_available = False
                
            if plt_available:
                plt.figure(figsize=(10, 6))
                plt.hist(gray.ravel(), 256, [0, 256])
                plt.title(f'Histogram: Brightness={brightness:.2f}, Contrast={contrast:.2f}')
                plt.xlabel('Pixel Value')
                plt.ylabel('Frequency')
                hist_path = os.path.join(self.debug_dir, f"{prefix}_quality_histogram.jpg")
                plt.savefig(hist_path)
                plt.close()
                logger.info(f"Đã lưu biểu đồ histogram: {hist_path}")
        
        # Thu thập thông tin chất lượng
        quality_info = {
            "blur_index": blur_index,
            "dark_ratio": dark_ratio,
            "brightness": brightness,
            "contrast": contrast,
            "resolution": (width, height)
        }
        
        # Kiểm tra các tiêu chí chất lượng
        blur_ok = blur_index >= self.config["min_blur_index"]
        dark_ok = dark_ratio <= self.config["max_dark_ratio"]
        brightness_ok = brightness >= self.config["min_brightness"]
        contrast_ok = contrast >= self.config["min_contrast"]
        
        # Đánh giá tổng thể
        is_good = blur_ok and dark_ok and brightness_ok and contrast_ok and resolution_ok
        
        # Ghi log kết quả kiểm tra chỉ khi debug mode được bật
        if self.debug:
            logger.info(f"Kiểm tra chất lượng ảnh:")
            logger.info(f"  - Chỉ số mờ (blur index): {blur_index:.2f} (tối thiểu: {self.config['min_blur_index']})")
            logger.info(f"  - Tỷ lệ pixel tối: {dark_ratio:.4f} (tối đa: {self.config['max_dark_ratio']})")
            logger.info(f"  - Độ sáng trung bình: {brightness:.2f} (tối thiểu: {self.config['min_brightness']})")
            logger.info(f"  - Độ tương phản: {contrast:.2f} (tối thiểu: {self.config['min_contrast']})")
            logger.info(f"  - Độ phân giải: {width}x{height} (tối thiểu: {self.config['min_resolution'][0]}x{self.config['min_resolution'][1]})")
        
        if not is_good:
            if self.debug:
                logger.warning("Ảnh không đạt chất lượng yêu cầu!")
                if not blur_ok:
                    logger.warning("  - Ảnh quá mờ")
                if not dark_ok:
                    logger.warning("  - Ảnh quá tối")
                if not brightness_ok:
                    logger.warning("  - Độ sáng không đủ")
                if not contrast_ok:
                    logger.warning("  - Độ tương phản không đủ")
                if not resolution_ok:
                    logger.warning("  - Độ phân giải không đủ")
        
        # Nâng cao chất lượng ảnh nếu cần
        enhanced_image = self.enhance_image(image, quality_info, prefix)
        
        return is_good, quality_info, enhanced_image
        
    def enhance_image(self, image: np.ndarray, quality_info: Union[Dict, ImageQualityMetrics], prefix=None) -> np.ndarray:
        """Tăng cường chất lượng ảnh một cách nhẹ nhàng
        
        Args:
            image: Ảnh cần tăng cường
            quality_info: Thông tin chất lượng ảnh
            prefix: Tiền tố cho tên file debug
            
        Returns:
            np.ndarray: Ảnh đã tăng cường
        """
        # Chuyển đổi sang ảnh xám nếu cần
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Tăng độ tương phản
        enhanced = cv2.equalizeHist(gray)
        
        # Lưu ảnh debug nếu cần
        if self.debug and prefix:
            debug_path = os.path.join(self.debug_dir, f"{prefix}_enhanced.jpg")
            cv2.imwrite(debug_path, enhanced)
            logger.info(f"Đã lưu ảnh tăng cường: {debug_path}")
            
        return enhanced
        
    def enhance_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Tối ưu hóa ảnh cho OCR
        
        Args:
            image: Ảnh cần xử lý
            
        Returns:
            np.ndarray: Ảnh đã tối ưu
        """
        # Chuyển sang ảnh xám
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Áp dụng ngưỡng thích ứng
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        return binary
            
    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Xoay ảnh
        
        Args:
            image: Ảnh cần xoay
            angle: Góc xoay (độ)
            
        Returns:
            np.ndarray: Ảnh đã xoay
        """
        height, width = image.shape[:2]
        center = (width/2, height/2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
        return rotated
        
    def process_image(self, input_path: Union[str, np.ndarray], output_path: str = None, 
                     auto_rotate: bool = True, preserve_color: bool = True) -> ProcessingResult:
        """Xử lý ảnh
        
        Args:
            input_path: Đường dẫn đến file ảnh hoặc numpy array
            output_path: Đường dẫn lưu ảnh đầu ra
            auto_rotate: Có tự động xoay ảnh không
            preserve_color: Có giữ nguyên màu không
            
        Returns:
            ProcessingResult: Kết quả xử lý ảnh
        """
        try:
            # Đọc ảnh nếu là đường dẫn
            if isinstance(input_path, str):
                image = cv2.imread(input_path)
                if image is None:
                    return ProcessingResult(
                        success=False,
                        image=None,
                        quality_metrics=None,
                        processing_steps=[],
                        error_message=f"Không thể đọc file ảnh: {input_path}"
                    )
            else:
                image = input_path
                
            # Kiểm tra chất lượng
            quality_metrics = self._check_image_quality(image)
            
            # Log thông tin chất lượng nếu debug mode được bật
            if self.debug:
                logger.info(f"Kiểm tra chất lượng ảnh:")
                logger.info(f"  - Chỉ số mờ (blur index): {quality_metrics.blur_index:.2f} (tối thiểu: {self.config['min_blur_index']})")
                logger.info(f"  - Tỷ lệ pixel tối: {quality_metrics.dark_ratio:.4f} (tối đa: {self.config['max_dark_ratio']})")
                logger.info(f"  - Độ sáng trung bình: {quality_metrics.brightness:.2f} (tối thiểu: {self.config['min_brightness']})")
                logger.info(f"  - Độ tương phản: {quality_metrics.contrast:.2f} (tối thiểu: {self.config['min_contrast']})")
                logger.info(f"  - Độ phân giải: {quality_metrics.resolution[0]}x{quality_metrics.resolution[1]} (tối thiểu: {self.config['min_resolution'][0]}x{self.config['min_resolution'][1]})")
            
            # Xử lý ảnh
            enhanced = self.enhance_image(image, quality_metrics)
            
            # Phát hiện và sửa góc nghiêng nếu cần
            angle = 0
            if auto_rotate:
                angle = self.detect_skew(enhanced)
                if abs(angle) > self.config["min_skew_angle"]:
                    enhanced = self.rotate_image(enhanced, angle)
            
            # Quyết định có chuyển binary không
            if preserve_color:
                # Giữ nguyên ảnh màu đã tăng cường
                result = enhanced
                processing_steps = ["check_quality", "enhance_image"]
                if angle != 0:
                    processing_steps.append("rotate_image")
            else:
                # Tối ưu cho OCR (chuyển binary)
                result = self.enhance_image_for_ocr(enhanced)
                processing_steps = ["check_quality", "enhance_image"]
                if angle != 0:
                    processing_steps.append("rotate_image")
                processing_steps.append("enhance_for_ocr")
            
            # Lưu kết quả nếu có đường dẫn
            if output_path:
                cv2.imwrite(output_path, result)
                if self.debug:
                    logger.info(f"✅ Hoàn thành: {output_path}")
            else:
                if self.debug:
                    logger.info("✅ Hoàn thành xử lý ảnh")
            
            return ProcessingResult(
                success=True,
                image=result,
                quality_metrics=quality_metrics,
                processing_steps=processing_steps,
                output_path=output_path,
                rotation_angle=angle
            )
            
        except Exception as e:
            if self.debug:
                logger.error(f"❌ Lỗi khi xử lý ảnh: {str(e)}")
            return ProcessingResult(
                success=False,
                image=None,
                quality_metrics=None,
                processing_steps=[],
                error_message=str(e)
            )
            
    def detect_skew(self, image, prefix=None):
        """Phát hiện góc nghiêng của ảnh
        
        Args:
            image: Ảnh cần phát hiện góc nghiêng
            prefix: Tiền tố cho tên file debug
            
        Returns:
            float: Góc nghiêng (độ)
        """
        # Chuyển sang ảnh xám
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Phát hiện cạnh
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Phát hiện đường thẳng
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is not None:
            angles = []
            for rho, theta in lines[:, 0]:
                angle = theta * 180 / np.pi
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)
                    
            if angles:
                # Lấy góc trung bình
                angle = np.mean(angles)
                
                # Log kết quả nếu debug mode được bật
                if self.debug:
                    logger.info(f"Phát hiện góc nghiêng: {angle:.2f} độ")
                    
                    # Lưu ảnh debug
                    if prefix:
                        debug_path = os.path.join(self.debug_dir, f"{prefix}_skew_detection.jpg")
                        debug_img = image.copy()
                        for rho, theta in lines[:, 0]:
                            a = np.cos(theta)
                            b = np.sin(theta)
                            x0 = a * rho
                            y0 = b * rho
                            x1 = int(x0 + 1000*(-b))
                            y1 = int(y0 + 1000*(a))
                            x2 = int(x0 - 1000*(-b))
                            y2 = int(y0 - 1000*(a))
                            cv2.line(debug_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv2.imwrite(debug_path, debug_img)
                        logger.info(f"Đã lưu ảnh phát hiện góc nghiêng: {debug_path}")
                
                return angle
                
        return 0.0 