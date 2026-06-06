import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

# Import backend modules from your teammates
import memory_db as member2_db
import router as member2_router  # <-- Imported Member 2's Router here!

# ==========================================
# 1. Environment & Database Initialization
# ==========================================
load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    st.error("❌ Missing GROQ_API_KEY! Please check your .env file or environment variables.")
    st.stop()

DATA_DIR = os.path.join(os.getcwd(), "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize database structure tracking layout
member2_db.create_tables()

# Establish uniform tracking token session tags
SESSION_ID = "context_switch_sprint_01"
member2_db.create_session(SESSION_ID)

# ==========================================
# 2. Page Configuration & ContextSwitch Theme CSS
# ==========================================
st.set_page_config(
    page_title="ContextSwitch AI | Multi-Mode Node",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 7rem; max-width: 1200px; }
    .main-title { font-size: 2.4rem; font-weight: 800; background: linear-gradient(45deg, #0284C7, #3B82F6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; }
    .sub-header { color: #64748B; font-size: 1rem; font-weight: 500; margin-top: 5px; margin-bottom: 1.5rem; letter-spacing: 0.5px; }
    section[data-testid="stSidebar"] { background-color: #0F172A !important; border-right: 1px solid #1E293B; }
    section[data-testid="stSidebar"] .stMarkdown h1, section[data-testid="stSidebar"] .stMarkdown h2, section[data-testid="stSidebar"] .stMarkdown h3 { color: #F8FAFC !important; font-weight: 700; }
    section[data-testid="stSidebar"] .stMarkdown p { color: #94A3B8 !important; }
    .status-card { background: #1E293B; border: 1px solid #334155; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; }
    .status-text { color: #38BDF8 !important; font-weight: 700; font-family: monospace; }
    .user-bubble { background-color: rgba(14, 165, 233, 0.15); border-left: 4px solid #0EA5E9; padding: 1.2rem; border-radius: 8px; margin-bottom: 1rem; }
    .assistant-bubble { background-color: rgba(30, 41, 59, 0.5); border-left: 4px solid #64748B; padding: 1.2rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #334155; }
    .node-badge { background: #1E293B; border: 1px solid #38BDF8; color: #38BDF8; font-family: monospace; font-size: 0.85rem; padding: 0.2rem 0.6rem; border-radius: 20px; display: inline-block; margin-bottom: 0.5rem; }
    .node-badge-rag { background: #1E293B; border: 1px solid #A78BFA; color: #A78BFA; font-family: monospace; font-size: 0.85rem; padding: 0.2rem 0.6rem; border-radius: 20px; display: inline-block; margin-bottom: 0.5rem; }
    div[data-testid="stExpander"] { background: #1E293B; border: 1px dashed #475569 !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. ContextSwitch AI Title Header Bar
# ==========================================
header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown("<h1 class='main-title'>⚡ ContextSwitch AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>STATEFUL MULTI-MODE ORCHESTRATION ENGINE | INNOVATION SPRINT 2026</p>", unsafe_allow_html=True)
with header_right:
    st.markdown(f"<p style='text-align: right; color: #64748B; padding-top: 1.5rem; font-weight: 500;'>Thread ID: `{SESSION_ID}`</p>", unsafe_allow_html=True)

st.markdown("<div style='border-bottom: 1px solid #334155; margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

# ==========================================
# 4. Initialize the Groq LLM Client
# ==========================================
@st.cache_resource
def init_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        streaming=True,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

try:
    llm = init_llm()
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}")
    st.stop()

# ==========================================
# 5. Dashboard Sidebar Control Room
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ SYSTEM ORCHESTRATION")
    st.markdown("Live monitoring controls for model context routing protocols.")
    st.markdown("---")

    st.markdown("<div class='status-card'><p style='margin:0; color:#94A3B8; font-size:0.8rem;'>CLUSTER STATUS</p><p style='margin:0; color:#4ADE80; font-weight:700;'>🟢 ONLINE // OPERATIONAL</p></div>", unsafe_allow_html=True)

    if "current_display_mode" not in st.session_state:
        st.session_state.current_display_mode = "IDLE // SYSTEM READY"
    st.markdown(f"<div class='status-card'><p style='margin:0; color:#94A3B8; font-size:0.8rem;'>ACTIVE ROUTING PATHWAY</p><p class='status-text'>{st.session_state.current_display_mode}</p></div>", unsafe_allow_html=True)

    session_count = member2_db.get_session_count()
    total_messages = member2_db.get_message_count()
    st.markdown(f"<div class='status-card'><p style='margin:0; color:#94A3B8; font-size:0.8rem;'>SQLITE LOGGED SESSIONS</p><p style='margin:0; color:#F59E0B; font-weight:700;'>📂 {session_count} ACTIVE THREADS</p></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='status-card'><p style='margin:0; color:#94A3B8; font-size:0.8rem;'>TOTAL RECORDED MESSAGES</p><p style='margin:0; color:#38BDF8; font-weight:700;'>💬 {total_messages} RECORDS LOGGED</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🧹 Clear Core Session Ledgers", use_container_width=True):
        member2_db.delete_session(SESSION_ID)
        member2_db.create_session(SESSION_ID)
        st.session_state.current_display_mode = "IDLE // REBOOT COMPLETE"
        st.toast("SQLite memory caches zeroed out cleanly!", icon="🗑️")
        time.sleep(0.4)
        st.rerun()

# ==========================================
# 6. Premium Document Staging Zone (Member 3 Layer)
# ==========================================
with st.expander("📂 ENTERPRISE KNOWLEDGE SOURCE INGESTION LAYER", expanded=False):
    uploaded_files = st.file_uploader(
        label="Ingest localized company policy assets directly into workspace memory map",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    if uploaded_files:
        st.markdown("<p style='color: #4ADE80; font-weight: 600; margin-top: 10px;'>✔️ Context buffers successfully injected into host staging filesystem:</p>", unsafe_allow_html=True)
        for file in uploaded_files:
            file_path = os.path.join(DATA_DIR, file.name)
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            st.markdown(f"<code style='color:#38BDF8;'>• {file.name}</code>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# Helper: parse stored mode tag from saved message
# ==========================================
MODE_TAG_RAG = "[MODE:rag]"
MODE_TAG_GEN = "[MODE:general]"

def strip_mode_tag(content: str) -> str:
    """Remove the hidden mode prefix tag from stored message content."""
    for tag in (MODE_TAG_RAG, MODE_TAG_GEN):
        if content.startswith(tag + "\n"):
            return content[len(tag) + 1:]
    return content

def get_badge_from_content(content: str) -> tuple[str, str]:
    """
    Returns (badge_html, badge_label) based on the stored mode tag.
    Falls back to general if no tag found.
    """
    if content.startswith(MODE_TAG_RAG):
        return (
            "<span class='node-badge-rag'>CONTEXT SWITCH // MODE 3: ISOLATED RAG PATH</span>",
            "CONTEXT SWITCH // MODE 3: ISOLATED RAG PATH"
        )
    return (
        "<span class='node-badge'>CONTEXT SWITCH // MODE 1: GENERAL LLM PATH</span>",
        "CONTEXT SWITCH // MODE 1: GENERAL LLM PATH"
    )

# ==========================================
# 7. Chat History Render Loop
# ==========================================
raw_db_history = member2_db.get_chat_history(SESSION_ID)
langchain_context_history = []

for role, message_content in raw_db_history:
    if role == "user":
        st.markdown(f"<div class='user-bubble'><strong>👤 USER PROMPT:</strong><br><br>{message_content}</div>", unsafe_allow_html=True)
        langchain_context_history.append(HumanMessage(content=message_content))
    elif role == "assistant":
        # FIX: Derive badge from the stored mode tag, not from response text keywords
        badge_html, badge_label = get_badge_from_content(message_content)
        display_content = strip_mode_tag(message_content)

        st.markdown(f"<div class='assistant-bubble'>{badge_html}<br><br>{display_content}</div>", unsafe_allow_html=True)
        # Pass clean content (no tag) into LangChain history for LLM context
        langchain_context_history.append(AIMessage(content=display_content))

if not raw_db_history:
    st.markdown("<div class='assistant-bubble' style='text-align:center; color:#94A3B8; padding: 3rem;'>⚡ ContextSwitch AI initialized. Core terminal routing channels completely open.<br>Submit a target string query into the base interface execution input to initiate pipeline computation.</div>", unsafe_allow_html=True)

# ==========================================
# 8. Fixed Native Bottom Input Interaction Component
# ==========================================
if user_query := st.chat_input("Input prompt sequence or construct document lookups here..."):

    st.markdown(f"<div class='user-bubble'><strong>👤 USER PROMPT:</strong><br><br>{user_query}</div>", unsafe_allow_html=True)
    member2_db.save_message(SESSION_ID, "user", user_query)

    with st.status("🛸 Routing transaction data through decision matrix...", expanded=True) as status:
        time.sleep(0.2)

        # LIVE INTERACTION: Call Member 2's clean router utility script!
        routing_decision = member2_router.determine_routing_intent(user_query)

        # FIX: Check both routing intent AND whether documents actually exist.
        # Only engage RAG mode when the router says so AND documents are present.
        # Do NOT fall back to RAG just because has_local_docs is True.
        has_local_docs = (
            os.path.exists(DATA_DIR)
            and len([f for f in os.listdir(DATA_DIR) if not f.startswith(".")]) > 0
        )

        use_rag = (routing_decision == "rag_mode") and has_local_docs

        if use_rag:
            current_mode = "Mode 3: Isolated RAG Context"
            badge_label = "CONTEXT SWITCH // MODE 3: ISOLATED RAG PATH"
            badge_html = "<span class='node-badge-rag'>CONTEXT SWITCH // MODE 3: ISOLATED RAG PATH</span>"
            mode_tag = MODE_TAG_RAG
            st.session_state.current_display_mode = "SWITCH_EXEC // MODE_3_RAG"
            status.update(label="📂 Shifting Context → Scanning localized vector arrays via ChromaDB Engine...", state="running")

            try:
                import tools.rag_retriever as rag_module
            except ImportError:
                import sys
                sys.path.append(os.getcwd())
                import rag_retriever as rag_module

            rag_payload = rag_module.retrieve_enterprise_docs(user_query)
            context = rag_payload["context"]
            sources = rag_payload["sources"]

            system_prompt = (
                "Answer the user query based ONLY on the following context records. "
                "If the answer cannot be found, state that you do not have that info.\n\n"
                f"Context:\n{context}"
            )

        elif routing_decision == "rag_mode" and not has_local_docs:
            # Router wanted RAG but no documents have been uploaded yet
            current_mode = "Mode 1: General LLM Context"
            badge_label = "CONTEXT SWITCH // MODE 1: GENERAL LLM PATH"
            badge_html = "<span class='node-badge'>CONTEXT SWITCH // MODE 1: GENERAL LLM PATH</span>"
            mode_tag = MODE_TAG_GEN
            st.session_state.current_display_mode = "SWITCH_EXEC // MODE_1_GEN (NO DOCS)"
            status.update(
                label="⚠️ RAG mode requested but no documents found → falling back to General LLM...",
                state="running"
            )
            sources = []
            system_prompt = (
                "You are an intelligent AI conversational assistant. "
                "Note: The user asked a document-related question but no documents have been uploaded yet. "
                "Politely let them know they can upload documents using the ENTERPRISE KNOWLEDGE SOURCE INGESTION LAYER panel above, "
                "and answer as best you can from your general knowledge."
            )

        else:
            current_mode = "Mode 1: General LLM Context"
            badge_label = "CONTEXT SWITCH // MODE 1: GENERAL LLM PATH"
            badge_html = "<span class='node-badge'>CONTEXT SWITCH // MODE 1: GENERAL LLM PATH</span>"
            mode_tag = MODE_TAG_GEN
            st.session_state.current_display_mode = "SWITCH_EXEC // MODE_1_GEN"
            status.update(label="🧠 Context Isolated → Connecting directly to Groq Cloud infrastructure...", state="running")
            sources = []
            system_prompt = "You are an intelligent AI conversational assistant. Answer the user prompt directly using your core knowledge base."

        status.update(label="Routing Fixed → Context Subsystem Secured", state="complete", expanded=False)

    # ==========================================
    # 9. Render Enhanced Assistant Generation Output
    # ==========================================
    with st.chat_message("assistant"):
        st.markdown(badge_html, unsafe_allow_html=True)
        response_placeholder = st.empty()
        full_response = ""

        execution_payload = langchain_context_history + [
            HumanMessage(content=f"{system_prompt}\n\nUser Question: {user_query}")
        ]

        try:
            for chunk in llm.stream(execution_payload):
                full_response += chunk.content
                response_placeholder.markdown(
                    f"<div class='assistant-bubble' style='margin-bottom:0px;'>{badge_html}<br><br>{full_response}▌</div>",
                    unsafe_allow_html=True
                )

            response_placeholder.markdown(
                f"<div class='assistant-bubble' style='margin-bottom:0px;'>{badge_html}<br><br>{full_response}</div>",
                unsafe_allow_html=True
            )

            # FIX: Prefix the saved message with the mode tag so history render
            # can correctly reconstruct the badge without relying on response text keywords.
            member2_db.save_message(SESSION_ID, "assistant", f"{mode_tag}\n{full_response}")

            if sources and current_mode == "Mode 3: Isolated RAG Context":
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("📚 VERIFIED DISK CITATION RECORDS"):
                    for src in sources:
                        st.markdown(f"<span style='color:#38BDF8;'>• {src}</span>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
            full_response = "Telemetry pipeline broken. Critical framework initialization failure."
            response_placeholder.markdown(f"<div class='assistant-bubble'>{full_response}</div>", unsafe_allow_html=True)

    st.rerun()