from typing import Union
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from backend.chat_completions.chatbot import ask_query, Response_Type, List_Types
import uuid

router = APIRouter(
    prefix="/api",
    tags=["api"],
)
class MessageRequest(BaseModel):
    user_id: Union[uuid.UUID, str]
    message: Response_Type = ""

class MessageResponse(MessageRequest):
    list_appended: List_Types

@router.post("/", status_code=status.HTTP_200_OK)
async def send_message(request: MessageRequest):
    try:
        response, list_messages = await ask_query(user_id=request.user_id, query=request.message)

        resp = MessageResponse(
            user_id=request.user_id, message=response, list_appended=list_messages
        )
        return resp
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))