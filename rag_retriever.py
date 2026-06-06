import os
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Dependencies check to guide you/your teammate during setup:
# pip install langchain-chroma langchain-community unstructured[pdf] sentence-transformers

DB_DIR = os.path.join(os.getcwd(), "chroma_db")
DATA_DIR = os.path.join(os.getcwd(), "data")


@st.cache_resource
def get_embeddings_engine():
    """Loads and caches the local BGE embedding model weights onto CPU."""
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={"normalize_embeddings": True}
    )


def _get_data_file_list() -> list[str]:
    """Returns a sorted list of supported files currently in the data directory."""
    supported_extensions = (".txt", ".pdf", ".docx", ".md")
    if not os.path.exists(DATA_DIR):
        return []
    return sorted([
        f for f in os.listdir(DATA_DIR)
        if f.endswith(supported_extensions) and not f.startswith(".")
    ])


def _chroma_is_stale() -> bool:
    """
    Returns True if the ChromaDB on disk was built from a different set of files
    than what currently exists in /data — so we know to rebuild.
    Uses a simple manifest file as a checksum.
    """
    manifest_path = os.path.join(DB_DIR, "_manifest.txt")
    current_files = _get_data_file_list()
    current_manifest = "\n".join(current_files)

    if not os.path.exists(manifest_path):
        return True  # No manifest → treat as stale

    with open(manifest_path, "r") as f:
        saved_manifest = f.read()

    return saved_manifest.strip() != current_manifest.strip()


def _write_manifest():
    """Saves a manifest of the current /data file list into the ChromaDB directory."""
    os.makedirs(DB_DIR, exist_ok=True)
    manifest_path = os.path.join(DB_DIR, "_manifest.txt")
    current_files = _get_data_file_list()
    with open(manifest_path, "w") as f:
        f.write("\n".join(current_files))


def build_or_load_vector_db():
    """
    Ingests all files inside the /data directory using Unstructured,
    chunks them, embeds them with BGE, and saves/loads a persistent ChromaDB instance.

    FIX: Added stale-check so that newly uploaded files trigger a rebuild instead
    of silently serving the old index.
    """
    embeddings = get_embeddings_engine()

    os.makedirs(DATA_DIR, exist_ok=True)

    files = _get_data_file_list()

    if not files:
        # No documents uploaded at all
        return None

    # FIX: Load existing ChromaDB ONLY if it's not stale (i.e. file list hasn't changed)
    if os.path.exists(DB_DIR) and len(os.listdir(DB_DIR)) > 0 and not _chroma_is_stale():
        return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

    # Otherwise rebuild the index from scratch
    from langchain_community.document_loaders import UnstructuredFileLoader
    import shutil

    # Wipe old stale index before rebuilding
    if os.path.exists(DB_DIR):
        shutil.rmtree(DB_DIR)

    all_docs = []

    for file_name in files:
        file_path = os.path.join(DATA_DIR, file_name)
        try:
            loader = UnstructuredFileLoader(file_path)
            loaded_documents = loader.load()
            for d in loaded_documents:
                d.metadata["source"] = file_name
            all_docs.extend(loaded_documents)
        except Exception as e:
            print(f"Skipping corrupt or unreadable file {file_name}: {e}")

    if not all_docs:
        return None

    # Chunk documents with a sliding window
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_docs)

    # Build and persist ChromaDB
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )

    # Save manifest so future calls know this index is up to date
    _write_manifest()

    return vector_db


def retrieve_enterprise_docs(query: str) -> dict:
    """
    CONTRACT 1 FUNCTION:
    Accepts: A raw user query string.
    Returns: A dictionary with a compiled string context block and a list of file sources.
    """
    # 1. Initialize or connect to the persistent ChromaDB matrix
    vector_db = build_or_load_vector_db()

    # Fallback if no documents are loaded
    if vector_db is None:
        return {
            "context": (
                "No documents found. Please upload company policy files using the "
                "ENTERPRISE KNOWLEDGE SOURCE INGESTION LAYER panel."
            ),
            "sources": ["No Documents Loaded"]
        }

    # 2. Query ChromaDB for the top 3 closest semantic matches
    # FIX: Increased k from 2 → 3 for better recall on longer documents
    try:
        matched_chunks = vector_db.similarity_search(query, k=3)
    except Exception as e:
        return {
            "context": f"Vector search error: {str(e)}",
            "sources": ["Search Error"]
        }

    if not matched_chunks:
        return {
            "context": "No relevant content found in the uploaded documents for this query.",
            "sources": ["No Matches Found"]
        }

    # 3. Format the context block and extract unique metadata document sources
    context_string = "\n\n".join([chunk.page_content for chunk in matched_chunks])
    sources_list = list(set([
        chunk.metadata.get("source", "Unknown File")
        for chunk in matched_chunks
    ]))

    return {
        "context": context_string,
        "sources": sources_list
    }