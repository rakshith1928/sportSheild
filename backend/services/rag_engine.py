import os
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from groq import Groq

# Global variables
rag_vectorstore = None
embeddings = None
groq_client = None

KNOWLEDGE_BASE_PATH = Path("knowledge_base/ip_laws")

def init_rag():
    global rag_vectorstore, embeddings, groq_client

    print("📚 Loading legal knowledge base...")

    # Init Groq client
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("⚠️ GROQ_API_KEY not set — explanations will be disabled")
    else:
        groq_client = Groq(api_key=groq_api_key)
        print("✅ Groq client initialized")

    # Load embeddings model
    print("🔤 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    # 1️⃣ FIX: Load existing DB instead of rebuilding every run
    rag_vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name="legal_knowledge"
    )

    existing_ids = rag_vectorstore.get()["ids"]
    if len(existing_ids) == 0:
        print("📄 Building knowledge base for first time...")
        _load_documents_into_db()
    else:
        print(f"✅ Knowledge base loaded from disk ({len(existing_ids)} chunks)")


def _load_documents_into_db():
    """Load legal documents into ChromaDB — only called once"""
    if not KNOWLEDGE_BASE_PATH.exists():
        print(f"⚠️ Knowledge base path not found: {KNOWLEDGE_BASE_PATH}")
        return

    documents = []
    for file_path in KNOWLEDGE_BASE_PATH.glob("*.txt"):
        print(f"📄 Loading: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "law": file_path.stem
                }
            ))

    if not documents:
        print("⚠️ No documents found in knowledge base")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"📝 Created {len(chunks)} chunks from {len(documents)} documents")

    rag_vectorstore.add_documents(chunks)
    rag_vectorstore.persist()
    print(f"✅ RAG knowledge base built and saved with {len(chunks)} chunks!")


def query_rag(query: str, k: int = 3, law_filter: str = None) -> list:
    """Search knowledge base for relevant legal context with scores"""
    if rag_vectorstore is None:
        return []

    # 3️⃣ FIX: Optional metadata filtering by law type
    search_kwargs = {"k": k}
    if law_filter:
        search_kwargs["filter"] = {"law": law_filter}

    # 1️⃣ FIX: Use similarity_search_with_score to get relevance scores
    results = rag_vectorstore.similarity_search_with_score(query, **search_kwargs)

    filtered = []
    for doc, score in results:
        # Chroma returns L2 distance — lower = more similar
        # Convert to 0-1 similarity: 1 = perfect match
        similarity = 1 / (1 + score)

        # 1️⃣ FIX: Filter out low-relevance chunks
        if similarity < 0.4:
            print(f"⚠️ Skipping low-relevance chunk (score={score:.3f}): {doc.page_content[:60]}...")
            continue

        filtered.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "law": doc.metadata.get("law", "unknown"),
            "relevance_score": round(similarity, 3)
        })

    return filtered


def explain_violation(violation: dict) -> dict:
    """Use RAG + Groq LLM to explain a violation and recommend legal actions"""

    similarity = violation.get("clip_similarity", 0)
    is_copy = violation.get("is_likely_copy", False)

    # 4️⃣ FIX: Confidence score
    confidence = round(similarity * 100, 2)

    # Severity logic
    if similarity > 0.92 and is_copy:
        severity = "HIGH"
    elif similarity > 0.85:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # Rich query for better retrieval
    query = f"""
    sports copyright infringement
    unauthorized broadcasting
    pirated sports content
    similarity score {similarity}
    likely copied media content
    DMCA violation streaming or reposting
    source url {violation.get('page_url', '')}
    """

    # 3️⃣ FIX: Use targeted law filter based on severity
    # HIGH violations → check DMCA first (faster takedowns)
    # others → search all laws
    law_filter = "dmca" if severity == "HIGH" else None
    legal_context = query_rag(query, k=3, law_filter=law_filter)

    # 3️⃣ FIX: If filtered retrieval returned nothing, fall back to unfiltered
    if not legal_context:
        print("⚠️ Filtered search returned nothing — falling back to unfiltered")
        legal_context = query_rag(query, k=3)

    # Limit context size
    legal_context = legal_context[:2]

    if not legal_context:
        context_text = "No specific legal context found."
    else:
        context_text = "\n\n".join([
            f"[{ctx['source']} | relevance: {ctx['relevance_score']}]:\n{ctx['content']}"
            for ctx in legal_context
        ])

    # Fallback if Groq not configured
    if groq_client is None:
        return {
            "explanation": _fallback_explanation(severity),
            "severity": severity,
            "confidence": confidence,
            "legal_context": legal_context,
            "recommended_action": get_recommended_action(severity)
        }

    # Grounded prompt with structured output
    prompt = f"""You are a legal advisor specializing in digital media copyright and sports broadcasting rights.

A potential copyright violation has been detected:
- Page URL: {violation.get('page_url', 'Unknown')}
- Similarity Score: {similarity} ({confidence}% confidence)
- Severity: {severity}
- Is Likely Copy: {is_copy}
- Detected At: {violation.get('detected_at', 'Unknown')}

Relevant Legal Context:
{context_text}

IMPORTANT: Only use the provided legal context above. Do not invent laws or facts not mentioned.

Provide your response in exactly this format:

Law Violated:
[Name the specific law and section from the context]

Why Harmful:
[1-2 sentences on impact to rights holder]

Severity:
[{severity} — one sentence reason]

Recommended Action:
[Most important immediate step]

Takedown Process:
[Specific platform or legal filing step]"""

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "You are a legal advisor for digital sports media copyright protection. Only use facts from the provided context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=400,
            temperature=0.3
        )
        explanation = response.choices[0].message.content

    except Exception as e:
        print(f"⚠️ Groq call failed: {e}")
        explanation = _fallback_explanation(severity)

    return {
        "explanation": explanation,
        "severity": severity,
        "confidence": confidence,
        "legal_context": legal_context,
        "recommended_action": get_recommended_action(severity)
    }

def _fallback_explanation(severity: str) -> str:
    """Structured fallback explanation when LLM is unavailable"""
    return f"""Law Violated:
Potential violation of DMCA Section 512 and/or Indian Copyright Act Section 51 — unauthorized reproduction or distribution of protected sports media.

Why Harmful:
Unauthorized use deprives the rights holder of licensing revenue and control over their intellectual property.

Severity:
{severity} — based on visual similarity score and copy detection analysis.

Recommended Action:
{get_recommended_action(severity)}

Takedown Process:
File a DMCA takedown notice with the hosting platform via their designated copyright agent or online reporting tool."""


def get_recommended_action(severity: str) -> str:
    actions = {
        "LOW": "Monitor the URL and send an informal cease and desist email to the site owner.",
        "MEDIUM": "File a platform takedown notice (YouTube/Instagram/Twitter) and send a formal cease and desist letter.",
        "HIGH": "File a DMCA takedown immediately, notify your legal team, and consider pursuing civil damages."
    }
    return actions.get(severity, "Monitor and assess further.")