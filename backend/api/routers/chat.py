from uuid import uuid4
from fastapi import APIRouter
from backend.models.raw_pattern_form import RawPatternQuery
from backend.models.chat_session import ChatSession

chat_router = APIRouter(
    prefix="/chat", tags=["chat"], responses={404: {"description": "Not Found"}}
)

sessions = {}  # Store active sessions


@chat_router.post("/")
def create_session(query: RawPatternQuery):
    """
    This function starts a session

    Args:
        filters (MetadataFilters): _description_

    Returns:
        _type_: _description_
    """
    # Creates a new session, and uses the raw pattern query to call pattern-generator
    filters = query.clean_query()
    session_id = str(uuid4())
    sessions[session_id] = {
        "history": [],
        "requirements": filters,
    }  # Store session info
    return session_id


@chat_router.get("/session/{session_id}")
async def start_session(session_id: str):
    """
    Retrieve the session id and the requirements
    """
    requirements = sessions.get(session_id).get("requirements")
    print("requirements:", requirements, type(requirements))
    chat = ChatSession(sessionId=session_id, requirements=requirements)
    print("clothing: ", chat.requirements.clothing_category)
    response = await chat.query_qdrant_engine(
        f"generate a pattern to make a {chat.requirements.clothing_category}"
    )
    print("backend response: ", response)
    return response
