"""
Script test đơn giản để kiểm tra export datasets hoạt động đúng.

Usage:
    python test_export.py
"""

import logging
import os
import tempfile
from pathlib import Path

from export_datasets import export_single_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_export_dummy():
    """Test export dummy dataset."""
    logger.info("=" * 80)
    logger.info("TEST: Export dummy dataset")
    logger.info("=" * 80)
    
    # Tạo thư mục temp
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = os.path.join(tmpdir, "test_export")
        
        # Test export JSON
        logger.info("\n1. Test export JSON format...")
        success = export_single_dataset("dummy", output_dir, "json")
        assert success, "Export JSON failed"
        
        # Kiểm tra file đã được tạo
        json_file = os.path.join(output_dir, "dummy.json")
        assert os.path.exists(json_file), f"File {json_file} không tồn tại"
        
        # Kiểm tra nội dung
        import json
        with open(json_file, "r") as f:
            data = json.load(f)
        assert len(data) > 0, "File JSON rỗng"
        assert "question" in data[0], "Thiếu field 'question'"
        
        logger.info("✓ JSON export thành công!")
        
        # Test export CSV
        logger.info("\n2. Test export CSV format...")
        success = export_single_dataset("dummy", output_dir, "csv")
        assert success, "Export CSV failed"
        
        csv_file = os.path.join(output_dir, "dummy.csv")
        assert os.path.exists(csv_file), f"File {csv_file} không tồn tại"
        
        import pandas as pd
        df = pd.read_csv(csv_file)
        assert len(df) > 0, "File CSV rỗng"
        assert "question" in df.columns, "Thiếu cột 'question'"
        
        logger.info("✓ CSV export thành công!")
        
        logger.info("\n" + "=" * 80)
        logger.info("TẤT CẢ TESTS ĐÃ PASS!")
        logger.info("=" * 80)


if __name__ == "__main__":
    test_export_dummy()

