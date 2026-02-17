#!/usr/bin/env python3
"""
Example: Import HuggingFace datasets to Coval test sets.

Demonstrates transforming various HuggingFace dataset formats
into Coval-compatible CSVs with proper structure.

Supported patterns:
- Multiple choice (MMLU, CommonsenseQA)
- Math word problems (GSM8K)
- Reading comprehension (DROP)
"""

import csv
import json
from pathlib import Path


def transform_to_coval_csv(
    records: list[dict],
    input_field: str,
    output_path: Path,
    source_name: str,
    metadata_fields: list[str] | None = None,
    category_field: str | None = None,
) -> dict[str, Path]:
    """
    Transform HuggingFace records to Coval CSV format.

    Args:
        records: List of records from HuggingFace dataset
        input_field: Field name containing the prompt/question
        output_path: Directory to write CSVs
        source_name: Name of the source dataset
        metadata_fields: Fields to preserve in metadata JSON
        category_field: Field to use for categorizing into separate CSVs

    Returns:
        Dict mapping category names to output file paths
    """
    output_path.mkdir(parents=True, exist_ok=True)
    metadata_fields = metadata_fields or []

    # Group by category if specified
    by_category: dict[str, list] = {}
    for record in records:
        category = record.get(category_field, "all") if category_field else "all"
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(record)

    output_files = {}

    for category, category_records in by_category.items():
        filename = f"{source_name}_{category}.csv" if category != "all" else f"{source_name}.csv"
        filepath = output_path / filename

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(["input", "metadata"])

            for record in category_records:
                input_text = record.get(input_field, "")
                if not input_text:
                    continue

                # Build metadata
                metadata = {"source": source_name}
                for field in metadata_fields:
                    if field in record:
                        metadata[field] = record[field]

                writer.writerow([input_text, json.dumps(metadata)])

        output_files[category] = filepath
        print(f"Created: {filepath} ({len(category_records)} test cases)")

    return output_files


# =============================================================================
# Example: MMLU (Multiple Choice)
# Dataset: cais/mmlu
# =============================================================================

MMLU_SAMPLE = [
    {
        "question": "What is the capital of France?",
        "choices": ["London", "Berlin", "Paris", "Madrid"],
        "answer": "C",
        "subject": "geography",
    },
    {
        "question": "Which element has atomic number 6?",
        "choices": ["Nitrogen", "Carbon", "Oxygen", "Boron"],
        "answer": "B",
        "subject": "chemistry",
    },
]


def format_mmlu_question(record: dict) -> str:
    """Format MMLU record as a complete question with choices."""
    question = record["question"]
    choices = record["choices"]
    formatted = f"{question}\n\n"
    for i, choice in enumerate(choices):
        formatted += f"{chr(65 + i)}. {choice}\n"
    return formatted.strip()


# =============================================================================
# Example: GSM8K (Math Word Problems)
# Dataset: openai/gsm8k
# =============================================================================

GSM8K_SAMPLE = [
    {
        "question": "Janet's ducks lay 16 eggs per day. She eats 3 for breakfast and uses 4 to bake muffins. She sells the rest at $2 each. How much does she make per day?",
        "answer": "Janet sells 16 - 3 - 4 = 9 eggs per day.\nShe makes 9 * 2 = $18 per day.\n#### 18",
    },
    {
        "question": "A store sold 120 books on Monday. On Tuesday, they sold twice as many. How many books did they sell in total?",
        "answer": "Tuesday sales: 120 * 2 = 240 books.\nTotal: 120 + 240 = 360 books.\n#### 360",
    },
]


# =============================================================================
# Example: CommonsenseQA
# Dataset: tau/commonsense_qa
# =============================================================================

COMMONSENSE_QA_SAMPLE = [
    {
        "id": "q1",
        "question": "Where would you put a plate after eating?",
        "choices": {
            "label": ["A", "B", "C", "D", "E"],
            "text": ["refrigerator", "dishwasher", "table", "floor", "window"],
        },
        "answerKey": "B",
    },
]


def format_commonsense_qa(record: dict) -> str:
    """Format CommonsenseQA record with choices."""
    question = record["question"]
    labels = record["choices"]["label"]
    texts = record["choices"]["text"]
    formatted = f"{question}\n\n"
    for label, text in zip(labels, texts):
        formatted += f"{label}. {text}\n"
    return formatted.strip()


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    output_dir = Path("./coval_test_sets")

    # Example 1: MMLU with category separation by subject
    print("=== MMLU ===")
    mmlu_records = [
        {"input": format_mmlu_question(r), "subject": r["subject"], "answer": r["answer"]}
        for r in MMLU_SAMPLE
    ]
    transform_to_coval_csv(
        records=mmlu_records,
        input_field="input",
        output_path=output_dir,
        source_name="mmlu",
        metadata_fields=["answer", "subject"],
        category_field="subject",
    )

    # Example 2: GSM8K math problems (single category)
    print("\n=== GSM8K ===")
    gsm8k_records = [
        {"input": r["question"], "expected_answer": r["answer"].split("####")[-1].strip()}
        for r in GSM8K_SAMPLE
    ]
    transform_to_coval_csv(
        records=gsm8k_records,
        input_field="input",
        output_path=output_dir,
        source_name="gsm8k",
        metadata_fields=["expected_answer"],
    )

    # Example 3: CommonsenseQA
    print("\n=== CommonsenseQA ===")
    csqa_records = [
        {"input": format_commonsense_qa(r), "id": r["id"], "answer": r["answerKey"]}
        for r in COMMONSENSE_QA_SAMPLE
    ]
    transform_to_coval_csv(
        records=csqa_records,
        input_field="input",
        output_path=output_dir,
        source_name="commonsense_qa",
        metadata_fields=["id", "answer"],
    )

    print(f"\nGenerated CSVs in {output_dir}/")
