from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import os
from core.database import supabase
from dotenv import load_dotenv


router = APIRouter()

load_dotenv()

router = APIRouter(prefix="/chats", tags=["chats"])
# ---------- SCHEMAS ----------
class ChatSessionCreate(BaseModel):
    title: Optional[str] = None
    chat_type: str  # "main", "secondary", "third"
    userid:UUID

class getChatSessions(BaseModel):
    userid: UUID
    chat_type: str


class ChatSession(BaseModel):
    id: UUID
    userid: UUID
    chat_type: str
    title: Optional[str]
    created_at: datetime


class MessageCreate(BaseModel):
    role: str  # "user" or "ai"
    content: str
    imageUrls: Optional[List[str]] = []


class Message(BaseModel):
    id: UUID
    session_id: UUID
    user_query: str
    ai_answer: Optional[str]
    imageUrls: Optional[List[str]]
    created_at: datetime


# ---------- ROUTES ----------

# get all the chats_session name from chat_type and user_id
@router.get("/", response_model=List[ChatSession])
def list_chats(userReq:getChatSessions):
    query = supabase.table("chat_sessions").select("*").eq("userid", str(userReq.userid))
    if userReq.chat_type:
        query = query.eq("chat_type", userReq.chat_type)
    response = query.order("created_at", desc=True).execute()
    return response.data


# create a new chat session
@router.post("/", response_model=ChatSession)
def create_chat(session: ChatSessionCreate):
    response = (
        supabase.table("chat_sessions")
        .insert(
            {
                "userid": str(session.userid),
                "chat_type": session.chat_type,
                "title": session.title,
            }
        )
        .execute()
    )
    return response.data[0]


# get a single chat session by chat_id
@router.get("/{chat_id}", response_model=ChatSession)
def get_chat(chat_id: UUID):
    response = (
        supabase.table("chat_sessions").select("*").eq("id", str(chat_id)).execute()
    )
    if not response.data:
        raise HTTPException(404, "Chat session not found")
    return response.data[0]


# add a new message to chat
@router.post("/{chat_id}/messages", response_model=Message)
def add_message(chat_id: UUID, msg: MessageCreate):
    if msg.role == "user":
        response = (
            supabase.table("chat_messages")
            .insert(
                {
                    "session_id": str(chat_id),
                    "user_query": msg.content,
                    "imageurls": msg.imageUrls,
                }
            )
            .execute()
        )
    elif msg.role == "ai":
        # fetch last user message
        last_msg = (
            supabase.table("chat_messages")
            .select("user_query")
            .eq("session_id", str(chat_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not last_msg.data:
            raise HTTPException(400, "No previous user message found for AI reply")

        response = (
            supabase.table("chat_messages")
            .insert(
                {
                    "session_id": str(chat_id),
                    "user_query": last_msg.data[0]["user_query"],
                    "ai_answer": msg.content,
                    "imageurls": msg.imageUrls,
                }
            )
            .execute()
        )
    else:
        raise HTTPException(400, "Invalid role")

    return response.data[0]


# delete chat session
@router.delete("/{chat_id}")
def delete_chat(chat_id: UUID):
    supabase.table("chat_sessions").delete().eq("id", str(chat_id)).execute()
    return {"status": "deleted"}