#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("cuda device:", torch.cuda.get_device_name(0))
else:
    raise SystemExit("CUDA is not available. Install a CUDA PyTorch build or move to a GPU runtime.")
PY

python training/scripts/train_gemma_qlora.py \
  --config training/configs/gemma_qlora.yaml
