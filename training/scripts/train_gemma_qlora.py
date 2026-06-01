#!/usr/bin/env python3
"""
Train a Gemma QLoRA adapter for Ask Physics extraction.

The script expects SFT chat JSONL records produced by
training/scripts/prepare_sft_dataset.py and saves a PEFT adapter that can be
loaded with the original Gemma base model.
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List

import torch
import yaml
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    set_seed,
)
from trl import SFTTrainer


def load_config(path: Path) -> Dict[str, Any]:
    """Load a YAML training config."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def dtype_from_name(name: str) -> torch.dtype:
    """Resolve a torch dtype from config text."""
    normalized = str(name).lower()
    if normalized in {"bf16", "bfloat16", "torch.bfloat16"}:
        return torch.bfloat16
    if normalized in {"fp16", "float16", "torch.float16"}:
        return torch.float16
    if normalized in {"fp32", "float32", "torch.float32"}:
        return torch.float32
    raise ValueError(f"Unsupported dtype: {name}")


def read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    """Read JSONL records."""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def messages_to_text(tokenizer: AutoTokenizer, messages: List[Dict[str, str]]) -> str:
    """Apply the model chat template to one SFT message list."""
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
        return tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )

    rendered = []
    for message in messages:
        rendered.append(f"{message['role'].upper()}: {message['content']}")
    return "\n".join(rendered) + tokenizer.eos_token


def load_sft_dataset(path: Path, tokenizer: AutoTokenizer) -> Dataset:
    """Load SFT JSONL.

    Supports either:
    - model-neutral records with `messages`
    - preformatted records with a Gemma-rendered `text` field
    """
    rows = []
    for record in read_jsonl(path):
        text = record.get("text")
        if text is None:
            text = messages_to_text(tokenizer, record["messages"])
        rows.append(
            {
                "paper_id": record["paper_id"],
                "task": record["task"],
                "text": text,
            }
        )
    return Dataset.from_list(rows)


def build_quantization_config(config: Dict[str, Any]) -> BitsAndBytesConfig:
    """Build bitsandbytes 4-bit config."""
    quant = config["quantization"]
    compute_dtype = dtype_from_name(quant.get("bnb_4bit_compute_dtype", "bfloat16"))
    return BitsAndBytesConfig(
        load_in_4bit=bool(quant.get("load_in_4bit", True)),
        bnb_4bit_quant_type=quant.get("bnb_4bit_quant_type", "nf4"),
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_use_double_quant=bool(quant.get("bnb_4bit_use_double_quant", True)),
    )


def build_lora_config(config: Dict[str, Any]) -> LoraConfig:
    """Build PEFT LoRA config."""
    lora = config["lora"]
    return LoraConfig(
        r=int(lora["r"]),
        lora_alpha=int(lora["lora_alpha"]),
        lora_dropout=float(lora["lora_dropout"]),
        bias=lora.get("bias", "none"),
        task_type=lora.get("task_type", "CAUSAL_LM"),
        target_modules=list(lora["target_modules"]),
    )


def load_model_and_tokenizer(config: Dict[str, Any]) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load the quantized base model and tokenizer."""
    model_config = config["model"]
    model_name = model_config["base_model"]
    torch_dtype = dtype_from_name(model_config.get("torch_dtype", "bfloat16"))
    quantization_config = build_quantization_config(config)

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=bool(model_config.get("trust_remote_code", False)),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map="auto",
        torch_dtype=torch_dtype,
        trust_remote_code=bool(model_config.get("trust_remote_code", False)),
        attn_implementation=model_config.get("attn_implementation", "eager"),
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(
        model,
        use_gradient_checkpointing=bool(config["training"].get("gradient_checkpointing", True)),
    )
    return model, tokenizer


def build_training_args(config: Dict[str, Any]) -> TrainingArguments:
    """Build Hugging Face training arguments."""
    training = config["training"]
    output = config["output"]
    output_dir = output["output_dir"]

    kwargs = {
        "output_dir": output_dir,
        "run_name": config.get("run_name"),
        "num_train_epochs": training["num_train_epochs"],
        "per_device_train_batch_size": training["per_device_train_batch_size"],
        "per_device_eval_batch_size": training["per_device_eval_batch_size"],
        "gradient_accumulation_steps": training["gradient_accumulation_steps"],
        "learning_rate": training["learning_rate"],
        "lr_scheduler_type": training["lr_scheduler_type"],
        "warmup_ratio": training["warmup_ratio"],
        "weight_decay": training["weight_decay"],
        "optim": training["optim"],
        "logging_steps": training["logging_steps"],
        "eval_steps": training["eval_steps"],
        "save_steps": training["save_steps"],
        "save_total_limit": output.get("save_total_limit", 2),
        "bf16": bool(training.get("bf16", False)),
        "fp16": bool(training.get("fp16", False)),
        "gradient_checkpointing": bool(training.get("gradient_checkpointing", True)),
        "max_grad_norm": training.get("max_grad_norm", 0.3),
        "report_to": training.get("report_to", []),
        "seed": training.get("seed", 42),
        "remove_unused_columns": False,
        "push_to_hub": bool(output.get("push_to_hub", False)),
        "hub_model_id": output.get("hub_model_id"),
    }

    eval_strategy = training.get("eval_strategy", "steps")
    save_strategy = training.get("save_strategy", "steps")
    try:
        return TrainingArguments(
            eval_strategy=eval_strategy,
            save_strategy=save_strategy,
            **kwargs,
        )
    except TypeError:
        return TrainingArguments(
            evaluation_strategy=eval_strategy,
            save_strategy=save_strategy,
            **kwargs,
        )


def train(config: Dict[str, Any]) -> None:
    """Run QLoRA training and save adapter artifacts."""
    set_seed(int(config["training"].get("seed", 42)))
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model_and_tokenizer(config)
    train_dataset = load_sft_dataset(Path(config["data"]["train_file"]), tokenizer)
    eval_dataset = load_sft_dataset(Path(config["data"]["eval_file"]), tokenizer)
    lora_config = build_lora_config(config)
    training_args = build_training_args(config)
    max_seq_length = int(config["data"].get("max_seq_length", 2048))

    try:
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            peft_config=lora_config,
            dataset_text_field="text",
            max_seq_length=max_seq_length,
            tokenizer=tokenizer,
            packing=False,
        )
    except TypeError:
        # Fallback for TRL/HF combinations where SFTTrainer signatures changed.
        def tokenize(batch: Dict[str, List[str]]) -> Dict[str, Any]:
            return tokenizer(
                batch["text"],
                truncation=True,
                max_length=max_seq_length,
                padding=False,
            )

        train_tokenized = train_dataset.map(
            tokenize,
            batched=True,
            remove_columns=train_dataset.column_names,
            num_proc=int(config["data"].get("preprocessing_num_workers", 1)),
        )
        eval_tokenized = eval_dataset.map(
            tokenize,
            batched=True,
            remove_columns=eval_dataset.column_names,
            num_proc=int(config["data"].get("preprocessing_num_workers", 1)),
        )
        from peft import get_peft_model

        model = get_peft_model(model, lora_config)
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_tokenized,
            eval_dataset=eval_tokenized,
            tokenizer=tokenizer,
            data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
        )

    train_result = trainer.train()
    trainer.save_model(str(output_dir / "adapter"))
    tokenizer.save_pretrained(str(output_dir / "adapter"))

    metrics = train_result.metrics
    metrics["train_samples"] = len(train_dataset)
    metrics["eval_samples"] = len(eval_dataset)
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)
    trainer.save_state()

    eval_metrics = trainer.evaluate()
    eval_metrics["eval_samples"] = len(eval_dataset)
    trainer.log_metrics("eval", eval_metrics)
    trainer.save_metrics("eval", eval_metrics)

    with (output_dir / "training_config.json").open("w", encoding="utf-8") as handle:
        json.dump(config, handle, indent=2, sort_keys=True)

    print(f"Saved adapter and metrics to {output_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Train Gemma QLoRA adapter for Ask Physics.")
    parser.add_argument("--config", default="training/configs/gemma_qlora.yaml")
    args = parser.parse_args()

    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    config = load_config(Path(args.config))
    train(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
