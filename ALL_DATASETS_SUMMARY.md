# Tóm Tắt Tất Cả Datasets AbstentionBench

## ✅ Tổng Quan

AbstentionBench có **23 datasets** (bao gồm dummy) đã được tích hợp vào script export.

## 📋 Danh Sách Đầy Đủ

Chạy lệnh sau để xem danh sách:
```bash
python3 export_datasets_simple.py --list
```

### Danh Sách 23 Datasets:

1. **dummy** - DummyDataset (để test)
2. **gsm8k** - GSM8K (math questions)
3. **bbq** - BBQDataset (Bias Benchmark for QA)
4. **kuq** - KUQDataset (Known Unknown Questions)
5. **coconot** - CoCoNotDataset
6. **falseqa** - FalseQADataset
7. **moralchoice** - MoralChoiceDataset
8. **self_aware** - SelfAwareDataset
9. **squad2** - Squad2Dataset (SQuAD 2.0)
10. **situated_qa** - SituatedQAGeoDataset
11. **qaqa** - QAQADataset (Question Answering with Questionable Assumptions)
12. **worldsense** - WorldSenseDataset
13. **alcuna** - ALCUNADataset
14. **gpqa** - GPQA (graduate level science questions)
15. **mediq** - MediQDataset
16. **mmlu_math** - MMLUMath
17. **mmlu_history** - MMLUHistory
18. **musique** - MusiqueDataset
19. **qasper** - QASPERDataset
20. **umwp** - UMWP
21. **freshqa** - FreshQADataset
22. **big_bench_disambiguate** - BigBenchDisambiguateDataset
23. **big_bench_known_unknowns** - BigBenchKnownUnknownsDataset

## ✅ Datasets Đã Test Thành Công

### 1. Dummy Dataset
- **Status**: ✅ PASSED
- **Samples**: 10
- **Format**: JSON
- **Validation**: ✓ VALID

### 2. GSM8K Dataset
- **Status**: ✅ PASSED
- **Samples**: 3 (test)
- **Format**: JSON
- **Validation**: ✓ VALID
- **Note**: Real math questions from GSM8K

### 3. BBQ Dataset
- **Status**: ✅ PASSED
- **Samples**: 3 (test)
- **Format**: JSON
- **Validation**: ✓ VALID
- **Note**: Real bias benchmark questions, auto-downloads from GitHub

### 4. CoCoNot Dataset
- **Status**: ✅ PASSED
- **Samples**: 3 (test)
- **Format**: JSON
- **Validation**: ✓ VALID
- **Note**: Auto-downloads from HuggingFace

## 📝 Cách Export

### Export một dataset:
```bash
python3 export_datasets_simple.py --dataset <tên_dataset> --output_dir ./exported --max_samples 10
```

### Ví dụ:
```bash
# Export GSM8K
python3 export_datasets_simple.py --dataset gsm8k --output_dir ./exported --max_samples 10

# Export BBQ
python3 export_datasets_simple.py --dataset bbq --output_dir ./exported --max_samples 10

# Export CoCoNot
python3 export_datasets_simple.py --dataset coconot --output_dir ./exported --max_samples 10
```

## 🔧 Dependencies

### Cơ bản (cho hầu hết datasets):
```bash
pip install --user --break-system-packages pandas pydantic torch datasets loguru jsonlines
```

### Bổ sung (cho một số datasets):
- **hydra-core**: Cần cho KUQ và một số datasets khác
- **requests**: Đã có sẵn trong Python

## ⚠️ Lưu Ý

1. **FreshQA**: Cần setup thủ công (xem README.md chính)
2. **KUQ**: Cần hydra-core để load category mapping
3. **Auto-download**: Một số datasets sẽ tự động download khi load lần đầu:
   - BBQ: Downloads từ GitHub
   - GSM8K, CoCoNot: Downloads từ HuggingFace
   - Các datasets khác từ HuggingFace

## 📊 Format Dữ Liệu

Tất cả datasets export ra cùng format JSON:

```json
{
  "dataset_index": 0,
  "question": "...",
  "reference_answers": ["..."],
  "should_abstain": true/false,
  "metadata": {...}
}
```

## 🎯 Next Steps

Để export tất cả datasets với script đầy đủ (cần môi trường AbstentionBench):

```bash
source activate.sh
python export_datasets.py --output_dir ./exported_datasets --format json
```

Script này sẽ export tất cả 23 datasets tự động.

