# flatten_json_to_txt.py - v1.0
import os
import json

SOURCE_JSON = "docs/bucket_metadata.json"
OUTPUT_TXT = "docs/bucket_metadata_flattened.txt"

def flatten_json_to_text():
    try:
        with open(SOURCE_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
            for entry in data:
                line = []
                for key, value in entry.items():
                    line.append(f"{key}: {value}")
                out.write(" | ".join(line) + "\n")
            print(f"[OK] Flattened to: {OUTPUT_TXT}")
    except Exception as e:
        print(f"[ERROR] Failed: {e}")

if __name__ == "__main__":
    flatten_json_to_text()
