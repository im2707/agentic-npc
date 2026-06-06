# Agentic NPC AI — Kael the Blacksmith

An end-to-end agentic NPC system powered by a local LLM, persistent memory, 
and real-time tool calling. Built to demonstrate game AI engineering skills 
for ML Engineer roles in the gaming industry.

## Demo

> "I'll take the grave robbing investigation job."

```json
{
  "npc_name": "Kael",
  "response": "Smart choice. Meet me behind the forge at dusk. Don't be late.",
  "tools_used": [
    {
      "tool": "trigger_quest",
      "result": "Quest 'investigate_grave_robbings' assigned to ibrahim."
    },
    {
      "tool": "update_reputation", 
      "result": "ibrahim reputation changed: neutral → friendly"
    }
  ]
}
```

Kael didn't just respond — he assigned a quest and updated the player's 
reputation in the game state. Through natural conversation.

## What this project demonstrates

- **Agentic AI architecture** — LLM reasons about context and decides 
  which tools to call without hardcoded logic
- **Persistent cross-session memory** — ChromaDB stores every interaction; 
  Kael remembers players across server restarts
- **Real-time game state mutation** — conversation triggers actual changes 
  to quests, inventory, reputation, and world state
- **Production API design** — FastAPI REST backend with session management, 
  7 endpoints, full OpenAPI docs at `/docs`
- **Local LLM deployment** — Mistral 7B running via Ollama, zero cloud 
  dependency, sub-5s response time

## Architecture

```
Player input
    │
    ▼
FastAPI (/chat endpoint)
    │
    ▼
NPCAgent (LangChain + Mistral 7B via Ollama)
    ├── ChromaDB memory recall (relevant past interactions)
    ├── Personality system prompt (Kael's identity)
    └── Tool dispatcher
            ├── get_player_stats
            ├── trigger_quest
            ├── craft_item
            ├── update_reputation
            └── get_world_state
```

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Mistral 7B (Ollama, local) |
| Agent framework | LangChain |
| Memory | ChromaDB (persistent vector store) |
| API | FastAPI + Uvicorn |
| Language | Python 3.11 |

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message, get NPC response + tools fired |
| POST | `/greet` | NPC opening line when player approaches |
| GET | `/memory/{player_id}` | Everything Kael remembers about a player |
| GET | `/gamestate/{player_id}` | Current player stats, quests, inventory |
| GET | `/sessions` | Active player sessions |
| DELETE | `/session/{player_id}` | End a session |

## Quickstart

```bash
# 1. Install Ollama and pull Mistral
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral

# 2. Clone and install
git clone https://github.com/im2707/agentic-npc.git
cd agentic-npc
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Run
uvicorn api:app --reload --port 8000

# 4. Open interactive docs
# http://127.0.0.1:8000/docs
```

## Key design decisions

**Why local LLM over API?** Zero latency variance, no per-token cost at 
scale, and full control over the model — critical for real-time game 
systems where consistent response time matters.

**Why ChromaDB for memory?** Semantic similarity search means Kael recalls 
*relevant* memories, not just recent ones. If you mentioned your home 
village 50 turns ago and ask about travel now, Kael connects those dots.

**Why a custom tool parser over LangChain's built-in tool calling?** 
Mistral 7B generates tool call syntax as text rather than structured JSON. 
The custom regex parser intercepts this output format reliably across 
model versions without requiring function-calling fine-tuning.

## Roadmap

- [ ] Pygame visual demo (top-down scene, player walks up to NPC)
- [ ] LoRA fine-tuning on custom dialogue dataset
- [ ] Multi-NPC support (each NPC has distinct personality + memory)
- [ ] Unity/Unreal HTTP integration example

## Author

Mohammed Ibrahim — MS Computer Engineering, NYU (2026)  
ML Engineer | Game AI | [LinkedIn](https://linkedin.com/in/mohammed-ibrahim-ny)