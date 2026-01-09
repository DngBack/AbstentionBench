"""
Script để validate dữ liệu đã export, đảm bảo format đúng và đầy đủ.

Usage:
    python validate_exported_data.py --input_dir ./exported_datasets --format json
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_json_file(file_path: str) -> Dict:
    """Validate một file JSON đã export."""
    errors = []
    warnings = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            errors.append("Data phải là một list")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        if len(data) == 0:
            warnings.append("File rỗng")
        
        required_fields = ["question", "should_abstain", "reference_answers", "metadata"]
        
        for idx, item in enumerate(data):
            # Kiểm tra required fields
            for field in required_fields:
                if field not in item:
                    errors.append(f"Item {idx} thiếu field: {field}")
            
            # Kiểm tra types
            if "question" in item and not isinstance(item["question"], str):
                errors.append(f"Item {idx}: 'question' phải là string")
            
            if "should_abstain" in item and not isinstance(item["should_abstain"], bool):
                errors.append(f"Item {idx}: 'should_abstain' phải là boolean")
            
            if "reference_answers" in item and item["reference_answers"] is not None:
                if not isinstance(item["reference_answers"], list):
                    errors.append(f"Item {idx}: 'reference_answers' phải là list hoặc None")
            
            if "metadata" in item and not isinstance(item["metadata"], dict):
                errors.append(f"Item {idx}: 'metadata' phải là dict")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "num_items": len(data),
        }
        
    except json.JSONDecodeError as e:
        errors.append(f"Lỗi parse JSON: {e}")
        return {"valid": False, "errors": errors, "warnings": warnings}
    except Exception as e:
        errors.append(f"Lỗi không xác định: {e}")
        return {"valid": False, "errors": errors, "warnings": warnings}


def validate_csv_file(file_path: str) -> Dict:
    """Validate một file CSV đã export."""
    errors = []
    warnings = []
    
    try:
        df = pd.read_csv(file_path)
        
        if len(df) == 0:
            warnings.append("File rỗng")
        
        required_columns = ["question", "should_abstain", "reference_answers", "metadata"]
        
        for col in required_columns:
            if col not in df.columns:
                errors.append(f"Thiếu cột: {col}")
        
        # Kiểm tra có thể parse JSON trong các cột
        if "reference_answers" in df.columns:
            for idx, val in enumerate(df["reference_answers"]):
                if pd.notna(val):
                    try:
                        json.loads(val)
                    except:
                        errors.append(f"Row {idx}: 'reference_answers' không phải JSON hợp lệ")
        
        if "metadata" in df.columns:
            for idx, val in enumerate(df["metadata"]):
                if pd.notna(val):
                    try:
                        json.loads(val)
                    except:
                        errors.append(f"Row {idx}: 'metadata' không phải JSON hợp lệ")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "num_items": len(df),
        }
        
    except Exception as e:
        errors.append(f"Lỗi: {e}")
        return {"valid": False, "errors": errors, "warnings": warnings}


def validate_huggingface_dataset(dataset_path: str) -> Dict:
    """Validate một HuggingFace dataset đã export."""
    errors = []
    warnings = []
    
    try:
        from datasets import load_from_disk
        
        dataset = load_from_disk(dataset_path)
        
        if len(dataset) == 0:
            warnings.append("Dataset rỗng")
        
        required_features = ["question", "should_abstain", "reference_answers", "metadata"]
        
        for feature in required_features:
            if feature not in dataset.features:
                errors.append(f"Thiếu feature: {feature}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "num_items": len(dataset),
        }
        
    except ImportError:
        errors.append("Cần cài đặt 'datasets' library")
        return {"valid": False, "errors": errors, "warnings": warnings}
    except Exception as e:
        errors.append(f"Lỗi: {e}")
        return {"valid": False, "errors": errors, "warnings": warnings}


def validate_directory(input_dir: str, format: str):
    """Validate tất cả files trong thư mục."""
    input_path = Path(input_dir)
    
    if not input_path.exists():
        logger.error(f"Thư mục không tồn tại: {input_dir}")
        return
    
    results = {}
    
    if format == "json":
        files = list(input_path.glob("*.json"))
        # Loại trừ summary files
        files = [f for f in files if f.name not in ["export_summary.json", "validation_summary.json"]]
        
        for file_path in files:
            logger.info(f"Đang validate: {file_path.name}")
            result = validate_json_file(str(file_path))
            results[file_path.name] = result
            
    elif format == "csv":
        files = list(input_path.glob("*.csv"))
        
        for file_path in files:
            logger.info(f"Đang validate: {file_path.name}")
            result = validate_csv_file(str(file_path))
            results[file_path.name] = result
            
    elif format == "huggingface":
        # Tìm các thư mục (mỗi dataset là một thư mục)
        dirs = [d for d in input_path.iterdir() if d.is_dir()]
        
        for dir_path in dirs:
            logger.info(f"Đang validate: {dir_path.name}")
            result = validate_huggingface_dataset(str(dir_path))
            results[dir_path.name] = result
    
    # In kết quả
    logger.info("=" * 80)
    logger.info("KẾT QUẢ VALIDATION")
    logger.info("=" * 80)
    
    valid_count = 0
    invalid_count = 0
    
    for filename, result in results.items():
        status = "✓ VALID" if result["valid"] else "✗ INVALID"
        logger.info(f"{filename}: {status}")
        
        if "num_items" in result and result["num_items"] is not None:
            logger.info(f"  Số lượng items: {result['num_items']}")
        
        if result["warnings"]:
            for warning in result["warnings"]:
                logger.warning(f"  Warning: {warning}")
        
        if result["errors"]:
            for error in result["errors"][:5]:  # Chỉ hiển thị 5 lỗi đầu
                logger.error(f"  Error: {error}")
            if len(result["errors"]) > 5:
                logger.error(f"  ... và {len(result['errors']) - 5} lỗi khác")
        
        if result["valid"]:
            valid_count += 1
        else:
            invalid_count += 1
        
        logger.info("")
    
    logger.info(f"Tổng kết: {valid_count} valid, {invalid_count} invalid")
    
    # Lưu kết quả
    summary_path = input_path / "validation_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info(f"Kết quả validation đã lưu tại: {summary_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Validate dữ liệu đã export"
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Thư mục chứa dữ liệu đã export",
    )
    parser.add_argument(
        "--format",
        type=str,
        required=True,
        choices=["json", "csv", "huggingface"],
        help="Format của dữ liệu",
    )
    
    args = parser.parse_args()
    
    validate_directory(args.input_dir, args.format)


if __name__ == "__main__":
    main()

