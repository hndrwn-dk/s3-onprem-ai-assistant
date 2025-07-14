# convert_json_to_txt.py - v1.0
import os
import json

SOURCE_DIR = "docs"
TARGET_SUFFIX = "_converted.txt"

def convert_json_to_txt():
    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith(".json"):
            json_path = os.path.join(SOURCE_DIR, filename)
            txt_path = os.path.join(SOURCE_DIR, filename.replace(".json", TARGET_SUFFIX))

            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                with open(txt_path, "w", encoding="utf-8") as out:
                    for i, entry in enumerate(data):
                        out.write(f"Entry {i + 1}:\n")
                        for key, value in entry.items():
                            out.write(f"{key}: {value}\n")
                        out.write("\n---\n\n")

                print(f"[OK] {filename} → {os.path.basename(txt_path)}")
            except Exception as e:
                print(f"[ERROR] Failed to convert {filename}: {e}")

if __name__ == "__main__":
    convert_json_to_txt()