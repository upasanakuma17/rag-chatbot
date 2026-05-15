import os
import streamlit as st
import pdfplumber

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.header("🤖 My RAG Chatbot")

# ---------------- SESSION STATE ---------------- #

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.title("📚 Your Documents")

    uploaded_files = st.file_uploader(
        "Upload your PDFs and start asking questions",
        type="pdf",
        accept_multiple_files=True
    )

    if st.button("Clear Chat"):

        st.session_state.messages = []

        st.rerun()

# ---------------- MAIN LOGIC ---------------- #

if uploaded_files:

    st.success("Files uploaded successfully!")

    # ---------- EXTRACT TEXT + METADATA ---------- #

    documents = []

    for uploaded_file in uploaded_files:

        with pdfplumber.open(uploaded_file) as pdf:

            for page_num, page in enumerate(pdf.pages):

                extracted_text = page.extract_text()

                if extracted_text:

                    documents.append(
                        {
                            "text": extracted_text,
                            "page": page_num + 1,
                            "source": uploaded_file.name
                        }
                    )

    # ---------- TEXT SPLITTING ---------- #

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " ", ""],
        chunk_size=1000,
        chunk_overlap=200
    )

    texts = []
    metadatas = []

    for doc in documents:

        split_chunks = text_splitter.split_text(doc["text"])

        for chunk in split_chunks:

            texts.append(chunk)

            metadatas.append(
                {
                    "page": doc["page"],
                    "source": doc["source"]
                }
            )

    # ---------- EMBEDDINGS ---------- #

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # ---------- VECTOR DATABASE ---------- #

    DB_FAISS_PATH = "vectorstore/db_faiss"

    if os.path.exists(DB_FAISS_PATH):

        vector_store = FAISS.load_local(
            DB_FAISS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    else:

        vector_store = FAISS.from_texts(
            texts,
            embeddings,
            metadatas=metadatas
        )

        vector_store.save_local(DB_FAISS_PATH)

    # ---------- RETRIEVER ---------- #

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4}
    )

    # ---------- LLM ---------- #

    llm = ChatOllama(
        model="gemma:2b",
        temperature=0.3
    )

    # ---------- PROMPT ---------- #

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a helpful assistant answering questions about PDF documents.

Guidelines:
1. Give complete and detailed answers.
2. Use ONLY the provided context.
3. If answer is not available in context, say politely that information is unavailable.
4. Summarize long answers in bullets when needed.
5. Mention important details and explanations clearly.

Context:
{context}
"""
        ),
        ("human", "{question}")
    ])

    # ---------- FORMAT DOCS ---------- #

    def format_docs(docs):

        return "\n\n".join(
            [doc.page_content for doc in docs]
        )

    # ---------- RAG CHAIN ---------- #

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # ---------- DISPLAY OLD CHAT ---------- #

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # ---------- USER INPUT ---------- #

    user_question = st.chat_input(
        "Ask a question about your documents"
    )

    # ---------- GENERATE RESPONSE ---------- #

    if user_question:

        # store user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        # show user message
        with st.chat_message("user"):

            st.markdown(user_question)

        with st.spinner("Thinking..."):

            # retrieve relevant docs
            retrieved_docs = retriever.invoke(user_question)

            # generate answer
            response = chain.invoke(user_question)

        # show assistant response
        with st.chat_message("assistant"):

            st.markdown(response)

        # store assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        # ---------- SOURCE CHUNKS ---------- #

        with st.expander("📖 View Source Chunks"):

            for i, doc in enumerate(retrieved_docs):

                st.write(f"### Source {i+1}")

                st.write(
                    f"📄 File: {doc.metadata['source']}"
                )

                st.write(
                    f"📌 Page: {doc.metadata['page']}"
                )

                st.write(doc.page_content)

                st.write("------")