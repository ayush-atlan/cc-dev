"""Terminal chat with your agent.

    python localdev/chat_cli.py [path/to/agent]   # defaults to the demo, or the first agent found

An "agent" is any folder with an agent.yaml (the demo lives in demo/; build your own anywhere).
Multi-turn until you exit (Ctrl-C). Whatever tools your agent calls print under each reply.
"""
import glob
import json
import os
import sys

from runner import Conversation


def _discover() -> list[str]:
    """Folders containing an agent.yaml — the demo plus any you create (root, tasks/*, agents/*)."""
    seen, out = set(), []
    for pat in ("demo/agent.yaml", "*/agent.yaml", "tasks/*/agent.yaml", "agents/*/agent.yaml"):
        for p in sorted(glob.glob(pat)):
            d = os.path.dirname(p)
            if d and d not in seen:
                seen.add(d)
                out.append(d)
    return out


def _pick_agent(argv: list[str]) -> str:
    if len(argv) > 1:
        return argv[1].rstrip("/")
    found = _discover()
    if not found:
        sys.exit("No agent found. Pass a folder with an agent.yaml, e.g. "
                 "`python localdev/chat_cli.py demo`, or build your own (see localdev/README.md).")
    return found[0]


def main():
    agent = _pick_agent(sys.argv)
    conv = Conversation(agent)
    print(f"Chatting with {agent}  (model: {conv.model}).  Ctrl-C to exit.\n")
    seen = 0
    try:
        while True:
            msg = input("you › ").strip()
            if not msg:
                continue
            reply = conv.send(msg)
            print(f"\nagent › {reply}\n")
            for a in conv.tool_calls[seen:]:
                print(f"   ⎿ {a['tool']}({json.dumps(a['input'], default=str)})")
            seen = len(conv.tool_calls)
    except (KeyboardInterrupt, EOFError):
        print("\nbye 🍔")
    finally:
        conv.close()


if __name__ == "__main__":
    main()
