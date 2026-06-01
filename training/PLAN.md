# QLoRA Data Collection Plan

## Objective

Create a reproducible open-source dataset for fine-tuning Gemma, Mistral, or another open model to extract plasma physics measurements for Ask Physics.

## Milestone 1: Raw Metadata Collection

Source arXiv paper metadata and abstracts from plasma-related categories and search queries.

Default queries:

- `cat:physics.plasm-ph`
- `all:tokamak`
- `all:stellarator`
- `all:"fusion plasma"`
- `all:"electron temperature"`
- `all:"electron density"`
- `all:"plasma density"`

Artifact:

```text
training/data/raw/arxiv_metadata.jsonl
```

Acceptance criteria:

- Every row has `paper_id`, `title`, `abstract`, `authors`, `published`, `categories`, `source_url`, and `provenance`.
- Records are deduplicated by `paper_id`.
- Collection can run with a small limit for repeatable testing.

## Milestone 2: Bronze Labels

Run deterministic regex extraction against each abstract.

Artifact:

```text
training/data/bronze/regex_labels.jsonl
```

Acceptance criteria:

- Every row has an extraction schema version.
- Empty measurement examples are retained as negative examples.
- Labels include context snippets and normalized units where possible.
- Label provenance is `regex`.

## Milestone 3: Extraction SFT Dataset

Convert labels into chat-style supervised fine-tuning records.

Artifacts:

```text
training/data/sft/train.jsonl
training/data/sft/dev.jsonl
training/data/sft/test.jsonl
```

Acceptance criteria:

- Splits are deterministic.
- Splits are by `paper_id`.
- Assistant output is strict JSON.
- Dataset remains model-neutral for Gemma and Mistral.

## Milestone 3b: Query Parsing SFT Dataset

Convert natural-language search queries into structured JSON compatible with
`backend.nlp_query_processor.ParsedQuery`.

Artifacts:

```text
training/data/query_parsing/train.jsonl
training/data/query_parsing/dev.jsonl
training/data/query_parsing/test.jsonl
```

Acceptance criteria:

- Covers keyword-only search, temporal constraints, temperature ranges, density ranges, combined temperature+density filters, and statistics intents.
- Assistant output is strict JSON with `intent`, `parameters`, `keywords`, `temporal_constraint`, and `confidence`.
- Uses `example_id` records instead of `paper_id` because examples are query-level rather than paper-level.
- Dataset remains model-neutral for Gemma and Mistral.
- The default generator writes a stratified 3,000-example split for v0.1 fine-tuning.

## Milestone 4: Silver Labels

Add a teacher-model labeling script after the bronze dataset is stable.

Artifact:

```text
training/data/silver/teacher_labels.jsonl
```

Acceptance criteria:

- Teacher labels are schema-valid.
- Teacher output keeps evidence context.
- Teacher labels can be compared against bronze labels.
- Cost and model name are recorded in provenance.

## Milestone 5: Gold Evaluation Set

Manually review a small high-quality evaluation set.

Artifact:

```text
training/data/gold/reviewed_labels.jsonl
```

Acceptance criteria:

- At least 200 reviewed examples for v0.1.
- Contains positive and negative examples.
- Contains unit conversion edge cases.
- Never train on gold evaluation rows.

## Milestone 6: QLoRA Training

Add training scripts only after the SFT dataset is validated.

Future files:

```text
training/scripts/train_qlora.py
training/scripts/evaluate_extraction.py
training/configs/gemma_qlora.yaml
training/configs/gemma_query_parsing_qlora.yaml
training/configs/mistral_qlora.yaml
```

Acceptance criteria:

- Gemma and Mistral use the same base SFT dataset.
- Training applies the model-specific chat template at runtime.
- Evaluation compares regex, OpenAI/teacher, and local adapter outputs.
