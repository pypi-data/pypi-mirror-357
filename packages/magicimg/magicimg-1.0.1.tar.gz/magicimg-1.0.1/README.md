# MagicImg - Thư viện xử lý ảnh thông minh

MagicImg là một thư viện Python mạnh mẽ cho việc xử lý và tối ưu hóa ảnh, đặc biệt là cho các tác vụ OCR. Thư viện hỗ trợ xử lý trên cả CPU và GPU, với khả năng tự động phát hiện và tối ưu hóa tài nguyên.

## Tính năng chính

- Tự động phát hiện và sử dụng GPU nếu có
- Quản lý bộ nhớ GPU thông minh
- Xử lý batch ảnh hiệu quả
- Tăng cường chất lượng ảnh tự động
- Phát hiện và sửa góc nghiêng
- Tối ưu hóa ảnh cho OCR
- Debug và logging chi tiết

## Yêu cầu hệ thống

- Python 3.7+
- CUDA (tùy chọn, cho xử lý GPU)
- OpenCV
- PyTorch
- Tesseract (cho OCR)

## Cài đặt

```bash
pip install -r requirements.txt
```

## Sử dụng cơ bản

```python
from magicimg.core import ImageProcessor

# Khởi tạo với cấu hình mặc định
processor = ImageProcessor()

# Hoặc với cấu hình tùy chỉnh
processor = ImageProcessor(
    config={
        "use_gpu": True,              # Bật/tắt GPU
        "gpu_id": 0,                  # ID của GPU muốn sử dụng
        "gpu_memory_limit": 0.7,      # Giới hạn bộ nhớ GPU (70%)
        "batch_size": 4,              # Số ảnh xử lý cùng lúc
        "parallel_jobs": 2,           # Số luồng xử lý song song
        "optimize_for_gpu": True      # Tối ưu các phép tính cho GPU
    }
)

# Xử lý một ảnh
result = processor.process_image("input.jpg", "output.jpg")

# Kiểm tra kết quả
if result.success:
    print(f"Xử lý thành công!")
    print(f"Chất lượng ảnh: {result.quality_metrics.quality_score}")
    print(f"Các bước đã thực hiện: {result.processing_steps}")
else:
    print(f"Lỗi: {result.error_message}")
```

## Xử lý batch

```python
import glob
from magicimg.core import ImageProcessor

# Khởi tạo processor
processor = ImageProcessor(
    config={
        "use_gpu": True,
        "batch_size": 4
    }
)

# Lấy danh sách ảnh
images = glob.glob("input/*.jpg")

# Xử lý theo batch
for i in range(0, len(images), processor.config["batch_size"]):
    batch = images[i:i + processor.config["batch_size"]]
    
    # Xử lý từng ảnh trong batch
    for img_path in batch:
        output_path = img_path.replace("input", "output")
        result = processor.process_image(img_path, output_path)
```

## Tối ưu hóa GPU

Thư viện tự động quản lý bộ nhớ GPU để tránh rò rỉ và tối ưu hiệu suất:

```python
from magicimg.core import ImageProcessor, gpu_memory_manager

processor = ImageProcessor(config={"use_gpu": True})

# Sử dụng context manager để tự động giải phóng bộ nhớ
with gpu_memory_manager():
    result = processor.process_image("input.jpg", "output.jpg")
```

## Debug và logging

Bật chế độ debug để lưu các ảnh trung gian và thông tin chi tiết:

```python
processor = ImageProcessor(
    debug_dir="debug",
    config={
        "debug": True
    }
)
```

## Cấu hình chi tiết

```python
config = {
    # Cấu hình GPU
    "use_gpu": True,              # Bật/tắt GPU
    "gpu_id": 0,                  # ID của GPU muốn sử dụng
    "gpu_memory_limit": 0.7,      # Giới hạn bộ nhớ GPU (70%)
    "batch_size": 4,              # Số ảnh xử lý cùng lúc
    "parallel_jobs": 2,           # Số luồng xử lý song song
    "optimize_for_gpu": True,     # Tối ưu các phép tính cho GPU
    
    # Ngưỡng chất lượng
    "min_blur_index": 80.0,       # Chỉ số mờ tối thiểu
    "max_dark_ratio": 0.2,        # Tỷ lệ pixel tối tối đa
    "min_brightness": 180.0,      # Độ sáng tối thiểu
    "min_contrast": 50.0,         # Độ tương phản tối thiểu
    "min_resolution": (1000, 1400), # Độ phân giải tối thiểu
    "min_quality_score": 0.7,     # Điểm chất lượng tối thiểu
    
    # Ngưỡng xử lý
    "min_skew_angle": 0.3,        # Góc nghiêng tối thiểu cần sửa
    "max_skew_angle": 30.0,       # Góc nghiêng tối đa có thể sửa
    "min_rotation_confidence": 0.8 # Độ tin cậy tối thiểu khi xoay
}
```

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request trên GitHub.

## Giấy phép

MIT License 