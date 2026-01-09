"""
Script để tái tạo và export tất cả datasets của AbstentionBench
ra format JSON/CSV/HuggingFace Dataset để sử dụng ở nơi khác.

Usage:
    python export_datasets.py --output_dir ./exported_datasets --format json
    python export_datasets.py --output_dir ./exported_datasets --format csv
    python export_datasets.py --output_dir ./exported_datasets --format huggingface
    python export_datasets.py --dataset gsm8k --output_dir ./exported_datasets --format json
"""

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from hydra import compose, initialize
from hydra.utils import instantiate, to_absolute_path
from omegaconf import OmegaConf

from recipe.abstention_datasets.abstract_abstention_dataset import Prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dataset_from_config(dataset_name: str, data_dir: Optional[str] = None) -> tuple:
    """
    Load dataset từ config file.
    
    Returns:
        (dataset_instance, dataset_name_class)
    """
    try:
        with initialize(version_base="1.2", config_path="configs"):
            cfg = compose(
                config_name="default_pipeline.yaml",
                overrides=[f"dataset={dataset_name}"]
            )
            
            # Override data_dir nếu được cung cấp
            if data_dir is not None:
                cfg.data_dir = data_dir
                # Resolve lại để cập nhật các path phụ thuộc
                OmegaConf.resolve(cfg)
            
            dataset = instantiate(cfg.datamodule)
            dataset_class_name = cfg.dataset_name
            
            return dataset, dataset_class_name
    except Exception as e:
        logger.error(f"Lỗi khi load dataset {dataset_name}: {e}")
        raise


def extract_all_prompts(dataset) -> List[Dict]:
    """
    Extract tất cả prompts từ dataset.
    
    Returns:
        List of dictionaries chứa thông tin prompt
    """
    prompts = []
    dataset_len = len(dataset)
    
    logger.info(f"Đang extract {dataset_len} prompts...")
    
    for idx in range(dataset_len):
        try:
            prompt: Prompt = dataset[idx]
            
            # Convert Prompt object thành dictionary
            prompt_dict = {
                "dataset_index": idx,
                "question": prompt.question,
                "reference_answers": prompt.reference_answers,
                "should_abstain": prompt.should_abstain,
                "metadata": prompt.metadata,
            }
            
            prompts.append(prompt_dict)
            
            if (idx + 1) % 100 == 0:
                logger.info(f"Đã extract {idx + 1}/{dataset_len} prompts...")
                
        except Exception as e:
            logger.warning(f"Lỗi khi extract prompt tại index {idx}: {e}")
            continue
    
    return prompts


def export_to_json(prompts: List[Dict], output_path: str):
    """Export prompts ra file JSON."""
    logger.info(f"Đang export {len(prompts)} prompts ra JSON: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)
    logger.info(f"Đã export thành công!")


def export_to_csv(prompts: List[Dict], output_path: str):
    """Export prompts ra file CSV."""
    logger.info(f"Đang export {len(prompts)} prompts ra CSV: {output_path}")
    
    # Flatten data cho CSV
    rows = []
    for prompt in prompts:
        row = {
            "dataset_index": prompt["dataset_index"],
            "question": prompt["question"],
            "reference_answers": json.dumps(prompt["reference_answers"]) if prompt["reference_answers"] else None,
            "should_abstain": prompt["should_abstain"],
            "metadata": json.dumps(prompt["metadata"]) if prompt["metadata"] else None,
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Đã export thành công!")


def export_to_huggingface(prompts: List[Dict], output_path: str):
    """Export prompts ra HuggingFace Dataset format."""
    try:
        from datasets import Dataset
        
        logger.info(f"Đang export {len(prompts)} prompts ra HuggingFace Dataset: {output_path}")
        
        # Convert prompts thành format cho HuggingFace
        dataset_dict = {
            "question": [p["question"] for p in prompts],
            "reference_answers": [p["reference_answers"] for p in prompts],
            "should_abstain": [p["should_abstain"] for p in prompts],
            "metadata": [p["metadata"] for p in prompts],
        }
        
        dataset = Dataset.from_dict(dataset_dict)
        dataset.save_to_disk(output_path)
        logger.info(f"Đã export thành công!")
        
    except ImportError:
        logger.error("Cần cài đặt 'datasets' library để export HuggingFace format")
        raise


def get_all_dataset_names(exclude_dummy: bool = True) -> List[str]:
    """Lấy danh sách tất cả dataset names từ config files."""
    config_dir = Path("configs/dataset")
    dataset_names = []
    
    for config_file in config_dir.glob("*.yaml"):
        dataset_name = config_file.stem
        if exclude_dummy and dataset_name == "dummy":
            continue
        dataset_names.append(dataset_name)
    
    return sorted(dataset_names)


def export_single_dataset(
    dataset_name: str,
    output_dir: str,
    format: str = "json",
    data_dir: Optional[str] = None,
):
    """Export một dataset."""
    logger.info(f"=" * 80)
    logger.info(f"Đang xử lý dataset: {dataset_name}")
    logger.info(f"=" * 80)
    
    try:
        # Load dataset
        dataset, dataset_class_name = load_dataset_from_config(dataset_name, data_dir)
        logger.info(f"Dataset class: {dataset_class_name}")
        logger.info(f"Dataset size: {len(dataset)}")
        
        # Extract prompts
        prompts = extract_all_prompts(dataset)
        
        # Tạo output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Export theo format
        if format == "json":
            output_path = os.path.join(output_dir, f"{dataset_name}.json")
            export_to_json(prompts, output_path)
        elif format == "csv":
            output_path = os.path.join(output_dir, f"{dataset_name}.csv")
            export_to_csv(prompts, output_path)
        elif format == "huggingface":
            output_path = os.path.join(output_dir, dataset_name)
            export_to_huggingface(prompts, output_path)
        else:
            raise ValueError(f"Format không hợp lệ: {format}. Chọn: json, csv, huggingface")
        
        logger.info(f"Đã export dataset {dataset_name} thành công!")
        return True
        
    except Exception as e:
        logger.error(f"Lỗi khi export dataset {dataset_name}: {e}", exc_info=True)
        return False


def export_all_datasets(
    output_dir: str,
    format: str = "json",
    data_dir: Optional[str] = None,
    exclude_dummy: bool = True,
):
    """Export tất cả datasets."""
    dataset_names = get_all_dataset_names(exclude_dummy=exclude_dummy)
    
    logger.info(f"Tìm thấy {len(dataset_names)} datasets để export")
    logger.info(f"Datasets: {', '.join(dataset_names)}")
    
    results = {}
    for dataset_name in dataset_names:
        success = export_single_dataset(dataset_name, output_dir, format, data_dir)
        results[dataset_name] = "success" if success else "failed"
    
    # Tạo summary file
    summary_path = os.path.join(output_dir, "export_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"=" * 80)
    logger.info("TỔNG KẾT EXPORT")
    logger.info(f"=" * 80)
    success_count = sum(1 for v in results.values() if v == "success")
    failed_count = len(results) - success_count
    logger.info(f"Thành công: {success_count}/{len(results)}")
    logger.info(f"Thất bại: {failed_count}/{len(results)}")
    logger.info(f"Summary file: {summary_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Export AbstentionBench datasets ra format khác nhau"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Tên dataset cụ thể để export (nếu không có thì export tất cả)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./exported_datasets",
        help="Thư mục output",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="json",
        choices=["json", "csv", "huggingface"],
        help="Format export: json, csv, hoặc huggingface",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default=None,
        help="Thư mục chứa data (override từ config)",
    )
    parser.add_argument(
        "--include_dummy",
        action="store_true",
        help="Bao gồm dummy dataset",
    )
    
    args = parser.parse_args()
    
    if args.dataset:
        # Export một dataset cụ thể
        export_single_dataset(
            args.dataset,
            args.output_dir,
            args.format,
            args.data_dir,
        )
    else:
        # Export tất cả datasets
        export_all_datasets(
            args.output_dir,
            args.format,
            args.data_dir,
            exclude_dummy=not args.include_dummy,
        )


if __name__ == "__main__":
    main()

