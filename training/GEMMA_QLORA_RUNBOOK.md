# Gemma QLoRA CLI Runbook

This runbook trains a Gemma 4 QLoRA adapter for Ask Physics on a CUDA-compatible PyTorch GPU machine.

## 1. Prepare Lightning Environment

Lightning Studios use the default Studio environment. Do not create a new venv inside the Studio.

```bash
python -m pip install --upgrade pip
```

Install the CUDA PyTorch wheel that matches your machine. Example for CUDA 12.1:

```bash
python -m pip install --index-url https://download.pytorch.org/whl/cu121 torch torchvision torchaudio
```

Then install the QLoRA dependencies:

```bash
python -m pip install -r training/requirements-qlora.txt
```

## 2. Check CUDA

```bash
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("device:", torch.cuda.get_device_name(0))
    print("memory GB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
PY
```

If this prints `cuda available: False`, fix PyTorch/CUDA before training.

## 3. Authenticate For Gemma 4

Gemma 4 models may require accepting the model terms on Hugging Face.

```bash
hf auth login
hf auth whoami
```

## 4. Verify Dataset

```bash
python training/scripts/report_dataset.py \
  --raw training/data/raw/arxiv_metadata.jsonl \
  --labels training/data/bronze/regex_labels.jsonl \
  --sft-dir training/data/sft_balanced \
  --output training/reports/dataset_report_balanced.md
```

The first run should use:

```text
training/data/sft_balanced/train.jsonl
training/data/sft_balanced/dev.jsonl
training/data/sft_balanced/test.jsonl
```

## 5. Train

The training script can apply Gemma formatting in memory from `training/data/sft_balanced/*.jsonl`.
If you want to materialize the exact Gemma training text first, run:

```bash
python training/scripts/format_sft_for_gemma.py \
  --model google/gemma-4-E4B-it \
  --input-dir training/data/sft_balanced \
  --output-dir training/data/gemma_sft_balanced
```

Then update `training/configs/gemma_qlora.yaml`:

```yaml
data:
  train_file: training/data/gemma_sft_balanced/train.jsonl
  eval_file: training/data/gemma_sft_balanced/dev.jsonl
```

```bash
bash training/run_gemma_cuda.sh
```

Equivalent direct command:

```bash
python training/scripts/train_gemma_qlora.py \
  --config training/configs/gemma_qlora.yaml
```

Outputs are written to:

```text
training/runs/gemma-qlora-ask-physics/
```

The adapter is saved at:

```text
training/runs/gemma-qlora-ask-physics/adapter/
```

## 6. Smoke Inference

```bash
python training/scripts/run_gemma_inference.py \
  --config training/configs/gemma_qlora.yaml \
  --adapter-dir training/runs/gemma-qlora-ask-physics/adapter \
  --title "Example plasma diagnostic paper" \
  --abstract "The electron temperature reached 5.2 keV and the electron density was 7.1 x 10^19 m^-3 during the discharge."
```

The expected output shape is:

```json
{
  "measurements": [
    {
      "type": "temperature",
      "value": 5.2,
      "unit": "keV",
      "normalized_value": 5.2,
      "normalized_unit": "keV",
      "context": "...",
      "confidence": 0.9
    }
  ]
}
```

## 7. Evaluate

Start with a small evaluation limit:

```bash
python training/scripts/evaluate_gemma_extraction.py \
  --config training/configs/gemma_qlora.yaml \
  --adapter-dir training/runs/gemma-qlora-ask-physics/adapter \
  --eval-file training/data/sft_balanced/test.jsonl \
  --limit 50 \
  --output training/runs/gemma-qlora-ask-physics/eval_predictions.json
```

Then increase the limit or omit it:

```bash
python training/scripts/evaluate_gemma_extraction.py \
  --config training/configs/gemma_qlora.yaml \
  --adapter-dir training/runs/gemma-qlora-ask-physics/adapter \
  --eval-file training/data/sft_balanced/test.jsonl \
  --limit 0
```

## 8. Useful Config Changes

For a smaller GPU:

```yaml
data:
  max_seq_length: 1024
training:
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 16
```

For a larger GPU:

```yaml
data:
  max_seq_length: 4096
training:
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
```

For a stronger model, change:

```yaml
model:
  base_model: google/gemma-4-26B-A4B-it
```

For a smaller model, change:

```yaml
model:
  base_model: google/gemma-4-E2B-it
```

## 9. What Counts As Success

For the first run:

- Training starts without CUDA/quantization errors.
- Loss decreases.
- Adapter saves successfully.
- Smoke inference returns parseable JSON.
- Evaluation reports a nonzero JSON validity rate.

Do not claim final extraction quality until the gold review queue has been manually reviewed.

## 10. Troubleshooting

If training fails with:

```text
TypeError: Trainer.__init__() got an unexpected keyword argument 'tokenizer'
```

the script is using an old Hugging Face `Trainer` argument. Verify that there is no standalone `tokenizer=tokenizer,` argument in `Trainer(...)`:

```bash
grep -n "^[[:space:]]*tokenizer=tokenizer," training/scripts/train_gemma_qlora.py || echo "ok: no standalone Trainer tokenizer arg"
```

It is correct for this to remain:

```python
DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
```

The data collator still needs the tokenizer for causal language modeling batch padding.
