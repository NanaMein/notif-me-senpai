from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from backend.databases.memory import MemoryDB

router = APIRouter(
    prefix="/api",
    tags=["api"],
)
class ChatMessage(BaseModel):
    role: str
    content: str


class MessageRequest(BaseModel):
    user_id: str
    message: str

class MessageResponse(MessageRequest):
    list_appended: list[ChatMessage]


@router.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"Hello": "World"}


@router.post("/", status_code=status.HTTP_200_OK, response_model=MessageResponse)
def send_message(request: MessageRequest):
    db = MemoryDB(user_id=request.user_id)
    db.add_user(request.message)
    db.add_assistant("Hello World")
    resp = MessageResponse(
        user_id=request.user_id, message=request.message, list_appended=db.get_messages()
    )
    return resp