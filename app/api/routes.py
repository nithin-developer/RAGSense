"""
API routes for RAG operations.
"""

import asyncio
import logging
from functools import partial

from fastapi import APIRouter, HTTPException, UploadFile, File, Header
from langchain_core.messages import HumanMessage, AIMessage

from app.memory.chat_history_mongo import ChatHistory
from app.models.query_request import QueryRequest
from app.rag.document_upload import documents
from app.rag.graph_builder import builder

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/rag/query")
async def rag_query(req: QueryRequest):
    """
    Process a RAG query and return the result.

    Args:
        req: The query request containing query text and session_id.

    Returns:
        The generated response from the RAG pipeline.
    """
    chat_history = ChatHistory.get_session_history(req.session_id)
    await chat_history.add_message(HumanMessage(content=req.query))

    messages = await chat_history.get_messages()
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, partial(builder.invoke, {"messages": messages}))
    output_text = result["messages"][-1].content

    await chat_history.add_message(AIMessage(content=output_text))
    return {"result": result["messages"][-1]}


@router.post("/rag/documents/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Header(..., alias="X-Description")
):
    """
    Upload a document for RAG processing.

    Args:
        file: The file to upload (PDF or TXT).
        description: Document description provided via header.

    Returns:
        Upload status.
    """
    # Read file bytes in async context before handing off to thread
    file_bytes = await file.read()
    file.file.seek(0)  # reset so documents() can read again if needed

    try:
        loop = asyncio.get_event_loop()
        status_upload = await loop.run_in_executor(
            None, partial(documents, description, file)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Document upload failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": status_upload}

