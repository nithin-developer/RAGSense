"""
Retriever setup and vector store configuration.
"""

import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import create_retriever_tool
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.vectorstores import FAISS

from app.core.config import settings

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# NVIDIAEmbeddings automatically handles input_type="passage"/"query"
# required by asymmetric models like nv-embedqa-e5-v5
embeddings = NVIDIAEmbeddings(
    model="nvidia/nv-embedqa-e5-v5",
    api_key=NVIDIA_API_KEY,
    truncate="NONE",
)

# Global variable to store the FAISS vectorstore instance
# This ensures get_retriever() can access documents stored by retriever_chain()
_faiss_vectorstore = None


# ── Dynamic retriever ──────────────────────────────────────────────────────────
# Solves the stale-reference problem: the agent creates its tools once at import
# time, but documents are uploaded later. This retriever always reads from the
# *current* global _faiss_vectorstore so new docs are visible immediately.

class _DynamicRetriever(BaseRetriever):
    """Retriever that always delegates to the current _faiss_vectorstore."""

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun | None = None,
        **kwargs: Any,
    ) -> list[Document]:
        global _faiss_vectorstore
        if _faiss_vectorstore is None:
            return [
                Document(
                    page_content="No documents have been uploaded yet. "
                    "Please upload a document first.",
                    metadata={"source": "initialization"},
                )
            ]
        return _faiss_vectorstore.as_retriever().invoke(query)


def retriever_chain(chunks: list[Document]):
    """
    Initialize and store documents in FAISS vector database.

    Args:
        chunks: List of document chunks to store.

    Returns:
        Boolean indicating success of the operation.
    """
    global _faiss_vectorstore

    try:
        vectorstore = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )

        # Store the vectorstore globally so DynamicRetriever can access it
        _faiss_vectorstore = vectorstore

        print("FAISS vector store initialized with documents")
        print(f"Vectorstore contains {len(chunks)} document chunks")
        return True
    except Exception as e:
        print(f"Error storing documents in FAISS: {e}")
        return False


def get_retriever():
    """
    Get a retriever tool connected to the FAISS vector store.

    Returns the retriever tool that uses a dynamic retriever, so documents
    uploaded after agent initialization are immediately searchable.

    Returns:
        A LangChain retriever tool configured for the vector store.

    Raises:
        Exception: If initialization fails.
    """
    global _faiss_vectorstore

    try:
        # Create the dummy vectorstore so the embeddings are validated at startup
        if _faiss_vectorstore is None:
            print("No documents uploaded yet, creating dummy vectorstore")
            dummy_doc = Document(
                page_content="No documents have been uploaded yet. "
                "Please upload a document first.",
                metadata={"source": "initialization"},
            )
            _faiss_vectorstore = FAISS.from_documents(
                documents=[dummy_doc],
                embedding=embeddings,
            )

        # Use the dynamic retriever so new uploads are visible immediately
        retriever = _DynamicRetriever()

        # Load document description
        if os.path.exists("description.txt"):
            with open("description.txt", "r", encoding="utf-8") as f:
                description = f.read()
        else:
            description = None

        retriever_tool = create_retriever_tool(
            retriever,
            "retriever_customer_uploaded_documents",
            f"Use this tool **only** to answer questions about: {description}\n"
            "Don't use this tool to answer anything else."
        )

        return retriever_tool

    except Exception as e:
        print(f"Error initializing retriever: {e}")
        raise Exception(e)

