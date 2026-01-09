"""
Script export datasets đơn giản - không cần Hydra, chỉ cần import trực tiếp.
Dùng để test với dữ liệu thực tế.

Hỗ trợ tất cả 20+ datasets của AbstentionBench.

Usage:
    python3 export_datasets_simple.py --dataset dummy --output_dir ./test_export
    python3 export_datasets_simple.py --dataset gsm8k --output_dir ./test_export --max_samples 10
    python3 export_datasets_simple.py --list  # Xem danh sách datasets
"""

import argparse
import json
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapping từ tên dataset (config name) sang class và module
DATASET_MAPPING = {
    "dummy": ("DummyDataset", "recipe.abstention_datasets.abstract_abstention_dataset"),
    "gsm8k": ("GSM8K", "recipe.abstention_datasets.gsm8k"),
    "bbq": ("BBQDataset", "recipe.abstention_datasets.bbq"),
    "kuq": ("KUQDataset", "recipe.abstention_datasets.kuq"),
    "coconot": ("CoCoNotDataset", "recipe.abstention_datasets.coconot"),
    "falseqa": ("FalseQADataset", "recipe.abstention_datasets.false_qa"),
    "moralchoice": ("MoralChoiceDataset", "recipe.abstention_datasets.moralchoice"),
    "self_aware": ("SelfAwareDataset", "recipe.abstention_datasets.self_aware"),
    "squad2": ("Squad2Dataset", "recipe.abstention_datasets.squad"),
    "situated_qa": ("SituatedQAGeoDataset", "recipe.abstention_datasets.situated_qa"),
    "qaqa": ("QAQADataset", "recipe.abstention_datasets.qaqa"),
    "worldsense": ("WorldSenseDataset", "recipe.abstention_datasets.world_sense"),
    # Các datasets khác có thể cần thêm params
    "alcuna": ("ALCUNADataset", "recipe.abstention_datasets.alcuna"),
    "gpqa": ("GPQA", "recipe.abstention_datasets.gpqa"),
    "mediq": ("MediQDataset", "recipe.abstention_datasets.mediq"),
    "mmlu_math": ("MMLUMath", "recipe.abstention_datasets.mmlu"),
    "mmlu_history": ("MMLUHistory", "recipe.abstention_datasets.mmlu"),
    "musique": ("MusiqueDataset", "recipe.abstention_datasets.musique"),
    "qasper": ("QASPERDataset", "recipe.abstention_datasets.qasper"),
    "umwp": ("UMWP", "recipe.abstention_datasets.umwp"),
    # Các datasets cần setup đặc biệt
    "freshqa": ("FreshQADataset", "recipe.abstention_datasets.freshqa"),
    "big_bench_disambiguate": ("BigBenchDisambiguateDataset", "recipe.abstention_datasets.big_bench"),
    "big_bench_known_unknowns": ("BigBenchKnownUnknownsDataset", "recipe.abstention_datasets.big_bench"),
}


def load_dataset_class(dataset_name: str):
    """Load dataset class từ mapping."""
    if dataset_name not in DATASET_MAPPING:
        raise ValueError(f"Dataset '{dataset_name}' không được hỗ trợ. Chạy --list để xem danh sách.")
    
    class_name, module_path = DATASET_MAPPING[dataset_name]
    module = __import__(module_path, fromlist=[class_name])
    dataset_class = getattr(module, class_name)
    return dataset_class


def export_dataset(dataset_name: str, output_dir: str, max_samples: int = 5, **kwargs):
    """Export một dataset bất kỳ."""
    try:
        dataset_class = load_dataset_class(dataset_name)
        
        logger.info(f"Đang load {dataset_name}...")
        
        # Tạo instance dataset với params phù hợp
        if dataset_name == "dummy":
            dataset = dataset_class(max_num_samples=max_samples)
        elif dataset_name == "gsm8k":
            dataset = dataset_class(split="test", max_num_samples=max_samples)
        elif dataset_name == "kuq":
            # KUQ cần category_map_path
            category_map_path = kwargs.get("category_map_path", "data/kuq/new-category-mapping.csv")
            dataset = dataset_class(max_num_samples=max_samples, category_map_path=category_map_path)
        elif dataset_name == "bbq":
            dataset = dataset_class(max_num_samples=max_samples)
        elif dataset_name in ["coconot", "falseqa", "moralchoice", "self_aware", 
                              "squad2", "situated_qa", "qaqa", "worldsense",
                              "alcuna", "gpqa", "mediq", "musique", "qasper", "umwp"]:
            dataset = dataset_class(max_num_samples=max_samples)
        elif dataset_name == "mmlu_math":
            dataset = dataset_class(split="test", max_num_samples=max_samples)
        elif dataset_name == "mmlu_history":
            dataset = dataset_class(split="test", max_num_samples=max_samples)
        elif dataset_name == "freshqa":
            # FreshQA cần setup đặc biệt
            logger.warning("FreshQA cần setup thủ công. Xem README.md")
            dataset = dataset_class(max_num_samples=max_samples)
        elif dataset_name in ["big_bench_disambiguate", "big_bench_known_unknowns"]:
            dataset = dataset_class(max_num_samples=max_samples)
        else:
            # Default: thử với max_num_samples
            dataset = dataset_class(max_num_samples=max_samples)
        
        logger.info(f"Dataset size: {len(dataset)}")
        
        # Extract prompts
        prompts = []
        dataset_len = min(len(dataset), max_samples) if max_samples else len(dataset)
        
        for idx in range(dataset_len):
            try:
                prompt = dataset[idx]
                prompt_dict = {
                    "dataset_index": idx,
                    "question": prompt.question,
                    "reference_answers": prompt.reference_answers,
                    "should_abstain": prompt.should_abstain,
                    "metadata": prompt.metadata,
                }
                prompts.append(prompt_dict)
                
                if (idx + 1) % 10 == 0:
                    logger.info(f"Đã extract {idx + 1}/{dataset_len} samples...")
            except Exception as e:
                logger.warning(f"Lỗi khi extract sample {idx}: {e}")
                continue
        
        # Export ra JSON
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{dataset_name}.json")
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ Đã export {len(prompts)} samples ra {output_file}")
        
        # Validate
        with open(output_file, "r") as f:
            data = json.load(f)
            assert len(data) > 0, "File rỗng"
            assert "question" in data[0], "Thiếu field question"
            logger.info("✓ Validation passed")
        
        # In một vài samples
        logger.info("\n" + "="*80)
        logger.info("MẪU DỮ LIỆU ĐÃ EXPORT:")
        logger.info("="*80)
        for i, item in enumerate(data[:2]):
            logger.info(f"\nSample {i}:")
            logger.info(f"  Question: {item['question'][:100]}...")
            logger.info(f"  Should abstain: {item['should_abstain']}")
            logger.info(f"  Reference answers: {item['reference_answers']}")
        
        return True
        
    except ImportError as e:
        logger.error(f"Lỗi import: {e}")
        logger.error("Có thể cần cài đặt thêm dependencies")
        return False
    except Exception as e:
        logger.error(f"Lỗi: {e}", exc_info=True)
        return False


def list_datasets():
    """In danh sách tất cả datasets có sẵn."""
    logger.info("="*80)
    logger.info("DANH SÁCH DATASETS CÓ SẴN")
    logger.info("="*80)
    logger.info(f"\nTổng số: {len(DATASET_MAPPING)} datasets\n")
    
    for i, (name, (class_name, module)) in enumerate(DATASET_MAPPING.items(), 1):
        logger.info(f"{i:2d}. {name:25s} -> {class_name}")
    
    logger.info("\n" + "="*80)
    logger.info("Sử dụng: python3 export_datasets_simple.py --dataset <tên_dataset>")
    logger.info("="*80)


def main():
    parser = argparse.ArgumentParser(description="Export datasets đơn giản (không cần Hydra)")
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Dataset để export (xem --list để biết danh sách)",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./test_export",
        help="Thư mục output",
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=5,
        help="Số lượng samples tối đa (mặc định: 5)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Hiển thị danh sách tất cả datasets có sẵn",
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_datasets()
        return
    
    if args.dataset is None:
        logger.error("Cần chỉ định --dataset hoặc dùng --list để xem danh sách")
        parser.print_help()
        return
    
    logger.info("="*80)
    logger.info(f"EXPORT DATASET: {args.dataset}")
    logger.info("="*80)
    
    success = export_dataset(
        args.dataset,
        args.output_dir,
        args.max_samples,
    )
    
    if success:
        logger.info("\n" + "="*80)
        logger.info("✓ EXPORT THÀNH CÔNG!")
        logger.info("="*80)
        logger.info(f"Dữ liệu đã được lưu tại: {args.output_dir}")
    else:
        logger.error("\n" + "="*80)
        logger.error("✗ EXPORT THẤT BẠI!")
        logger.error("="*80)


if __name__ == "__main__":
    main()

