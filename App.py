"""CCNA / CCNP Networking Tutor - Streamlit chat app powered by Gemini Flash."""

import os

import streamlit as st
from google import genai
from google.genai import types

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
DEFAULT_MODEL = "gemini-3.6-flash"  # change to any Gemini Flash model id
MAX_HISTORY_MESSAGES = 20  # last N messages sent to the model
MAX_INPUT_CHARS = 4000

LEVELS = {
    "CCNA": "CCNA (Cisco Certified Network Associate): network fundamentals, network access "
    "(VLANs, trunking, STP, EtherChannel, wireless), IP connectivity (static routing, OSPFv2), "
    "IP services (NAT, DHCP, DNS, NTP, SNMP, QoS basics), security fundamentals (ACLs, port security, "
    "AAA, VPN concepts), and automation/programmability basics.",
    "CCNP Enterprise": "CCNP Enterprise (core ENCOR plus concentrations): dual-stack architecture, "
    "virtualization, infrastructure (advanced OSPF, EIGRP, BGP, redistribution, path control, multicast), "
    "wireless, network assurance, security, SD-Access, SD-WAN, automation (Python, NETCONF/RESTCONF, "
    "YANG, REST APIs).",
}

MODES = {
    "Discuss / Explain": "Explain concepts clearly like a patient instructor: start with the idea in "
    "plain words, then the technical detail, then a short example or analogy. Offer one follow-up "
    "question at the end.",
    "Quiz me": "Act as an exam coach. Ask ONE multiple-choice question at a time (options A-D) at the "
    "chosen level, then wait for the answer. After the student answers, say if it is right, explain why "
    "each option is right or wrong, then ask if they want the next question. If they have not named a "
    "topic, ask for one first.",
    "Config & CLI help": "Focus on Cisco IOS / IOS-XE configuration and verification. Give exact CLI "
    "commands in fenced code blocks, explain what each command does, and include the 'show' commands "
    "used to verify the result.",
    "Troubleshooting": "Act as a troubleshooting coach. Ask for symptoms, topology and relevant 'show' "
    "output when needed, then work through a structured method (layer by layer), giving the most likely "
    "causes first and the commands to confirm each.",
}

QUICK_STARTS = [
    "Explain OSPF neighbor states",
    "Difference between STP, RSTP and MST",
    "How does BGP choose the best path?",
    "Subnetting tips for 192.168.10.0/26",
]

st.set_page_config(page_title="CCNA / CCNP Tutor", page_icon="🌐", layout="centered")


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def get_api_key(user_key: str = "") -> str:
    """Priority: key typed in sidebar > Streamlit secrets > environment variable."""
    if user_key.strip():
        return user_key.strip()
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")


def build_system_instruction(level: str, mode: str) -> str:
    return f"""You are an expert Cisco networking instructor and CCIE-level engineer helping a student prepare for Cisco certifications and real-world networking work.

Certification focus: {LEVELS[level]}

Teaching mode: {MODES[mode]}

Guidelines:
- Be accurate. If you are not sure about something, say so instead of guessing.
- Use Markdown. Put every CLI command or config in fenced code blocks.
- Use simple tables or bullet points for comparisons (for example OSPF vs EIGRP).
- Keep answers focused; do not write a huge essay for a simple question.
- Cisco exam blueprints change over time. When asked about exam topics, remind the student to check the current official blueprint on cisco.com.
- Only discuss networking, Cisco certifications, and closely related IT topics. Politely steer other questions back to networking.
"""


def build_contents(messages: list) -> list:
    """Convert stored chat messages into Gemini 'contents' (last N messages only)."""
    recent = messages[-MAX_HISTORY_MESSAGES:]
    # Gemini expects the conversation to start with a user turn.
    while recent and recent[0]["role"] != "user":
        recent = recent[1:]
    contents = []
    for m in recent:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=m["content"])]))
    return contents


def ask_gemini(api_key: str, model: str, level: str, mode: str, messages: list) -> str:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=build_contents(messages),
        config=types.GenerateContentConfig(
            system_instruction=build_system_instruction(level, mode),
            temperature=0.4,
        ),
    )
    text = (response.text or "").strip()
    if not text:
        raise ValueError("The AI returned an empty answer (it may have been blocked). Try rephrasing.")
    return text


def chat_to_markdown(messages: list) -> str:
    parts = []
    for m in messages:
        who = "You" if m["role"] == "user" else "Tutor"
        parts.append(f"### {who}\n\n{m['content']}\n")
    return "\n".join(parts)


# ----------------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------------
def main() -> None:
    st.title("🌐 CCNA / CCNP Networking Tutor")
    st.caption("Discuss networking concepts, practise exam questions, and get CLI and troubleshooting help.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    with st.sidebar:
        st.header("Settings")
        user_key = st.text_input(
            "Gemini API key",
            type="password",
            help="Leave empty if the key is set in Streamlit secrets or the GEMINI_API_KEY environment variable.",
        )
        model = st.text_input("Gemini model", value=DEFAULT_MODEL)
        level = st.selectbox("Certification level", list(LEVELS.keys()))
        mode = st.selectbox("Mode", list(MODES.keys()))
        st.markdown("[Get a free API key](https://aistudio.google.com/apikey)")

        if st.button("🗑 Clear chat"):
            st.session_state["messages"] = []
            st.rerun()
        if st.session_state["messages"]:
            st.download_button(
                "Download chat",
                data=chat_to_markdown(st.session_state["messages"]),
                file_name="networking_chat.md",
                mime="text/markdown",
            )

    messages = st.session_state["messages"]

    # Quick-start buttons on an empty chat
    clicked = None
    if not messages:
        st.write("Ask anything about CCNA or CCNP, or try one of these:")
        for q in QUICK_STARTS:
            if st.button(q, key=f"qs_{q}"):
                clicked = q

    for m in messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    typed = st.chat_input("Ask a networking question...")
    prompt = (typed or clicked or "").strip()[:MAX_INPUT_CHARS]
    if not prompt:
        return

    api_key = get_api_key(user_key)
    if not api_key:
        st.error("Please enter a Gemini API key in the sidebar.")
        return

    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_gemini(api_key, model.strip() or DEFAULT_MODEL, level, mode, messages)
            st.markdown(answer)
    except Exception as e:
        messages.pop()  # remove the unanswered question so history stays valid
        st.error(f"Something went wrong: {e}")
        return

    messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
