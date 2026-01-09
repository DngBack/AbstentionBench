# Hướng Dẫn Export Dữ Liệu AbstentionBench

## 🚀 Cách Nhanh Nhất

### Export một dataset cụ thể:
```bash
python3 export_datasets_simple.py --dataset gsm8k --output_dir ./exported_datasets --max_samples 100
```

### Export nhiều datasets cùng lúc:
```bash
./export_all_datasets.sh --datasets gsm8k,bbq,kuq --max_samples 50
```

### Export TẤT CẢ datasets:
```bash
./export_all_datasets.sh --max_samples 100
```

## 📋 Xem Danh Sách Datasets

```bash
python3 export_datasets_simple.py --list
```

Hoặc:
```bash
./export_all_datasets.sh --list
```

## 📝 Các Lệnh Chi Tiết

### 1. Export một dataset

**Cú pháp:**
```bash
python3 export_datasets_simple.py --dataset <tên_dataset> --output_dir <thư_mục> --max_samples <số_lượng>
```

**Ví dụ:**
```bash
# Export GSM8K với 100 samples
python3 export_datasets_simple.py --dataset gsm8k --output_dir ./exported --max_samples 100

# Export BBQ với 50 samples
python3 export_datasets_simple.py --dataset bbq --output_dir ./exported --max_samples 50

# Export CoCoNot với 200 samples
python3 export_datasets_simple.py --dataset coconot --output_dir ./exported --max_samples 200
```

### 2. Export tất cả datasets (script tự động)

**Cú pháp:**
```bash
./export_all_datasets.sh [options]
```

**Options:**
- `--output_dir DIR`: Thư mục output (mặc định: `./exported_datasets`)
- `--max_samples N`: Số samples tối đa cho mỗi dataset (mặc định: 100)
- `--datasets LIST`: Danh sách datasets cách nhau bởi dấu phẩy
- `--list`: Chỉ hiển thị danh sách datasets

**Ví dụ:**
```bash
# Export tất cả với 100 samples mỗi dataset
./export_all_datasets.sh

# Export tất cả với 50 samples
./export_all_datasets.sh --max_samples 50

# Export chỉ 3 datasets
./export_all_datasets.sh --datasets gsm8k,bbq,kuq --max_samples 100

# Export vào thư mục khác
./export_all_datasets.sh --output_dir ./my_exported_data --max_samples 200
```

### 3. Validate dữ liệu đã export

```bash
python3 validate_exported_data.py --input_dir ./exported_datasets --format json
```

## 📂 Cấu Trúc Output

Sau khi export, bạn sẽ có:

```
exported_datasets/
├── dummy.json
├── gsm8k.json
├── bbq.json
├── kuq.json
├── coconot.json
├── ...
└── validation_summary.json
```

Mỗi file JSON chứa một mảng các samples với format:

```json
[
  {
    "dataset_index": 0,
    "question": "Câu hỏi...",
    "reference_answers": ["Đáp án 1", "Đáp án 2"],
    "should_abstain": true,
    "metadata": {...}
  },
  ...
]
```

## ⚡ Ví Dụ Thực Tế

### Export 5 datasets phổ biến:
```bash
./export_all_datasets.sh --datasets gsm8k,bbq,kuq,coconot,moralchoice --max_samples 100
```

### Export tất cả với số lượng nhỏ để test:
```bash
./export_all_datasets.sh --max_samples 10
```

### Export đầy đủ tất cả datasets:
```bash
./export_all_datasets.sh --max_samples 1000
```

## 🔍 Kiểm Tra Kết Quả

Sau khi export, kiểm tra:

```bash
# Xem danh sách files đã export
ls -lh exported_datasets/*.json

# Validate tất cả
python3 validate_exported_data.py --input_dir ./exported_datasets --format json

# Xem một file cụ thể
head -50 exported_datasets/gsm8k.json
```

## ⚠️ Lưu Ý

1. **Lần đầu download**: Một số datasets sẽ tự động download từ HuggingFace/GitHub khi load lần đầu (có thể mất thời gian)

2. **Dependencies**: Đảm bảo đã cài đặt:
   ```bash
   pip install --user --break-system-packages pandas pydantic torch datasets loguru jsonlines
   ```

3. **FreshQA**: Dataset FreshQA cần setup thủ công (xem README.md)

4. **KUQ**: Có thể cần `hydra-core` để load category mapping

5. **Disk space**: Export tất cả datasets với nhiều samples có thể tốn nhiều dung lượng

## 📊 Thống Kê

- **Tổng số datasets**: 23
- **Format output**: JSON
- **Mỗi sample có**: question, reference_answers, should_abstain, metadata

## 🎯 Next Steps

Sau khi export, bạn có thể:
- Sử dụng dữ liệu trong các project khác
- Phân tích dữ liệu với pandas
- Load vào HuggingFace Dataset format
- Chia sẻ dữ liệu với team

Xem `examples_use_exported_data.py` để biết cách sử dụng dữ liệu đã export.

