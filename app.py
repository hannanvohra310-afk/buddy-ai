"""
Buddy AI - Career Counselling Chatbot
Main application entry point.

This file orchestrates the app flow. Business logic is in separate modules:
- utils/ - Sanitization, rate limiting, retry logic
- ui/ - Styles and components
- chat/ - Chat history management
- conversation/ - State detection
- prompts/ - System prompts and guardrails
- memory/ - Student profiling
- auth/ - Authentication
"""
from dotenv import load_dotenv
import os
import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
APP_DIR = Path(__file__).parent.resolve()
DATA_PATH = APP_DIR / "data"

# Configuration
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300
RETRIEVER_K = 6
LLM_TEMPERATURE = 0.3
PINECONE_INDEX = "buddy-ai-index"

load_dotenv(APP_DIR / ".env")

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Buddy AI - Career Counsellor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== AUTHENTICATION CHECK ==========
if not st.session_state.get('authenticated', False):
    st.switch_page("pages/login.py")
    st.stop()

# Session expiry check (24 hours)
session_created = st.session_state.get('session_created_at')
if session_created:
    if isinstance(session_created, str):
        session_created = datetime.fromisoformat(session_created)
    if datetime.now() - session_created > timedelta(hours=24):
        logger.info("Session expired, redirecting to login")
        st.session_state.authenticated = False
        st.session_state.session_token = None
        st.warning("Your session has expired. Please log in again.")
        st.switch_page("pages/login.py")
        st.stop()

# ========== IMPORT MODULES ==========
from utils import sanitize_input, check_rate_limit, retry_with_backoff
from ui.styles import inject_styles, inject_sidebar_styles
from ui.components import render_header, render_sidebar, render_welcome, render_messages
from chat import (
    save_chat_history, load_chat_history, create_new_chat,
    get_chat_by_id, add_message,
    get_active_messages, ensure_active_chat, switch_to_chat
)

# Initialize Buddy AI modules
state_detector = None
response_generator = None
guardrails = None
profile_extractor = None
memory_store = None
memory_referencer = None
MODULES_LOADED = False

try:
    from conversation.constants import ConversationState, CANONICAL_OUT_OF_SCOPE_RESPONSE
except ImportError:
    from enum import Enum, auto
    class ConversationState(Enum):
        OUT_OF_SCOPE = auto()
        CONFUSED = auto()
        VALIDATION_SEEKING = auto()
        SELF_REFLECTION = auto()
        CAREER_CURIOSITY = auto()
        COMPARISON = auto()
        INFORMATION_SEEKING = auto()
        GREETING = auto()
    CANONICAL_OUT_OF_SCOPE_RESPONSE = "I'm sorry — I don't have the right context to answer this. I can help with careers, education, and future planning."

try:
    from conversation import StateDetector, ResponseGenerator
    from prompts import ResponseGuardrails
    from memory import ProfileExtractor, MemoryStore, MemoryReferencer

    state_detector = StateDetector()
    response_generator = ResponseGenerator()
    guardrails = ResponseGuardrails()
    profile_extractor = ProfileExtractor()
    memory_store = MemoryStore(db_path=str(DATA_PATH / "buddy_ai.db"))
    memory_referencer = MemoryReferencer(memory_store)
    MODULES_LOADED = True
    logger.info("Buddy AI modules loaded successfully")
except Exception as e:
    logger.warning(f"Could not load Buddy AI modules: {e}")

# ========== SESSION STATE ==========
# Note: messages are stored in the active chat (single source of truth)
# Use get_active_messages() to access them
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "chat_list" not in st.session_state:
    st.session_state.chat_list = load_chat_history()
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = False
if "suggestion_clicked" not in st.session_state:
    st.session_state.suggestion_clicked = None
if "rag_status" not in st.session_state:
    st.session_state.rag_status = "offline"

# ========== INJECT STYLES ==========
inject_styles()

# ========== SETUP RAG ==========
rag_ready = False
rag_chain = None

try:
    if DATA_PATH.exists():
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_pinecone import PineconeVectorStore
        from pinecone import Pinecone

        all_docs = []
        for file in DATA_PATH.iterdir():
            if file.suffix == ".pdf":
                loader = PyPDFLoader(str(file))
                all_docs.extend(loader.load())

        if all_docs:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
            )
            docs = text_splitter.split_documents(all_docs)

            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            index = pc.Index(PINECONE_INDEX)

            vectorstore = PineconeVectorStore(index=index, embedding=embeddings, text_key="text")
            retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})

            stats = index.describe_index_stats()
            if stats["total_vector_count"] == 0:
                vectorstore.add_documents(docs)

            llm = ChatOpenAI(model="gpt-4o-mini", temperature=LLM_TEMPERATURE)

            from prompts import get_system_prompt
            base_system_prompt = get_system_prompt()

            prompt = ChatPromptTemplate.from_template(base_system_prompt + """

## CURRENT CONTEXT
Chat History:
{history}

Career Information:
{context}

{memory_context}
{state_instructions}

Student's Question: {question}

Remember: Respond like a warm elder sibling. Keep it simple. Max 1-2 questions. Max 1 emoji.
""")

            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)

            rag_chain = (
                {
                    "context": lambda x: format_docs(retriever.invoke(x["question"])),
                    "question": lambda x: x["question"],
                    "history": lambda x: x["history"],
                    "memory_context": lambda x: x.get("memory_context", ""),
                    "state_instructions": lambda x: x.get("state_instructions", ""),
                }
                | prompt | llm | StrOutputParser()
            )
            rag_ready = True
            st.session_state.rag_status = "connected"
            logger.info("RAG system initialized")
except Exception as e:
    logger.error(f"RAG initialization failed: {e}")

# ========== MAIN APP ==========

# Menu toggle button
col1, col2, col3 = st.columns([1, 6, 1])
with col1:
    if st.button("☰", key="menu_btn", help="Menu"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()

# Render header
render_header()

# Render sidebar if open
if st.session_state.sidebar_open:
    inject_sidebar_styles()
    render_sidebar()

# Add spacer for header
st.markdown('<div style="height: 70px;"></div>', unsafe_allow_html=True)

# Chat area - use single source of truth
messages = get_active_messages()
if len(messages) == 0:
    render_welcome()
else:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    render_messages()
    st.markdown('</div>', unsafe_allow_html=True)

# Add spacer for input
st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)

# ========== CHAT INPUT ==========
def format_history(messages):
    return "\n".join(
        f"{'Student' if m['role']=='user' else 'Buddy AI'}: {m['content']}"
        for m in messages[-6:]
    )

# Handle suggestion clicks
user_input = st.chat_input("Ask me about any career")
if st.session_state.suggestion_clicked:
    user_input = st.session_state.suggestion_clicked
    st.session_state.suggestion_clicked = None

if user_input:
    # Sanitize and validate
    user_input = sanitize_input(user_input)
    if not user_input:
        st.warning("Please enter a valid message.")
        st.stop()

    if not check_rate_limit():
        st.warning("You're sending messages too quickly. Please wait a moment.")
        st.stop()

    # Ensure active chat exists (single source of truth)
    ensure_active_chat()

    # Add user message (single source of truth)
    add_message("user", user_input)

    # Get messages for state detection
    messages = get_active_messages()

    # Detect conversation state
    current_state = ConversationState.CAREER_CURIOSITY
    if MODULES_LOADED:
        try:
            current_state = state_detector.detect_state(user_input, messages)
            logger.info(f"Detected state: {current_state.name}")

            # Extract profile info
            student_id = st.session_state.get("student_id")
            if student_id:
                extractions = profile_extractor.extract_from_message(user_input)
                if any(extractions.values()):
                    memory_store.update_profile(student_id, extractions)
        except Exception as e:
            logger.error(f"State detection error: {e}")

    # Handle out-of-scope
    if current_state == ConversationState.OUT_OF_SCOPE:
        response = CANONICAL_OUT_OF_SCOPE_RESPONSE
        add_message("assistant", response)
        st.rerun()

    # Generate response
    if rag_ready and rag_chain:
        with st.spinner("Thinking..."):
            try:
                history = format_history(messages)
                state_instructions = ""
                memory_context = ""

                if MODULES_LOADED:
                    state_instructions = response_generator.build_state_instructions(current_state)
                    student_id = st.session_state.get("student_id")
                    if student_id:
                        message_idx = len(messages)
                        should_ref = memory_referencer.should_reference_memory(student_id, message_idx)
                        memory_context = memory_referencer.build_memory_context(
                            student_id, include_reference=should_ref, current_input=user_input
                        )

                def make_rag_call():
                    return rag_chain.invoke({
                        "question": user_input,
                        "history": history,
                        "memory_context": memory_context,
                        "state_instructions": state_instructions
                    })

                answer = retry_with_backoff(make_rag_call)

                # Validate with guardrails
                if MODULES_LOADED and guardrails:
                    is_valid, violations = guardrails.validate_response(answer, current_state)
                    if not is_valid:
                        logger.warning(f"Response violations: {violations}")

                add_message("assistant", answer)

            except Exception as e:
                logger.error(f"RAG query error: {e}")
                add_message("assistant", "Something went wrong. Could you try that again?")
    else:
        # Fallback responses
        if current_state == ConversationState.GREETING:
            response = "Hey! Good to see you. I'm Buddy AI - your career exploration buddy. What's on your mind?"
        elif current_state == ConversationState.CONFUSED:
            response = "It's totally normal to feel confused about this. Let's start simple - what's one thing you enjoy doing?"
        elif current_state == ConversationState.VALIDATION_SEEKING:
            response = "That's a thoughtful question. Careers aren't about being 'good enough' - they're about finding what fits you."
        else:
            response = "That's a great question! Could you tell me more about what interests you about this?"

        add_message("assistant", response)

    st.rerun()

# Handle URL-based chat selection
query_params = st.query_params
if "chat" in query_params:
    chat_id = query_params.get("chat")
    if chat_id and chat_id != st.session_state.current_chat_id:
        if switch_to_chat(chat_id):
            st.query_params.clear()
            st.rerun()
