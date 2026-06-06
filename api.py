from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from npc.agent import NPCAgent
from npc.memory import get_all_memories
from npc.tools import GAME_STATE

app = FastAPI(title="Agentic NPC API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, NPCAgent] = {}


class ChatRequest(BaseModel):
    player_id: str
    message: str


class ChatResponse(BaseModel):
    npc_name: str
    response: str
    session_id: str
    turn_count: int
    tools_used: list = []


def get_or_create_session(player_id: str) -> NPCAgent:
    if player_id not in sessions:
        sessions[player_id] = NPCAgent(player_id=player_id)
    return sessions[player_id]


@app.get("/")
def root():
    return {"status": "Kael's forge is open", "active_sessions": len(sessions)}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    agent = get_or_create_session(request.player_id)
    try:
        response = agent.chat(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NPC error: {str(e)}")
    return ChatResponse(
        npc_name="Kael",
        response=response,
        session_id=request.player_id,
        turn_count=len(agent.get_history()),
        tools_used=agent.last_tool_calls,
    )


@app.post("/greet")
def greet(player_id: str):
    agent = get_or_create_session(player_id)
    opening = agent.chat(
        "[SYSTEM: Player just walked in. Greet them in one sentence, in character.]"
    )
    agent.clear_history()
    return {"npc_name": "Kael", "response": opening, "session_id": player_id}


@app.delete("/session/{player_id}")
def end_session(player_id: str):
    if player_id in sessions:
        del sessions[player_id]
        return {"status": "session ended"}
    raise HTTPException(status_code=404, detail="Session not found")


@app.get("/sessions")
def list_sessions():
    return {"active_sessions": list(sessions.keys()), "count": len(sessions)}


@app.get("/memory/{player_id}")
def get_memory(player_id: str):
    memories = get_all_memories(player_id)
    return {"player_id": player_id, "memory_count": len(memories), "memories": memories}


@app.get("/gamestate/{player_id}")
def get_gamestate(player_id: str):
    return {
        "player": GAME_STATE["players"].get(player_id, {}),
        "world": GAME_STATE["world"]
    }