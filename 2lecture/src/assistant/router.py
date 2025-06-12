from fastapi import APIRouter
from pydantic import BaseModel
from assistant.a2a_controller import agent_to_agent_communication
from pydantic import BaseModel

class A2ARequest(BaseModel):
    message: str

router = APIRouter(prefix="/assistant", tags=["assistant"])

@router.post("/a2a-chat")
async def a2a_chat(data: A2ARequest):
    result = await agent_to_agent_communication(data.message)
    return {"result": result}