from langchain_core.tools import tool
from datetime import datetime

# Simulated game state — in a real game this connects to your game engine
GAME_STATE = {
    "players": {
        "ibrahim": {
            "level": 5,
            "gold": 120,
            "reputation": "neutral",
            "active_quests": [],
            "inventory": ["iron sword", "leather armor", "health potion x2"]
        }
    },
    "world": {
        "time_of_day": "evening",
        "weather": "stormy",
        "active_events": ["grave robbing in the north district"]
    }
}


@tool
def get_player_stats(player_id: str) -> str:
    """Get the current stats and inventory of a player."""
    player = GAME_STATE["players"].get(player_id)
    if not player:
        return f"No record of player '{player_id}' in Vael."
    return (
        f"Player {player_id}: Level {player['level']}, "
        f"{player['gold']} gold, reputation={player['reputation']}, "
        f"inventory={player['inventory']}, "
        f"active_quests={player['active_quests']}"
    )


@tool
def trigger_quest(player_id: str, quest_name: str) -> str:
    """Assign a new quest to the player."""
    players = GAME_STATE["players"]
    if player_id not in players:
        players[player_id] = {"level": 1, "gold": 0, "reputation": "neutral",
                               "active_quests": [], "inventory": []}
    if quest_name in players[player_id]["active_quests"]:
        return f"Quest '{quest_name}' is already active for {player_id}."
    players[player_id]["active_quests"].append(quest_name)
    return f"Quest '{quest_name}' assigned to {player_id}."


@tool
def update_reputation(player_id: str, direction: str) -> str:
    """Update player reputation. Direction must be 'improve' or 'worsen'."""
    rep_ladder = ["enemy", "hostile", "neutral", "friendly", "trusted"]
    players = GAME_STATE["players"]
    if player_id not in players:
        return f"Player '{player_id}' not found."
    current = players[player_id]["reputation"]
    idx = rep_ladder.index(current) if current in rep_ladder else 2
    if direction == "improve":
        new_idx = min(idx + 1, len(rep_ladder) - 1)
    else:
        new_idx = max(idx - 1, 0)
    players[player_id]["reputation"] = rep_ladder[new_idx]
    return f"{player_id} reputation changed: {current} → {rep_ladder[new_idx]}"


@tool
def get_world_state() -> str:
    """Get the current state of the game world."""
    world = GAME_STATE["world"]
    return (
        f"Time: {world['time_of_day']}, "
        f"Weather: {world['weather']}, "
        f"Active events: {world['active_events']}"
    )


@tool
def craft_item(player_id: str, item_name: str, cost_gold: int) -> str:
    """Craft an item for the player if they have enough gold."""
    players = GAME_STATE["players"]
    if player_id not in players:
        return f"Player '{player_id}' not found."
    player = players[player_id]
    if player["gold"] < cost_gold:
        return f"{player_id} only has {player['gold']} gold. {item_name} costs {cost_gold}."
    player["gold"] -= cost_gold
    player["inventory"].append(item_name)
    return f"Crafted '{item_name}' for {player_id}. Remaining gold: {player['gold']}."


# All tools Kael can use
KAEL_TOOLS = [
    get_player_stats,
    trigger_quest,
    update_reputation,
    get_world_state,
    craft_item,
]