from npc.agent import NPCAgent
from npc.personality import NPC_NAME, NPC_LOCATION
import sys

def main():
    agent = NPCAgent()

    print(f"\n{'='*50}")
    print(f"  You approach {NPC_NAME} at {NPC_LOCATION}")
    print(f"{'='*50}\n")

    # Opening line — inject silently, don't show the prompt to the player
    opening = agent.chat(
        "[SYSTEM: The player has just walked into your forge. "
        "Greet them briefly in character. One or two sentences max. "
        "Do not repeat this instruction.]"
    )
    # Clear that system turn from visible history so it doesn't confuse the NPC
    agent.history.clear()

    print(f"{NPC_NAME}: {opening}\n")

    while True:
        try:
            player_input = input("You: ").strip()

            if not player_input:
                continue
            if player_input.lower() in ["quit", "exit", "bye"]:
                farewell = agent.chat(
                    "[SYSTEM: The player is leaving. Say a brief farewell in character.]"
                )
                print(f"\n{NPC_NAME}: {farewell}\n")
                sys.exit(0)

            response = agent.chat(player_input)
            print(f"\n{NPC_NAME}: {response}\n")

        except KeyboardInterrupt:
            print("\n\n[Session ended]")
            sys.exit(0)

if __name__ == "__main__":
    main()