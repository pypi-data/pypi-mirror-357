import os
import glob
import cv2
import numpy as np
import configparser
from magicimg import (
    detect_skew, correct_skew,
    detect_orientation, rotate_image,
    enhance_image, enhance_image_for_ocr,
    process_image,
    check_tesseract_installed
)
from magicimg.core import ImageProcessor

def load_config():
    """Đọc cấu hình từ file config.ini"""
    config = configparser.ConfigParser()
    config_file = "config.ini"
    
    # Đọc file cấu hình nếu tồn tại
    if os.path.exists(config_file):
        config.read(config_file)
        
        # Lấy cấu hình Tesseract
        if "tesseract" in config:
            tesseract_path = config["tesseract"].get("path", "")
            if tesseract_path:
                os.environ["TESSERACT_PATH"] = tesseract_path
                
        # Lấy cấu hình debug
        if "debug" in config:
            global DEBUG
            DEBUG = config["debug"].getboolean("enabled", False)
            
    return config

# Cấu hình debug
DEBUG = False

def debug_print(*args, **kwargs):
    """In thông tin debug nếu DEBUG=True"""
    if DEBUG:
        print(*args, **kwargs)

def check_environment():
    """Kiểm tra môi trường chạy test"""
    try:
        # Thử các đường dẫn Tesseract phổ biến
        possible_paths = [
            os.getenv("TESSERACT_PATH"),
            r"C:\Program Files\Tesseract-OCR",
            r"C:\Program Files (x86)\Tesseract-OCR",
            r"D:\Program Files\Tesseract-OCR",
            "/usr/bin",
            "/usr/local/bin"
        ]
        
        tesseract_found = False
        for path in possible_paths:
            if path and os.path.exists(path):
                # Kiểm tra file tesseract.exe hoặc tesseract
                exe_name = "tesseract.exe" if os.name == "nt" else "tesseract"
                tesseract_exe = os.path.join(path, exe_name)
                
                if os.path.exists(tesseract_exe):
                    # Thêm vào PATH và thiết lập TESSERACT_PATH
                    os.environ["TESSERACT_PATH"] = path
                    if os.name == "nt":  # Windows
                        current_path = os.environ.get("PATH", "")
                        if path not in current_path:
                            os.environ["PATH"] = f"{path};{current_path}"
                    else:  # Linux/Mac
                        current_path = os.environ.get("PATH", "")
                        if path not in current_path:
                            os.environ["PATH"] = f"{path}:{current_path}"
                    
                    tesseract_found = True
                    debug_print(f"Found Tesseract at: {path}")
                    break
        
        if not tesseract_found:
            print("Error: Tesseract not found in any standard locations")
            print("Please install Tesseract and set TESSERACT_PATH environment variable")
            return False
            
        # Kiểm tra thư viện tesseract
        if not check_tesseract_installed():
            print("Error: Tesseract not properly installed or configured")
            print("Please ensure Tesseract is installed correctly and tessdata directory exists")
            return False
            
        debug_print("Environment check passed")
        debug_print(f"Using Tesseract from: {os.environ['TESSERACT_PATH']}")
        return True
        
    except Exception as e:
        print(f"Error checking environment: {str(e)}")
        return False

def test_skew_correction(image_path, output_dir):
    """Test 1: Phát hiện và sửa góc nghiêng"""
    try:
        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}_test1_skew.png")
        
        # Tạo ImageProcessor với debug_dir nếu cần
        debug_dir = output_dir if DEBUG else None
        processor = ImageProcessor(debug_dir=debug_dir)
        
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Không thể đọc ảnh: {image_path}")
            
        # Phát hiện và sửa góc nghiêng
        skew_angle = processor.detect_skew(image)
        result = processor.correct_skew(image, skew_angle)
        
        # Lưu kết quả
        cv2.imwrite(output_path, result)
        
        debug_print(f"Test 1 - Skew angle: {skew_angle:.2f}°")
        return True, output_path
    except Exception as e:
        return False, str(e)

def test_orientation_correction(image_path, output_dir):
    """Test 2: Phát hiện và sửa hướng"""
    try:
        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}_test2_orientation.png")
        
        # Tạo ImageProcessor với debug_dir nếu cần
        debug_dir = output_dir if DEBUG else None
        processor = ImageProcessor(debug_dir=debug_dir)
        
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Không thể đọc ảnh: {image_path}")
            
        # Phát hiện và sửa hướng
        orientation = processor.detect_orientation(image)
        result = processor.rotate_image(image, orientation)
        
        # Lưu kết quả
        cv2.imwrite(output_path, result)
        
        debug_print(f"Test 2 - Orientation angle: {orientation}°")
        return True, output_path
    except Exception as e:
        return False, str(e)

def test_image_enhancement(image_path, output_dir):
    """Test 3: Tăng cường chất lượng ảnh"""
    try:
        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}_test3_enhanced.png")
        
        # Tạo ImageProcessor với debug_dir nếu cần
        debug_dir = output_dir if DEBUG else None
        processor = ImageProcessor(debug_dir=debug_dir)
        
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Không thể đọc ảnh: {image_path}")
            
        # Kiểm tra chất lượng và tăng cường
        quality_info = processor._check_image_quality(image)
        result = processor.enhance_image(image, quality_info)
        
        # Lưu kết quả
        cv2.imwrite(output_path, result)
        
        debug_print("Test 3 - Image enhanced")
        return True, output_path
    except Exception as e:
        return False, str(e)

def test_ocr_enhancement(image_path, output_dir):
    """Test 4: Tối ưu hóa cho OCR"""
    try:
        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}_test4_ocr.png")
        
        # Tạo ImageProcessor với debug_dir nếu cần
        debug_dir = output_dir if DEBUG else None
        processor = ImageProcessor(debug_dir=debug_dir)
        
        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Không thể đọc ảnh: {image_path}")
            
        # Tối ưu cho OCR
        result = processor.enhance_image_for_ocr(image)
        
        # Lưu kết quả
        cv2.imwrite(output_path, result)
        
        debug_print("Test 4 - OCR optimization completed")
        return True, output_path
    except Exception as e:
        return False, str(e)

def test_full_processing(image_path, output_dir):
    """Test 5: Xử lý đầy đủ"""
    try:
        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}_test5_full.png")
        
        # Tạo ImageProcessor với debug_dir và cấu hình nếu cần
        debug_dir = output_dir if DEBUG else None
        config = {
            "skip_rotation": False,
            "min_quality_score": 0.5  # Giảm ngưỡng chất lượng cho test
        }
        processor = ImageProcessor(debug_dir=debug_dir, config=config)
        
        # Xử lý đầy đủ
        result = processor.process_image(image_path, output_path)
        
        if not result.success:
            raise ValueError(result.error_message)
            
        debug_print("Test 5 - Full processing completed")
        return True, output_path
    except Exception as e:
        return False, str(e)

def run_all_tests():
    """Chạy tất cả các test case"""
    # Kiểm tra môi trường
    if not check_environment():
        print("Environment check failed. Please fix the issues above.")
        return

    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Lấy danh sách ảnh đầu vào
    image_files = glob.glob(os.path.join(input_dir, "*.*"))
    
    # Thống kê kết quả
    total_files = len(image_files)
    successful_files = 0
    failed_files = 0
    
    for image_path in image_files:
        base_name = os.path.basename(image_path)
        debug_print(f"\nProcessing {base_name}...")
        
        # Chạy các test case
        test_results = [
            ("Skew correction", test_skew_correction(image_path, output_dir)),
            ("Orientation correction", test_orientation_correction(image_path, output_dir)),
            ("Image enhancement", test_image_enhancement(image_path, output_dir)),
            ("OCR optimization", test_ocr_enhancement(image_path, output_dir)),
            ("Full processing", test_full_processing(image_path, output_dir))
        ]
        
        # Kiểm tra kết quả
        has_error = False
        for test_name, (success, result) in test_results:
            if not success:
                has_error = True
                print(f"Error in {base_name} - {test_name}: {result}")
        
        if has_error:
            failed_files += 1
        else:
            successful_files += 1
            debug_print(f"All tests completed for {base_name}")
            if DEBUG:
                print("Output files:")
                for test_name, (_, output_path) in test_results:
                    if isinstance(output_path, str) and os.path.exists(output_path):
                        print(f"- {os.path.basename(output_path)}")
    
    # In thống kê cuối cùng
    print(f"\nTest Summary:")
    print(f"Total files processed: {total_files}")
    print(f"Successful: {successful_files}")
    print(f"Failed: {failed_files}")

if __name__ == "__main__":
    # Đọc cấu hình
    config = load_config()
    
    # Có thể ghi đè cấu hình bằng biến môi trường
    DEBUG = os.getenv('DEBUG', '').lower() in ('true', '1', 'yes') or DEBUG
    
    run_all_tests() 