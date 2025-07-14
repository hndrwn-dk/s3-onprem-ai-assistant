# s3ai_query_v1.8.py
import sys
from utils import load_embeddings, query_llm, query_json, search_txt_documents, save_question

def main():
    if len(sys.argv) < 2:
        print("Usage: python s3ai_query_v1.8.py <your question>")
        sys.exit(1)

    query = " ".join(sys.argv[1:]).strip()
    save_question(query)

    # Step 1: Vector search
    try:
        vectorstore = load_embeddings()
        answer = query_llm(query, vectorstore)
    except Exception as e:
        answer = f"[Vector Load Error] {e}"

    print("Answer:\n", answer)

    # Step 2: If vector search fails or gives no useful answer, check JSON
    if "No result found" in answer or "No metadata match found" in answer or "helpful assistant" in answer:
        json_result = query_json(query)
        if json_result:
            print("\n[JSON Metadata Fallback Result]\n", json_result)
            return

    # Step 3: Fallback to flat .txt files
    txt_matches = search_txt_documents(query)
    if txt_matches:
        print("\n[TXT Fallback Matches Found]")
        for fname, snippet in txt_matches:
            print(f"\nFile: {fname}\n---\n{snippet.strip()}\n---")
    else:
        print("\nNo metadata match found.")

if __name__ == "__main__":
    main()
