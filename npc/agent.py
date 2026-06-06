from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from npc.personality import NPC_SYSTEM_PROMPT, NPC_NAME
from npc.memory import save_memory, recall_memories
from npc.tools import (
    get_player_stats, trigger_quest,
    update_reputation, get_world_state, craft_item
)
import re


# Map tool names to actual functions
TOOL_MAP = {
    "get_player_stats": get_player_stats,
    "trigger_quest": trigger_quest,
    "update_reputation": update_reputation,
    "get_world_state": get_world_state,
    "craft_item": craft_item,
}


def parse_and_run_tools(text: str, player_id: str) -> tuple[str, list]:
    """
    Scan LLM output for [tool_name key="val"] patterns.
    Execute each one found. Return cleaned text + list of tool results.
    """
    pattern = r'\[(\w+)([^\]]*)\]'
    matches = re.findall(pattern, text)
    tool_calls_made = []
    clean_text = text

    for tool_name, args_str in matches:
        if tool_name not in TOOL_MAP:
            continue

        # Parse key="value" or key=value pairs
        arg_pattern = r'(\w+)=["\']?([^"\'\\,\]]+)["\']?'
        args = dict(re.findall(arg_pattern, args_str))

        # Always inject player_id
        args["player_id"] = player_id

        # Convert numeric strings to int where needed
        for k, v in args.items():
            try:
                args[k] = int(v)
            except (ValueError, TypeError):
                pass

        try:
            result = TOOL_MAP[tool_name].invoke(args)
            tool_calls_made.append({
                "tool": tool_name,
                "args": args,
                "result": result
            })
        except Exception as e:
            tool_calls_made.append({
                "tool": tool_name,
                "args": args,
                "result": f"error: {str(e)}"
            })

        # Remove the tool call tag from the visible response
        full_tag = f"[{tool_name}{args_str}]"
        clean_text = clean_text.replace(full_tag, "").strip()

    return clean_text, tool_calls_made


class NPCAgent:
    def __init__(self, player_id: str = "default"):
        self.player_id = player_id
        self.llm = ChatOllama(
            model="mistral",
            temperature=0.8,
            num_predict=200,
        )
        self.history = InMemoryChatMessageHistory()
        self.system_message = SystemMessage(content=NPC_SYSTEM_PROMPT)
        self.last_tool_calls = []

    def _build_memory_context(self, player_input: str) -> str:
        memories = recall_memories(self.player_id, player_input, n_results=4)
        if not memories:
            return ""
        memory_block = "\n".join(f"- {m}" for m in memories)
        return (
            f"\n\n[KAEL'S MEMORY — what you remember about this player:]\n"
            f"{memory_block}\n"
            f"[Use naturally. Don't recite. Let it inform your tone.]\n"
        )

    def chat(self, player_input: str) -> str:
        self.last_tool_calls = []

        memory_context = self._build_memory_context(player_input)
        augmented_system = SystemMessage(
            content=NPC_SYSTEM_PROMPT + memory_context
        )

        self.history.add_user_message(player_input)
        messages = [augmented_system] + self.history.messages

        response = self.llm.invoke(messages)
        raw_reply = response.content

        # Parse and execute any tool calls embedded in the response
        clean_reply, tool_calls = parse_and_run_tools(raw_reply, self.player_id)
        self.last_tool_calls = tool_calls

        # If tools fired, append results to context and get a final reply
        if tool_calls:
            results_summary = "\n".join(
                f"[{tc['tool']} result: {tc['result']}]"
                for tc in tool_calls
            )
            followup_messages = messages + [
                SystemMessage(content=(
                    f"You just took these actions:\n{results_summary}\n"
                    f"Now give your spoken in-character response to the player. "
                    f"Do NOT include any tool tags. Just speak as Kael."
                ))
            ]
            final_response = self.llm.invoke(followup_messages)
            clean_reply = final_response.content

        self.history.add_ai_message(clean_reply)

        # Persist to long-term memory
        save_memory(self.player_id, "player", player_input)
        save_memory(self.player_id, "kael", clean_reply)

        return clean_reply

    def get_history(self) -> list:
        return [
            {
                "role": "player" if isinstance(m, HumanMessage) else NPC_NAME,
                "content": m.content
            }
            for m in self.history.messages
        ]

    def clear_history(self):
        self.history.clear()