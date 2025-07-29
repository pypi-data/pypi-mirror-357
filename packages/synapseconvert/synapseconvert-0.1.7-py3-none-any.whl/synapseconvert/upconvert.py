import pandas as pd
import json
import argparse
import sys


def upconvert(input_path: str, output_path: str):
    try:
        df = pd.read_excel(input_path)
    except FileNotFoundError:
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    collection_name = df["collection"].iloc[0] if "collection" in df.columns else "Unnamed Collection"
    categories = {}

    for _, row in df.iterrows():
        if "category" not in row or pd.isna(row["category"]):
            continue

        cat = row["category"]
        item = row.drop(labels=["collection", "category"],
                        errors="ignore").dropna().to_dict()

        if "tags" in item and isinstance(item["tags"], str):
            try:
                item["tags"] = json.loads(item["tags"].replace("'", '"'))
            except json.JSONDecodeError:
                item["tags"] = []

        categories.setdefault(cat, []).append(item)

    collection = {
        "Collection": {
            "name": collection_name,
            "designator": "BST",
            "url": "https://thebiblicalstory.org",
            "Categories": [{"name": k, "items": v} for k, v in categories.items()]
        }
    }

    with open(output_path, "w") as f:
        json.dump(collection, f, indent=2)

    print(f"✅ Upconverted {input_path} to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Synapse-format Excel file to JSON."
    )
    parser.add_argument("input", help="Path to input Excel file")
    parser.add_argument("output", help="Path to output JSON file")
    args = parser.parse_args()

    upconvert(args.input, args.output)


if __name__ == "__main__":
    main()
