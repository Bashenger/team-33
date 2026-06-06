# ⚡ ContextSwitch AI
> **Stateful Multi-Mode Orchestration Engine** > *Developed for Department of Computer Science | Sponsored INNOVATION SPRINT 2026*

ContextSwitch AI is an enterprise-grade AI assistant designed to solve corporate data isolation challenges. It features a stateful, multi-mode architecture that seamlessly shifts its execution environment between direct cloud LLM generation and a completely secure, isolated **Retrieval-Augmented Generation (RAG)** pipeline depending on the user's operational intent.

---

## 🛠️ Architecture & Core Components

The platform unifies three distinct software layers built seamlessly across our core development scrum team:

### 1. High-Fidelity UI Console (`app.py`)
* Implements a premium, dark-slate developer dashboard layout utilizing custom injected glassmorphism CSS layers.
* Features a stable, bottom-docked conversational chat utility with integrated live telemetry monitors.
* Dynamically manages system status diagnostics overlays that open during pipeline calculations.

### 2. Transaction Routing & Memory Management (`router.py` & `memory_db.py`)
* **Intent Routing Engine:** Intercepts real-time queries and processes strings to determine whether to execute high-speed general chat or isolate text tracking into local secure vectors.
* **Stateful SQLite Ledger Store:** Moves beyond volatile browser cache. Every user interaction prompt, system badge state, and token array chunk is written persistently to a local SQLite database (`chat_memory.db`).

### 3. Open-Source Local Knowledge Base (`rag_retriever.py`)
* Operates an offline embedding framework utilizing the state-of-the-art **`BAAI/bge-small-en-v1.5`** deep learning model to compile documents into local filesystems.
* Automatically ingests, segments, and indexes unstructured corporate documentation arrays (`.txt`, `.pdf`, `.docx`) into a local **`ChromaDB`** vector store instance.

---

## 🛰️ Technical Stack & Dependencies

* **Frontend Layout:** Streamlit (v1.35+)
* **Inference Cloud Infrastructure:** Groq Cloud API (`Llama 3.1 8B Instruct Engine`)
* **Orchestration Framework:** LangChain (Core & Community)
* **Vector Vector Store Engine:** ChromaDB
* **Local Embeddings Network:** Hugging Face Transformers (`BAAI/bge-small-en-v1.5`)
* **Stateful Database Layer:** SQLite3

---

## 🚀 Step-by-Step Installation & Local Setup

### 1. Clone the Workspace Repository
```bash
git clone [https://github.com/Bashenger/Hackathon.git](https://github.com/Bashenger/Hackathon.git)
cd Hackathon
