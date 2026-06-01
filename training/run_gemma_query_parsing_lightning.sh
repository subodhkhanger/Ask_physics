#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

CONFIG="${CONFIG:-training/configs/gemma_query_parsing_qlora.yaml}"
DATA_DIR="${DATA_DIR:-training/data/query_parsing}"
INSTALL_DEPS="${INSTALL_DEPS:-0}"

export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

echo "== Ask Physics Gemma query parsing QLoRA =="
echo "repo: $(pwd)"
echo "config: ${CONFIG}"
echo "data: ${DATA_DIR}"

if [ "${INSTALL_DEPS}" = "1" ]; then
  echo "== Installing QLoRA dependencies =="
  python -m pip install --upgrade pip
  python -m pip install -r training/requirements-qlora.txt
fi

if [ ! -f "${CONFIG}" ]; then
  echo "Missing config: ${CONFIG}" >&2
  echo "Make sure the latest repo files are synced to Lightning AI." >&2
  exit 1
fi

if [ ! -f "${DATA_DIR}/train.jsonl" ] || [ ! -f "${DATA_DIR}/dev.jsonl" ]; then
  echo "Query parsing dataset missing. Generating ${DATA_DIR}..."
  python training/scripts/prepare_query_parsing_dataset.py --output-dir "${DATA_DIR}"
fi

python - <<'PY'
from pathlib import Path
import json

paths = [
    Path("training/data/query_parsing/train.jsonl"),
    Path("training/data/query_parsing/dev.jsonl"),
    Path("training/data/query_parsing/test.jsonl"),
]
for path in paths:
    if not path.exists():
        raise SystemExit(f"missing dataset split: {path}")
    with path.open("r", encoding="utf-8") as handle:
        count = sum(1 for _ in handle)
    print(f"{path}: {count} rows")

sample = json.loads(paths[0].read_text(encoding="utf-8").splitlines()[0])
json.loads(sample["messages"][-1]["content"])
print("dataset json: ok")
PY

python - <<'PY'
import torch

print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if not torch.cuda.is_available():
    raise SystemExit("CUDA is not available. In Lightning AI, switch the Studio to a GPU runtime or install CUDA PyTorch.")

device = torch.cuda.get_device_name(0)
memory_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
print("cuda device:", device)
print("cuda memory GB:", round(memory_gb, 2))
PY

if ! command -v hf >/dev/null 2>&1; then
  echo "Warning: Hugging Face CLI 'hf' not found. If Gemma download fails, install huggingface_hub and run: hf auth login" >&2
else
  hf auth whoami >/dev/null 2>&1 || echo "Warning: not logged into Hugging Face. Run: hf auth login" >&2
fi

echo "== Starting training =="
python training/scripts/train_gemma_qlora.py --config "${CONFIG}"
