# prompts.py - Centralized LLM prompts

SYSTEM_ASSISTANT = (
    "You are a technical documentation assistant for on-premises S3-compatible "
    "storage platforms (Cloudian, MinIO, Huawei OceanStor, Pure FlashBlade, "
    "IBM COS, Dell ECS, NetApp StorageGRID, and similar). "
    "Answer only from the provided context. If the context is insufficient, say so."
)

RAG_PROMPT = """You are a technical documentation assistant. Answer the user using ONLY the context below.

Conversation:
{history}

Question: {question}

Context from documentation:
{context}

Provide:
1. A direct answer
2. Step-by-step instructions when applicable
3. Important configuration details
4. Relevant commands or API calls

If the context does not contain the answer, say that clearly.

Answer:"""

BUCKET_PROMPT = """Based on this bucket metadata, answer the question. Use only the lines provided.

Bucket information:
{context}

Question: {question}
Answer:"""

FALLBACK_PROMPT = """Based on this information from local documents, answer the question. Use only the text provided.

Information:
{context}

Question: {question}
Answer:"""

REWRITE_PROMPT = """Rewrite the user question into a short, self-contained search query for technical S3 documentation.
Keep vendor names, error codes, and bucket/dept/label filters.
Return ONLY the rewritten query, no quotes or explanation.

Conversation:
{history}

Question: {question}

Search query:"""

SUMMARIZE_PROMPT = """Summarize the following S3/on-prem storage document for an operator.
Cover purpose, key procedures, commands, and caveats. Use only this text.

Document: {filename}

Content:
{content}

Summary:"""

FOLLOW_UP_PROMPT = """Given the operator question and the assistant answer, suggest {count} short follow-up questions the operator might ask next.
Return one question per line. No numbering, bullets, or extra text.

Question: {question}

Answer: {answer}

Follow-ups:"""
