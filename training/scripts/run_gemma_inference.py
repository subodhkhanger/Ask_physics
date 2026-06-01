#!/usr/bin/env python3
"""
Run inference with a Gemma base model plus an optional Ask Physics QLoRA adapter.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import yaml
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from train_gemma_qlora import dtype_from_name


SYSTEM_PROMPT = (
    "Extract plasma physics measurements from paper titles and abstracts. "
    "Return only valid JSON with a top-level measurements array. "
    "Each measurement must include type, value, unit, normalized_value, "
    "normalized_unit, context, and confidence. Return an empty array when "
    "no temperature or density measurement is present."
)


def load_config(path: Path) -> Dict[str, Any]:
    """Load YAML config."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def build_quantization_config(config: Dict[str, Any]) -> BitsAndBytesConfig:
    """Build bitsandbytes quantization config from training config."""
    quant = config["quantization"]
    return BitsAndBytesConfig(
        load_in_4bit=bool(quant.get("load_in_4bit", True)),
        bnb_4bit_quant_type=quant.get("bnb_4bit_quant_type", "nf4"),
        bnb_4bit_compute_dtype=dtype_from_name(quant.get("bnb_4bit_compute_dtype", "bfloat16")),
        bnb_4bit_use_double_quant=bool(quant.get("bnb_4bit_use_double_quant", True)),
    )


def load_model(config: Dict[str, Any], adapter_dir: Optional[str]) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load base model and optional PEFT adapter."""
    model_name = config["model"]["base_model"]
    tokenizer = AutoTokenizer.from_pretrained(adapter_dir or model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=build_quantization_config(config),
        device_map="auto",
        torch_dtype=dtype_from_name(config["model"].get("torch_dtype", "bfloat16")),
        trust_remote_code=bool(config["model"].get("trust_remote_code", False)),
        attn_implementation=config["model"].get("attn_implementation", "eager"),
    )
    if adapter_dir:
        model = PeftModel.from_pretrained(model, adapter_dir)
    model.eval()
    return model, tokenizer


def build_messages(title: str, abstract: str) -> List[Dict[str, str]]:
    """Build Ask Physics extraction prompt messages."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Title: {title}\nAbstract: {abstract}"},
    ]


def generate(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    messages: List[Dict[str, str]],
    max_new_tokens: int,
    temperature: float,
    top_p: float,
) -> str:
    """Generate assistant text."""
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    generation_kwargs = {
        "max_new_tokens": max_new_tokens,
        "pad_token_id": tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }
    if temperature > 0:
        generation_kwargs.update(
            {
                "do_sample": True,
                "temperature": temperature,
                "top_p": top_p,
            }
        )
    else:
        generation_kwargs["do_sample"] = False

    with torch.no_grad():
        output = model.generate(**inputs, **generation_kwargs)
    generated = output[0][inputs["input_ids"].shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Gemma QLoRA inference for Ask Physics.")
    parser.add_argument("--config", default="training/configs/gemma_qlora.yaml")
    parser.add_argument("--adapter-dir", default="training/runs/gemma-qlora-ask-physics/adapter")
    parser.add_argument("--title", required=True)
    parser.add_argument("--abstract", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=None)
    args = parser.parse_args()

    config = load_config(Path(args.config))
    generation = config.get("generation", {})
    model, tokenizer = load_model(config, args.adapter_dir)
    text = generate(
        model,
        tokenizer,
        build_messages(args.title, args.abstract),
        max_new_tokens=args.max_new_tokens or int(generation.get("max_new_tokens", 512)),
        temperature=float(generation.get("temperature", 0.0)),
        top_p=float(generation.get("top_p", 1.0)),
    )
    print(text)
    try:
        print(json.dumps(json.loads(text), indent=2, sort_keys=True))
    except json.JSONDecodeError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
