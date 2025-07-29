"""
Các hàm tiện ích cho package image-preprocess
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from typing import Optional, Union, List, Tuple, Any
import numpy as np
import cv2
from .core import ImageProcessor, ImageQualityMetrics, ProcessingResult

logger = logging.getLogger(__name__)

def check_tesseract_installed() -> bool:
    """
    Kiểm tra xem Tesseract OCR có được cài đặt hay không
    
    Returns:
        bool: True nếu Tesseract được cài đặt, False nếu không
    """
    try:
        import pytesseract
        # Thử gọi pytesseract để kiểm tra
        pytesseract.get_tesseract_version()
        return True
    except ImportError:
        logger.warning("pytesseract không được cài đặt. Cài đặt bằng: pip install pytesseract")
        return False
    except Exception as e:
        logger.warning(f"Tesseract không khả dụng: {str(e)}")
        return False

def validate_image_path(image_path: Union[str, Path]) -> bool:
    """
    Kiểm tra đường dẫn ảnh có hợp lệ hay không
    
    Args:
        image_path: Đường dẫn đến file ảnh
        
    Returns:
        bool: True nếu đường dẫn hợp lệ, False nếu không
    """
    if not image_path:
        logger.error("Đường dẫn ảnh không được để trống")
        return False
    
    path = Path(image_path)
    
    if not path.exists():
        logger.error(f"File không tồn tại: {image_path}")
        return False
    
    if not path.is_file():
        logger.error(f"Đường dẫn không phải file: {image_path}")
        return False
    
    # Kiểm tra phần mở rộng file
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    if path.suffix.lower() not in valid_extensions:
        logger.error(f"Định dạng file không được hỗ trợ: {path.suffix}")
        return False
    
    return True

def create_debug_dir(base_dir: Union[str, Path], name: str = "debug") -> str:
    """
    Tạo thư mục debug
    
    Args:
        base_dir: Thư mục gốc
        name: Tên thư mục debug
        
    Returns:
        str: Đường dẫn đến thư mục debug
    """
    debug_dir = Path(base_dir) / name
    debug_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Đã tạo thư mục debug: {debug_dir}")
    return str(debug_dir)

def get_image_info(image_path: Union[str, Path]) -> dict:
    """
    Lấy thông tin cơ bản về ảnh
    
    Args:
        image_path: Đường dẫn đến file ảnh
        
    Returns:
        dict: Thông tin về ảnh
    """
    if not validate_image_path(image_path):
        return {}
    
    try:
        # Đọc ảnh
        image = cv2.imread(str(image_path))
        if image is None:
            return {"error": "Không thể đọc ảnh"}
        
        # Lấy thông tin cơ bản
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        # Lấy thông tin file
        file_path = Path(image_path)
        file_size = file_path.stat().st_size
        
        return {
            "file_path": str(file_path.absolute()),
            "file_name": file_path.name,
            "file_size": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "width": width,
            "height": height,
            "channels": channels,
            "total_pixels": width * height,
            "aspect_ratio": round(width / height, 2) if height > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Lỗi khi lấy thông tin ảnh: {str(e)}")
        return {"error": str(e)}

def clean_debug_dir(debug_dir: Union[str, Path], keep_latest: int = 5) -> None:
    """
    Dọn dẹp thư mục debug, chỉ giữ lại những file mới nhất
    
    Args:
        debug_dir: Thư mục debug
        keep_latest: Số lượng file mới nhất cần giữ lại
    """
    debug_path = Path(debug_dir)
    
    if not debug_path.exists():
        return
    
    try:
        # Lấy danh sách tất cả file
        files = list(debug_path.glob("*"))
        files = [f for f in files if f.is_file()]
        
        if len(files) <= keep_latest:
            return
        
        # Sắp xếp theo thời gian sửa đổi
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Xóa các file cũ
        files_to_delete = files[keep_latest:]
        deleted_count = 0
        
        for file in files_to_delete:
            try:
                file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Không thể xóa file {file}: {str(e)}")
        
        if deleted_count > 0:
            logger.info(f"Đã xóa {deleted_count} file cũ trong thư mục debug")
            
    except Exception as e:
        logger.error(f"Lỗi khi dọn dẹp thư mục debug: {str(e)}")

def check_dependencies() -> dict:
    """
    Kiểm tra các dependency có được cài đặt hay không
    
    Returns:
        dict: Trạng thái các dependency
    """
    dependencies = {
        "opencv-python": False,
        "numpy": False,
        "matplotlib": False,
        "pytesseract": False,
        "Pillow": False
    }
    
    # Kiểm tra OpenCV
    try:
        import cv2
        dependencies["opencv-python"] = True
    except ImportError:
        pass
    
    # Kiểm tra NumPy
    try:
        import numpy
        dependencies["numpy"] = True
    except ImportError:
        pass
    
    # Kiểm tra Matplotlib
    try:
        import matplotlib
        dependencies["matplotlib"] = True
    except ImportError:
        pass
    
    # Kiểm tra pytesseract
    try:
        import pytesseract
        dependencies["pytesseract"] = True
    except ImportError:
        pass
    
    # Kiểm tra Pillow
    try:
        from PIL import Image
        dependencies["Pillow"] = True
    except ImportError:
        pass
    
    return dependencies

def get_missing_dependencies() -> List[str]:
    """
    Lấy danh sách các dependency bị thiếu
    
    Returns:
        List[str]: Danh sách các package bị thiếu
    """
    deps = check_dependencies()
    missing = [name for name, installed in deps.items() if not installed]
    return missing

def print_system_info():
    """In thông tin hệ thống và trạng thái các dependency"""
    print("=== THÔNG TIN HỆ THỐNG ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    print("\n=== TRẠNG THÁI DEPENDENCIES ===")
    deps = check_dependencies()
    for name, installed in deps.items():
        print(f"{name}: {'✓ Đã cài đặt' if installed else '✗ Chưa cài đặt'}")
    
    missing = get_missing_dependencies()
    if missing:
        print("\n⚠️ Một số dependency chưa được cài đặt:")
        for dep in missing:
            print(f"  - {dep}")
    else:
        print("\n✓ Tất cả dependencies đã được cài đặt!")

def create_sample_config() -> dict:
    """
    Tạo cấu hình mẫu cho ImageProcessor
    
    Returns:
        dict: Cấu hình mẫu
    """
    return {
        # Ngưỡng chất lượng
        "min_blur_index": 80.0,
        "max_dark_ratio": 0.2,
        "min_brightness": 180.0,
        "min_contrast": 50.0,
        "min_resolution": (1000, 1400),
        "min_quality_score": 0.7,
        
        # Ngưỡng xử lý
        "min_skew_angle": 0.3,
        "max_skew_angle": 30.0,
        "min_rotation_confidence": 0.8,
        
        # Cấu hình xử lý
        "skip_rotation": False,
        "reuse_rotation": None,
        
        # Từ khóa tìm kiếm
        "ballot_keywords": [
            "phieu bau cu", "doan dai bieu", "dai hoi", "dang bo",
            "nhiem ky", "stt", "ho va ten", "ha noi", "ngay", "thang", "nam"
        ],

        # Tham số phát hiện đường kẻ ngang
        "line_detection": {
            "min_line_length_ratio": 0.6,
            "min_length_threshold_ratio": 0.7,
            "max_line_height": 3,
            "morph_iterations": 1,
            "histogram_threshold_ratio": 0.5,
            "min_line_distance": 20,
            "dilate_kernel_div": 30,
            "horizontal_kernel_div": 5,
            "projection_threshold_div": 4
        },

        # Tham số cắt hàng
        "row_extraction": {
            "top_margin": 8,
            "bottom_margin": 8,
            "safe_zone": 5,
            "min_row_height": 20,
            "check_text": True,
            "text_margin": 3,
            "min_text_area": 0.003
        }
    }

def detect_skew_array(image: np.ndarray, **kwargs) -> float:
    """
    Phát hiện góc nghiêng của ảnh từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        float: Góc nghiêng (độ)
    """
    processor = ImageProcessor(**kwargs)
    return processor.detect_skew(image)

def correct_skew_array(
    image: np.ndarray, 
    angle: Optional[float] = None,
    **kwargs
) -> np.ndarray:
    """
    Chỉnh sửa góc nghiêng của ảnh từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        angle (float, optional): Góc nghiêng cần sửa. Nếu None sẽ tự động phát hiện
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        np.ndarray: Ảnh đã sửa góc nghiêng
    """
    processor = ImageProcessor(**kwargs)
    
    if angle is None:
        angle = processor.detect_skew(image)
    
    return processor.correct_skew(image, angle)

def check_quality_array(image: np.ndarray, **kwargs) -> Tuple[bool, ImageQualityMetrics, Optional[np.ndarray]]:
    """
    Kiểm tra chất lượng ảnh từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        Tuple[bool, ImageQualityMetrics, Optional[np.ndarray]]: 
            - is_good: Ảnh có đạt chất lượng không
            - quality_info: Thông tin chất lượng
            - enhanced_image: Ảnh đã tăng cường (nếu cần)
    """
    processor = ImageProcessor(**kwargs)
    return processor.check_quality(image)

def detect_orientation_array(image: np.ndarray, **kwargs) -> int:
    """
    Phát hiện hướng của ảnh từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        int: Góc xoay cần điều chỉnh (0, 90, 180, 270)
    """
    processor = ImageProcessor(**kwargs)
    return processor.detect_orientation(image)

def enhance_image_array(image: np.ndarray, **kwargs) -> np.ndarray:
    """
    Tăng cường chất lượng ảnh từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        np.ndarray: Ảnh đã tăng cường chất lượng
    """
    processor = ImageProcessor(**kwargs)
    _, quality_info, enhanced = processor.check_quality(image)
    return enhanced if enhanced is not None else image

def enhance_image_for_ocr_array(image: np.ndarray, **kwargs) -> np.ndarray:
    """
    Tăng cường ảnh đặc biệt cho OCR từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        np.ndarray: Ảnh đã tăng cường cho OCR
    """
    processor = ImageProcessor(**kwargs)
    return processor.enhance_image_for_ocr(image)

def rotate_image_array(image: np.ndarray, angle: int, **kwargs) -> np.ndarray:
    """
    Xoay ảnh theo góc cho trước từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        angle (int): Góc xoay (0, 90, 180, 270)
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        np.ndarray: Ảnh đã xoay
    """
    processor = ImageProcessor(**kwargs)
    return processor.rotate_image(image, angle)

def process_image_array(
    image: np.ndarray, 
    auto_rotate: bool = True,
    **kwargs
) -> ProcessingResult:
    """
    Xử lý ảnh với các bước tối ưu từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        auto_rotate (bool): Có tự động xoay ảnh hay không
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        ProcessingResult: Kết quả xử lý ảnh
    """
    processor = ImageProcessor(**kwargs)
    return processor.process_image_array(image, auto_rotate=auto_rotate)

def detect_horizontal_lines_array(image: np.ndarray, **kwargs) -> List[int]:
    """
    Phát hiện các đường kẻ ngang trong ảnh từ numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        List[int]: Danh sách các tọa độ y của đường kẻ ngang
    """
    processor = ImageProcessor(**kwargs)
    processed = processor.preprocess_image(image)
    return processor.detect_horizontal_lines(processed)

def extract_rows_from_table_array(
    image: np.ndarray,
    table_id: int = 1,
    **kwargs
) -> List[np.ndarray]:
    """
    Cắt các hàng từ ảnh bảng dạng numpy array
    
    Args:
        image (np.ndarray): Ảnh đầu vào dạng numpy array
        table_id (int): ID của bảng
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        List[np.ndarray]: Danh sách các ảnh hàng đã cắt
    """
    processor = ImageProcessor(**kwargs)
    return processor.extract_rows_from_table(image, table_id)

def process_skew(
    image: Union[str, np.ndarray, Path],
    output_path: Optional[str] = None,
    return_type: str = "auto",
    **kwargs
) -> Union[np.ndarray, str, Tuple[float, Union[np.ndarray, str]]]:
    """
    Phát hiện và sửa nghiêng cho ảnh. Hỗ trợ cả đường dẫn file và numpy array.
    
    Args:
        image: Đường dẫn ảnh (str/Path) hoặc numpy array
        output_path: Đường dẫn lưu ảnh kết quả (tùy chọn)
        return_type: Kiểu dữ liệu trả về ("numpy", "path", "auto", "both")
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        - Nếu return_type="numpy": numpy array đã sửa nghiêng
        - Nếu return_type="path": đường dẫn file đã sửa nghiêng
        - Nếu return_type="auto": tự động theo kiểu đầu vào
        - Nếu return_type="both": (góc nghiêng, kết quả)
    """
    processor = ImageProcessor(**kwargs)
    
    # Đọc ảnh đầu vào
    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image))
        input_is_path = True
    else:
        img = image.copy()
        input_is_path = False
        
    if img is None:
        raise ValueError("Không thể đọc ảnh đầu vào")
    
    # Phát hiện và sửa nghiêng
    skew_angle = processor.detect_skew(img)
    if abs(skew_angle) >= processor.config["min_skew_angle"]:
        img = processor.correct_skew(img, skew_angle)
    
    # Xử lý đầu ra
    if return_type == "both":
        if output_path:
            cv2.imwrite(output_path, img)
            return skew_angle, output_path
        return skew_angle, img
        
    if output_path:
        cv2.imwrite(output_path, img)
        if return_type == "path" or (return_type == "auto" and input_is_path):
            return output_path
            
    if return_type == "numpy" or (return_type == "auto" and not input_is_path):
        return img
        
    return output_path if output_path else img

def process_orientation(
    image: Union[str, np.ndarray, Path],
    output_path: Optional[str] = None,
    return_type: str = "auto",
    **kwargs
) -> Union[np.ndarray, str, Tuple[float, Union[np.ndarray, str]]]:
    """
    Phát hiện và xoay hướng cho ảnh. Hỗ trợ cả đường dẫn file và numpy array.
    
    Args:
        image: Đường dẫn ảnh (str/Path) hoặc numpy array
        output_path: Đường dẫn lưu ảnh kết quả (tùy chọn)
        return_type: Kiểu dữ liệu trả về ("numpy", "path", "auto", "both")
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        - Nếu return_type="numpy": numpy array đã xoay hướng
        - Nếu return_type="path": đường dẫn file đã xoay hướng
        - Nếu return_type="auto": tự động theo kiểu đầu vào
        - Nếu return_type="both": (góc xoay, kết quả)
    """
    processor = ImageProcessor(**kwargs)
    
    # Đọc ảnh đầu vào
    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image))
        input_is_path = True
    else:
        img = image.copy()
        input_is_path = False
        
    if img is None:
        raise ValueError("Không thể đọc ảnh đầu vào")
    
    # Phát hiện và xoay hướng
    orientation_angle = processor.detect_orientation(img)
    if orientation_angle != 0:
        img = processor.rotate_image(img, orientation_angle)
    
    # Xử lý đầu ra
    if return_type == "both":
        if output_path:
            cv2.imwrite(output_path, img)
            return orientation_angle, output_path
        return orientation_angle, img
        
    if output_path:
        cv2.imwrite(output_path, img)
        if return_type == "path" or (return_type == "auto" and input_is_path):
            return output_path
            
    if return_type == "numpy" or (return_type == "auto" and not input_is_path):
        return img
        
    return output_path if output_path else img

def process_image_full(
    image: Union[str, np.ndarray, Path],
    output_path: Optional[str] = None,
    return_type: str = "auto",
    auto_rotate: bool = True,
    **kwargs
) -> Union[np.ndarray, str, ProcessingResult]:
    """
    Xử lý đầy đủ cho ảnh (nghiêng, hướng, chất lượng). Hỗ trợ cả đường dẫn file và numpy array.
    
    Args:
        image: Đường dẫn ảnh (str/Path) hoặc numpy array
        output_path: Đường dẫn lưu ảnh kết quả (tùy chọn)
        return_type: Kiểu dữ liệu trả về ("numpy", "path", "auto", "result")
        auto_rotate: Có tự động xoay hướng không
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        - Nếu return_type="numpy": numpy array đã xử lý
        - Nếu return_type="path": đường dẫn file đã xử lý
        - Nếu return_type="auto": tự động theo kiểu đầu vào
        - Nếu return_type="result": ProcessingResult object
    """
    processor = ImageProcessor(**kwargs)
    
    # Đọc ảnh đầu vào
    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image))
        input_is_path = True
    else:
        img = image.copy()
        input_is_path = False
        
    if img is None:
        raise ValueError("Không thể đọc ảnh đầu vào")
    
    # Xử lý ảnh
    result = processor.process_image_array(img, auto_rotate=auto_rotate)
    
    # Xử lý đầu ra
    if return_type == "result":
        if output_path:
            cv2.imwrite(output_path, result.image)
            result.output_path = output_path
        return result
        
    if output_path:
        cv2.imwrite(output_path, result.image)
        if return_type == "path" or (return_type == "auto" and input_is_path):
            return output_path
            
    if return_type == "numpy" or (return_type == "auto" and not input_is_path):
        return result.image
        
    return output_path if output_path else result.image 

def _process_flexible(
    func_name: str,
    image: Union[str, np.ndarray, Path],
    output_path: Optional[str] = None,
    return_type: str = "auto",
    **kwargs
) -> Union[np.ndarray, str, Tuple[Any, Union[np.ndarray, str]], ProcessingResult]:
    """
    Template cho các hàm xử lý ảnh linh hoạt.
    
    Args:
        func_name: Tên hàm xử lý trong ImageProcessor
        image: Đường dẫn ảnh (str/Path) hoặc numpy array
        output_path: Đường dẫn lưu ảnh kết quả (tùy chọn)
        return_type: Kiểu dữ liệu trả về ("numpy", "path", "auto", "both", "result")
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        - Nếu return_type="numpy": numpy array đã xử lý
        - Nếu return_type="path": đường dẫn file đã xử lý
        - Nếu return_type="auto": tự động theo kiểu đầu vào
        - Nếu return_type="both": (kết quả phụ, kết quả chính)
        - Nếu return_type="result": ProcessingResult object
    """
    processor = ImageProcessor(**kwargs)
    
    # Đọc ảnh đầu vào
    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image))
        input_is_path = True
    else:
        img = image.copy()
        input_is_path = False
        
    if img is None:
        raise ValueError("Không thể đọc ảnh đầu vào")
    
    # Gọi hàm xử lý tương ứng
    func = getattr(processor, func_name)
    result = func(img)
    
    # Xử lý kết quả tùy theo kiểu hàm
    if isinstance(result, tuple):
        sub_result, main_result = result
    elif isinstance(result, ProcessingResult):
        if return_type == "result":
            if output_path:
                cv2.imwrite(output_path, result.image)
                result.output_path = output_path
            return result
        main_result = result.image
        sub_result = result
    else:
        main_result = result
        sub_result = None
    
    # Xử lý đầu ra
    if return_type == "both" and sub_result is not None:
        if output_path:
            cv2.imwrite(output_path, main_result)
            return sub_result, output_path
        return sub_result, main_result
        
    if output_path:
        cv2.imwrite(output_path, main_result)
        if return_type == "path" or (return_type == "auto" and input_is_path):
            return output_path
            
    if return_type == "numpy" or (return_type == "auto" and not input_is_path):
        return main_result
        
    return output_path if output_path else main_result

def process_flexible(
    func_name: str,
    image: Union[str, np.ndarray, Path],
    output_path: Optional[str] = None,
    return_type: str = "auto",
    **kwargs
) -> Union[np.ndarray, str, Tuple[Any, Union[np.ndarray, str]], ProcessingResult]:
    """
    Hàm xử lý ảnh linh hoạt, hỗ trợ tất cả các API.
    
    Args:
        func_name: Tên hàm xử lý ("detect_skew", "correct_skew", "detect_orientation", ...)
        image: Đường dẫn ảnh (str/Path) hoặc numpy array
        output_path: Đường dẫn lưu ảnh kết quả (tùy chọn)
        return_type: Kiểu dữ liệu trả về ("numpy", "path", "auto", "both", "result")
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        - Nếu return_type="numpy": numpy array đã xử lý
        - Nếu return_type="path": đường dẫn file đã xử lý
        - Nếu return_type="auto": tự động theo kiểu đầu vào
        - Nếu return_type="both": (kết quả phụ, kết quả chính)
        - Nếu return_type="result": ProcessingResult object
        
    Examples:
        >>> # Phát hiện nghiêng
        >>> angle = process_flexible("detect_skew", "input.jpg", return_type="numpy")
        >>> 
        >>> # Sửa nghiêng
        >>> result = process_flexible("correct_skew", image_array, angle=30)
        >>> 
        >>> # Phát hiện hướng
        >>> angle = process_flexible("detect_orientation", "input.jpg")
        >>> 
        >>> # Xử lý đầy đủ
        >>> result = process_flexible("process_image", "input.jpg", return_type="result")
    """
    return _process_flexible(func_name, image, output_path, return_type, **kwargs)

# Định nghĩa các hàm wrapper cụ thể
def detect_skew_flexible(
    image: Union[str, np.ndarray, Path],
    output_path: Optional[str] = None,
    return_type: str = "auto",
    **kwargs
) -> Union[float, np.ndarray, str, Tuple[float, Union[np.ndarray, str]]]:
    """
    Phát hiện góc nghiêng của ảnh. Hỗ trợ cả đường dẫn file và numpy array.
    
    Args:
        image: Đường dẫn ảnh (str/Path) hoặc numpy array
        output_path: Đường dẫn lưu ảnh debug (tùy chọn)
        return_type: Kiểu dữ liệu trả về ("numpy", "path", "auto", "both")
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        - Mặc định: góc nghiêng (float)
        - Nếu return_type="both": (góc nghiêng, ảnh debug)
    """
    return process_flexible("detect_skew", image, output_path, return_type, **kwargs)

def correct_skew_flexible(
    image: Union[str, np.ndarray, Path],
    angle: Optional[float] = None,
    output_path: Optional[str] = None,
    return_type: str = "auto",
    **kwargs
) -> Union[np.ndarray, str]:
    """
    Sửa góc nghiêng của ảnh. Hỗ trợ cả đường dẫn file và numpy array.
    
    Args:
        image: Đường dẫn ảnh (str/Path) hoặc numpy array
        angle: Góc nghiêng cần sửa (nếu None sẽ tự động phát hiện)
        output_path: Đường dẫn lưu ảnh kết quả (tùy chọn)
        return_type: Kiểu dữ liệu trả về ("numpy", "path", "auto")
        **kwargs: Các tham số tùy chỉnh
        
    Returns:
        - Nếu return_type="numpy": numpy array đã sửa nghiêng
        - Nếu return_type="path": đường dẫn file đã sửa nghiêng
        - Nếu return_type="auto": tự động theo kiểu đầu vào
    """
    if angle is not None:
        kwargs['angle'] = angle
    return process_flexible("correct_skew", image, output_path, return_type, **kwargs)

# ... Tương tự cho các API khác ... 