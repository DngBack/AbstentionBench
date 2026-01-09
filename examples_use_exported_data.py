"""
Ví dụ sử dụng dữ liệu đã export từ AbstentionBench.

Các ví dụ này minh họa cách load và sử dụng dữ liệu đã export
ở các format khác nhau.
"""

import json
from pathlib import Path

# ============================================================================
# VÍ DỤ 1: Load và sử dụng dữ liệu JSON
# ============================================================================

def example_load_json():
    """Ví dụ load và xử lý dữ liệu từ file JSON."""
    print("=" * 80)
    print("VÍ DỤ 1: Load dữ liệu từ JSON")
    print("=" * 80)
    
    # Giả sử bạn đã export dataset ra JSON
    json_file = "exported_datasets/gsm8k.json"
    
    # Load dữ liệu
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Tổng số samples: {len(data)}")
    
    # Xem một vài samples
    for i, item in enumerate(data[:3]):
        print(f"\nSample {i}:")
        print(f"  Question: {item['question']}")
        print(f"  Should abstain: {item['should_abstain']}")
        print(f"  Reference answers: {item['reference_answers']}")
        print(f"  Metadata: {item['metadata']}")
    
    # Thống kê
    abstain_count = sum(1 for item in data if item['should_abstain'])
    answerable_count = len(data) - abstain_count
    
    print(f"\nThống kê:")
    print(f"  Cần abstain: {abstain_count} ({abstain_count/len(data)*100:.1f}%)")
    print(f"  Có thể trả lời: {answerable_count} ({answerable_count/len(data)*100:.1f}%)")


# ============================================================================
# VÍ DỤ 2: Load và sử dụng dữ liệu CSV
# ============================================================================

def example_load_csv():
    """Ví dụ load và xử lý dữ liệu từ file CSV."""
    print("\n" + "=" * 80)
    print("VÍ DỤ 2: Load dữ liệu từ CSV")
    print("=" * 80)
    
    import pandas as pd
    
    # Load CSV
    csv_file = "exported_datasets/gsm8k.csv"
    df = pd.read_csv(csv_file)
    
    print(f"Tổng số samples: {len(df)}")
    print(f"\nCác cột: {df.columns.tolist()}")
    
    # Xem một vài samples
    print("\n5 samples đầu tiên:")
    for idx, row in df.head().iterrows():
        print(f"\nSample {idx}:")
        print(f"  Question: {row['question']}")
        print(f"  Should abstain: {row['should_abstain']}")
        
        # Parse JSON trong các cột
        if pd.notna(row['reference_answers']):
            answers = json.loads(row['reference_answers'])
            print(f"  Reference answers: {answers}")
        else:
            print(f"  Reference answers: None")
    
    # Thống kê với pandas
    print(f"\nThống kê:")
    print(df['should_abstain'].value_counts())


# ============================================================================
# VÍ DỤ 3: Load và sử dụng HuggingFace Dataset
# ============================================================================

def example_load_huggingface():
    """Ví dụ load và sử dụng HuggingFace Dataset."""
    print("\n" + "=" * 80)
    print("VÍ DỤ 3: Load dữ liệu từ HuggingFace Dataset")
    print("=" * 80)
    
    try:
        from datasets import load_from_disk
        
        dataset_path = "exported_datasets/gsm8k"
        dataset = load_from_disk(dataset_path)
        
        print(f"Tổng số samples: {len(dataset)}")
        print(f"Features: {list(dataset.features.keys())}")
        
        # Xem một vài samples
        print("\n3 samples đầu tiên:")
        for i in range(min(3, len(dataset))):
            item = dataset[i]
            print(f"\nSample {i}:")
            print(f"  Question: {item['question']}")
            print(f"  Should abstain: {item['should_abstain']}")
            print(f"  Reference answers: {item['reference_answers']}")
        
        # Filter và map với HuggingFace API
        abstain_samples = dataset.filter(lambda x: x['should_abstain'])
        answerable_samples = dataset.filter(lambda x: not x['should_abstain'])
        
        print(f"\nThống kê:")
        print(f"  Cần abstain: {len(abstain_samples)}")
        print(f"  Có thể trả lời: {len(answerable_samples)}")
        
    except ImportError:
        print("Cần cài đặt 'datasets' library: pip install datasets")


# ============================================================================
# VÍ DỤ 4: Convert giữa các formats
# ============================================================================

def example_convert_formats():
    """Ví dụ convert dữ liệu giữa các formats."""
    print("\n" + "=" * 80)
    print("VÍ DỤ 4: Convert giữa các formats")
    print("=" * 80)
    
    # Load từ JSON
    json_file = "exported_datasets/gsm8k.json"
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Convert sang CSV
    import pandas as pd
    
    rows = []
    for item in data:
        row = {
            "question": item["question"],
            "should_abstain": item["should_abstain"],
            "reference_answers": json.dumps(item["reference_answers"]) if item["reference_answers"] else None,
            "metadata": json.dumps(item["metadata"]) if item["metadata"] else None,
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    output_csv = "converted_data.csv"
    df.to_csv(output_csv, index=False)
    print(f"Đã convert JSON sang CSV: {output_csv}")
    
    # Convert sang HuggingFace Dataset
    try:
        from datasets import Dataset
        
        dataset_dict = {
            "question": [item["question"] for item in data],
            "should_abstain": [item["should_abstain"] for item in data],
            "reference_answers": [item["reference_answers"] for item in data],
            "metadata": [item["metadata"] for item in data],
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        output_hf = "converted_hf_dataset"
        dataset.save_to_disk(output_hf)
        print(f"Đã convert JSON sang HuggingFace Dataset: {output_hf}")
        
    except ImportError:
        print("Cần cài đặt 'datasets' library để convert sang HuggingFace format")


# ============================================================================
# VÍ DỤ 5: Tạo dataset tùy chỉnh từ dữ liệu đã export
# ============================================================================

def example_create_custom_dataset():
    """Ví dụ tạo dataset tùy chỉnh từ dữ liệu đã export."""
    print("\n" + "=" * 80)
    print("VÍ DỤ 5: Tạo dataset tùy chỉnh")
    print("=" * 80)
    
    # Load dữ liệu từ nhiều datasets
    datasets_to_load = ["gsm8k", "bbq", "kuq"]
    
    all_data = []
    for dataset_name in datasets_to_load:
        json_file = f"exported_datasets/{dataset_name}.json"
        if Path(json_file).exists():
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Thêm thông tin dataset source
                for item in data:
                    item["source_dataset"] = dataset_name
                all_data.extend(data)
    
    print(f"Tổng số samples từ {len(datasets_to_load)} datasets: {len(all_data)}")
    
    # Filter chỉ lấy các samples cần abstain
    abstain_only = [item for item in all_data if item["should_abstain"]]
    print(f"Số samples cần abstain: {len(abstain_only)}")
    
    # Lưu dataset tùy chỉnh
    output_file = "custom_abstention_dataset.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(abstain_only, f, ensure_ascii=False, indent=2)
    
    print(f"Đã lưu dataset tùy chỉnh: {output_file}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("VÍ DỤ SỬ DỤNG DỮ LIỆU ĐÃ EXPORT TỪ ABSTENTIONBENCH")
    print("=" * 80)
    print("\nLưu ý: Các ví dụ này giả định bạn đã export datasets.")
    print("Chạy: python export_datasets.py --output_dir ./exported_datasets --format json")
    print("\n")
    
    # Chạy các ví dụ (comment/uncomment để chạy)
    # example_load_json()
    # example_load_csv()
    # example_load_huggingface()
    # example_convert_formats()
    # example_create_custom_dataset()
    
    print("\nUncomment các hàm example_*() để chạy ví dụ cụ thể!")

