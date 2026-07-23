# Reference Schemas

## Evals Schema

```json
{
  "skill_name": "string",
  "evals": [
    {
      "id": "number",
      "prompt": "string",
      "expected_behavior": ["array of required observable behaviors"],
      "files": ["array of file paths"]
    }
  ]
}
```

## Grading Schema

```json
{
  "eval_id": "number",
  "eval_name": "string",
  "grades": [
    {
      "criterion": "string",
      "score": "number (0-100)",
      "feedback": "string"
    }
  ],
  "final_grade": "string (A-F)",
  "summary": "string"
}
```

## Report Metadata Schema

```json
{
  "report_type": "fault|change|operation|security",
  "date": "YYYY-MM-DD",
  "time_range": "HH:MM - HH:MM",
  "severity": "P0-P3 or 严重/高/中/低",
  "affected_systems": ["array of systems"],
  "report_author": "string",
  "data_sources": [
    {
      "type": "string",
      "command": "string",
      "output_location": "string",
      "description": "string"
    }
  ]
}
```
