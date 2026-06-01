# Ask Physics Plasma Measurement Extraction Dataset

## Dataset Summary

This dataset prepares Ask Physics paper abstracts for QLoRA fine-tuning of an open model such as Gemma or Mistral.

The task is narrow: extract plasma physics measurements from titles and abstracts into strict JSON that can later be converted to RDF/SPARQL-ready knowledge graph records.

## Current Version

- Dataset version: `v0.1-bronze`
- Label provenance: regex-generated weak labels
- Source: arXiv metadata and abstracts
- Task: abstract measurement extraction
- Output format: chat-style SFT JSONL

See `training/reports/dataset_report.md` for current counts.

## Intended Use

Use this dataset for:

- QLoRA smoke fine-tuning experiments.
- Comparing Gemma/Mistral adapters against regex extraction.
- Building a teacher-label and manual-review workflow.
- Testing strict JSON generation for scientific extraction.

Do not use the bronze labels alone for final claims about extraction quality.

## Data Sources

Raw records are collected from arXiv using targeted plasma physics queries in:

```text
training/queries/plasma_measurement_queries.txt
```

Each raw record stores:

- arXiv ID
- title
- abstract
- authors
- publication/update dates
- categories
- source URL
- PDF URL
- query provenance

## Label Schema

Each extraction label has:

```json
{
  "measurements": [
    {
      "type": "temperature",
      "value": 100.0,
      "unit": "keV",
      "normalized_value": 100.0,
      "normalized_unit": "keV",
      "context": "...",
      "confidence": 0.65
    }
  ]
}
```

Supported measurement types in v0.1:

- `temperature`
- `density`

## Dataset Levels

- `raw`: arXiv metadata and abstracts.
- `bronze`: regex-generated weak labels.
- `silver`: planned teacher-model labels.
- `gold`: manually reviewed examples for evaluation.
- `sft`: model-neutral chat records for QLoRA.

## Known Limitations

- Bronze labels are noisy and incomplete.
- Temperature extraction can include false positives from non-plasma energy references.
- Density extraction is improving but still underrepresented.
- Abstract-only extraction misses measurements that appear only in full papers.
- No manual gold labels are included until `training/data/gold/review_queue.jsonl` is reviewed.

## License And Redistribution Notes

The dataset stores arXiv metadata and abstracts with source URLs and provenance. Avoid redistributing full PDFs or full text unless the paper license permits it.

Before publishing a public dataset release, verify the final license policy for included metadata, abstracts, generated labels, and any teacher-model outputs.
