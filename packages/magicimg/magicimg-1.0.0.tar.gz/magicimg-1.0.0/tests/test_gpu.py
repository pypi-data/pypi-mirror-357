import pytest
import cv2
import numpy as np
import torch
from magicimg.core import ImageProcessor

def test_gpu_initialization():
    """Test khởi tạo GPU"""
    # Test với GPU
    processor = ImageProcessor(
        config={
            "use_gpu": True,
            "gpu_id": 0
        }
    )
    if torch.cuda.is_available():
        assert processor.has_gpu
        assert processor.gpu_info is not None
        assert "name" in processor.gpu_info
        assert "total_memory" in processor.gpu_info
    else:
        assert not processor.has_gpu
        assert processor.gpu_info is None
        
    # Test với CPU
    processor = ImageProcessor(
        config={
            "use_gpu": False
        }
    )
    assert not processor.has_gpu
    assert processor.gpu_info is None

def test_gpu_memory_management():
    """Test quản lý bộ nhớ GPU"""
    if not torch.cuda.is_available():
        pytest.skip("Không có GPU")
        
    processor = ImageProcessor(
        config={
            "use_gpu": True,
            "gpu_id": 0,
            "gpu_memory_limit": 0.5
        }
    )
    
    # Tạo ảnh test lớn
    image = np.random.randint(0, 255, (4096, 4096, 3), dtype=np.uint8)
    
    # Kiểm tra bộ nhớ trước
    before = torch.cuda.memory_allocated()
    
    # Xử lý ảnh
    result = processor.process_image(image)
    
    # Kiểm tra bộ nhớ sau
    after = torch.cuda.memory_allocated()
    
    # Bộ nhớ phải được giải phóng
    assert after <= before

def test_batch_processing():
    """Test xử lý batch"""
    processor = ImageProcessor(
        config={
            "use_gpu": True,
            "batch_size": 4
        }
    )
    
    # Tạo batch test
    images = [
        np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        for _ in range(4)
    ]
    
    # Hàm xử lý đơn giản
    def process_fn(batch):
        return batch * 2
        
    # Xử lý batch
    results = processor._process_batch(images, process_fn)
    
    # Kiểm tra kết quả
    assert len(results) == len(images)
    for img, res in zip(images, results):
        np.testing.assert_array_almost_equal(res, img * 2)

def test_gpu_error_handling():
    """Test xử lý lỗi GPU"""
    # Test với GPU ID không tồn tại
    processor = ImageProcessor(
        config={
            "use_gpu": True,
            "gpu_id": 999  # ID không tồn tại
        }
    )
    assert not processor.has_gpu
    
    # Test với memory limit không hợp lệ
    processor = ImageProcessor(
        config={
            "use_gpu": True,
            "gpu_memory_limit": 2.0  # Giá trị > 1
        }
    )
    if processor.has_gpu:
        assert processor.config["gpu_memory_limit"] <= 1.0

def test_gpu_optimization():
    """Test tối ưu GPU"""
    if not torch.cuda.is_available():
        pytest.skip("Không có GPU")
        
    processor = ImageProcessor(
        config={
            "use_gpu": True,
            "optimize_for_gpu": True
        }
    )
    
    # Tạo ảnh test
    image = np.random.randint(0, 255, (1024, 1024, 3), dtype=np.uint8)
    
    # Đo thời gian xử lý
    import time
    start = time.time()
    result = processor.process_image(image)
    gpu_time = time.time() - start
    
    # Test với CPU
    processor.has_gpu = False
    start = time.time()
    result = processor.process_image(image)
    cpu_time = time.time() - start
    
    # GPU phải nhanh hơn
    assert gpu_time < cpu_time

if __name__ == "__main__":
    pytest.main([__file__]) 