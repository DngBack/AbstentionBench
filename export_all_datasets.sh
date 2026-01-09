#!/bin/bash
# Script để export tất cả hoặc một số datasets của AbstentionBench

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

OUTPUT_DIR="./exported_datasets"
MAX_SAMPLES=100  # Số samples mặc định cho mỗi dataset

# Parse arguments
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --output_dir DIR     Thư mục output (mặc định: ./exported_datasets)"
    echo "  --max_samples N      Số samples tối đa cho mỗi dataset (mặc định: 100)"
    echo "  --datasets LIST      Danh sách datasets cách nhau bởi dấu phẩy (mặc định: tất cả)"
    echo "  --list               Chỉ hiển thị danh sách datasets"
    echo ""
    echo "Ví dụ:"
    echo "  $0                                    # Export tất cả datasets"
    echo "  $0 --max_samples 50                   # Export tất cả với 50 samples mỗi dataset"
    echo "  $0 --datasets gsm8k,bbq,kuq           # Chỉ export 3 datasets"
    echo "  $0 --list                             # Xem danh sách"
    exit 0
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output_dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --max_samples)
            MAX_SAMPLES="$2"
            shift 2
            ;;
        --datasets)
            DATASETS_LIST="$2"
            shift 2
            ;;
        --list)
            python3 export_datasets_simple.py --list
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage"
            exit 1
            ;;
    esac
done

# Tạo thư mục output
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}EXPORT ABSTENTIONBENCH DATASETS${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Output directory: $OUTPUT_DIR"
echo "Max samples per dataset: $MAX_SAMPLES"
echo ""

# Danh sách tất cả datasets
ALL_DATASETS=(
    "dummy"
    "gsm8k"
    "bbq"
    "kuq"
    "coconot"
    "falseqa"
    "moralchoice"
    "self_aware"
    "squad2"
    "situated_qa"
    "qaqa"
    "worldsense"
    "alcuna"
    "gpqa"
    "mediq"
    "mmlu_math"
    "mmlu_history"
    "musique"
    "qasper"
    "umwp"
    "freshqa"
    "big_bench_disambiguate"
    "big_bench_known_unknowns"
)

# Nếu có danh sách datasets cụ thể
if [ -n "$DATASETS_LIST" ]; then
    IFS=',' read -ra DATASETS <<< "$DATASETS_LIST"
else
    DATASETS=("${ALL_DATASETS[@]}")
fi

echo "Sẽ export ${#DATASETS[@]} datasets..."
echo ""

# Đếm thành công/thất bại
SUCCESS=0
FAILED=0
FAILED_LIST=()

# Export từng dataset
for dataset in "${DATASETS[@]}"; do
    dataset=$(echo "$dataset" | xargs)  # Trim whitespace
    echo -e "${YELLOW}[$((SUCCESS + FAILED + 1))/${#DATASETS[@]}] Exporting: $dataset${NC}"
    
    if python3 export_datasets_simple.py --dataset "$dataset" --output_dir "$OUTPUT_DIR" --max_samples "$MAX_SAMPLES" > /tmp/export_${dataset}.log 2>&1; then
        echo -e "${GREEN}✓ Success: $dataset${NC}"
        ((SUCCESS++))
    else
        echo -e "${RED}✗ Failed: $dataset${NC}"
        ((FAILED++))
        FAILED_LIST+=("$dataset")
        # Hiển thị lỗi
        tail -5 /tmp/export_${dataset}.log
    fi
    echo ""
done

# Tổng kết
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}TỔNG KẾT${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Thành công: ${GREEN}$SUCCESS${NC}"
echo -e "Thất bại: ${RED}$FAILED${NC}"

if [ $FAILED -gt 0 ]; then
    echo -e "\n${RED}Datasets thất bại:${NC}"
    for ds in "${FAILED_LIST[@]}"; do
        echo -e "  - ${RED}$ds${NC}"
    done
    echo -e "\nXem log tại: /tmp/export_<dataset>.log"
fi

echo -e "\nDữ liệu đã được lưu tại: ${GREEN}$OUTPUT_DIR${NC}"

# Validate
if [ $SUCCESS -gt 0 ]; then
    echo ""
    echo "Đang validate dữ liệu..."
    python3 validate_exported_data.py --input_dir "$OUTPUT_DIR" --format json 2>&1 | tail -10
fi

