#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script test đơn giản để kiểm tra image-preprocess package
"""

import sys
import tempfile
import os
import cv2
import numpy as np

def create_test_image():
    """Tạo ảnh test đơn giản"""
    # Tạo ảnh trắng 800x600
    image = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Thêm text
    cv2.putText(image, "TEST IMAGE", (200, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    cv2.putText(image, "Line 1: Sample text", (50, 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(image, "Line 2: More content", (50, 300), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Thêm đường kẻ ngang
    cv2.line(image, (50, 150), (750, 150), (0, 0, 0), 2)
    cv2.line(image, (50, 250), (750, 250), (0, 0, 0), 2)
    cv2.line(image, (50, 350), (750, 350), (0, 0, 0), 2)
    
    return image

def test_package_import():
    """Test import package"""
    print("🔍 Test import package...")
    try:
        import image_preprocess
        print(f"✅ Import package thành công! Version: {image_preprocess.__version__}")
        
        # Test import các module con
        from image_preprocess import ImageProcessor, ImageQualityMetrics, ProcessingResult
        print("✅ Import các class chính thành công!")
        
        from image_preprocess.utils import validate_image_path, get_image_info, check_dependencies
        print("✅ Import utils thành công!")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi import: {e}")
        return False

def test_basic_functionality():
    """Test chức năng cơ bản"""
    print("\n🔍 Test chức năng cơ bản...")
    
    try:
        from image_preprocess import ImageProcessor
        from image_preprocess.utils import get_image_info
        
        # Tạo ảnh test
        with tempfile.TemporaryDirectory() as temp_dir:
            test_image = create_test_image()
            image_path = os.path.join(temp_dir, "test.jpg")
            cv2.imwrite(image_path, test_image)
            
            print(f"✅ Tạo ảnh test: {image_path}")
            
            # Test get_image_info
            info = get_image_info(image_path)
            print(f"✅ Thông tin ảnh: {info['width']}x{info['height']}, {info['file_size_mb']} MB")
            
            # Test ImageProcessor
            processor = ImageProcessor()
            print("✅ Khởi tạo ImageProcessor thành công!")
            
            # Test check quality
            is_good, quality_info, enhanced = processor.check_quality(test_image)
            print(f"✅ Kiểm tra chất lượng: {is_good}")
            print(f"   - Độ sáng: {quality_info['brightness']:.2f}")
            print(f"   - Độ tương phản: {quality_info['contrast']:.2f}")
            
            # Test xử lý ảnh (không auto rotate để nhanh hơn)
            output_path = os.path.join(temp_dir, "processed.jpg")
            result = processor.process_image(
                input_path=image_path,
                output_path=output_path,
                auto_rotate=False
            )
            
            if result.success:
                print("✅ Xử lý ảnh thành công!")
                print(f"   - Các bước: {', '.join(result.processing_steps)}")
                print(f"   - Điểm chất lượng: {result.quality_metrics.quality_score:.2f}")
            else:
                print(f"❌ Xử lý ảnh thất bại: {result.error_message}")
                return False
            
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test chức năng: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_functions():
    """Test các hàm API tiện ích"""
    print("\n🔍 Test API functions...")
    
    try:
        import image_preprocess
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_image = create_test_image()
            image_path = os.path.join(temp_dir, "test.jpg")
            cv2.imwrite(image_path, test_image)
            
            # Test hàm tiện ích
            is_good, quality_info, enhanced = image_preprocess.check_image_quality(image_path)
            print(f"✅ check_image_quality: {is_good}")
            
            # Test preprocess_for_ocr (không auto rotate)
            output_path = os.path.join(temp_dir, "processed.jpg")
            result = image_preprocess.preprocess_for_ocr(
                image_path, 
                output_path, 
                config={"skip_rotation": True}
            )
            
            if result.success:
                print("✅ preprocess_for_ocr thành công!")
            else:
                print(f"❌ preprocess_for_ocr thất bại: {result.error_message}")
                return False
            
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test API: {e}")
        return False

def test_dependencies():
    """Test dependencies"""
    print("\n🔍 Test dependencies...")
    
    try:
        from image_preprocess.utils import check_dependencies, get_missing_dependencies
        
        deps = check_dependencies()
        missing = get_missing_dependencies()
        
        print(f"✅ Kiểm tra dependencies:")
        for name, installed in deps.items():
            status = "✅" if installed else "❌"
            print(f"   {status} {name}")
        
        if missing:
            print(f"⚠️ Thiếu dependencies: {', '.join(missing)}")
        else:
            print("✅ Tất cả dependencies đã cài đặt!")
            
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test dependencies: {e}")
        return False

def main():
    """Hàm chính"""
    print("🎯 TEST IMAGE-PREPROCESS PACKAGE")
    print("=" * 50)
    
    tests = [
        ("Import Package", test_package_import),
        ("Basic Functionality", test_basic_functionality),
        ("API Functions", test_api_functions),
        ("Dependencies", test_dependencies),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 KẾT QUẢ TEST: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 Tất cả test đều PASSED!")
        return True
    else:
        print("⚠️ Một số test FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 