"""Chat with your agent in the browser:

    streamlit run localdev/chat_streamlit.py

Pick the agent in the sidebar (the demo plus any you build). Whatever tools your agent calls show
in the sidebar as it works.
"""
import glob
import os

import streamlit as st

from runner import Conversation

st.set_page_config(page_title="McContext · local dev", page_icon="🍔")
st.title("🍔 Local dev — chat with your agent")


def _discover() -> list[str]:
    seen, out = set(), []
    for pat in ("demo/agent.yaml", "*/agent.yaml", "tasks/*/agent.yaml", "agents/*/agent.yaml"):
        for p in sorted(glob.glob(pat)):
            d = os.path.dirname(p)
            if d and d not in seen:
                seen.add(d)
                out.append(d)
    return out


agents = _discover()
if not agents:
    st.warning("No agent found. The demo lives in `demo/`; build your own folder with an "
               "`agent.yaml` (see `localdev/README.md`).")
    st.stop()

agent = st.sidebar.selectbox("Agent", agents, index=0)
st.sidebar.caption("Auth: your Claude subscription via the Claude Code CLI "
                   "(`claude setup-token` or `claude login`).")

# Keep one Conversation (and its event loop + SDK client) alive across Streamlit reruns.
if st.session_state.get("agent") != agent:
    st.session_state.agent = agent
    st.session_state.conv = Conversation(agent)
    st.session_state.msgs = []

for m in st.session_state.msgs:
    st.chat_message(m["role"]).write(m["content"])

if prompt := st.chat_input("Message your agent…"):
    st.session_state.msgs.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("thinking…"):
            reply = st.session_state.conv.send(prompt)
        st.write(reply)
    st.session_state.msgs.append({"role": "assistant", "content": reply})

calls = st.session_state.conv.tool_calls
if calls:
    st.sidebar.subheader("Tool calls this session")
    for a in calls:
        st.sidebar.code(f"{a['tool']}({a['input']})", language="json")
