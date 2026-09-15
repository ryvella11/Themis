import os
import glob
import streamlit as st
from pypdf import PdfReader
import anthropic

st.set_page_config(page_title="Themis Speaks", page_icon="⚖️", layout="centered")

# ---------- CONFIG ----------
MODEL = "claude-sonnet-4-6"
DOCS_FOLDER = "docs"
MAX_CONTEXT_CHARS = 600_000  # rough safety cap (~150k tokens); trims oldest-added docs if exceeded

SYSTEM_PROMPT_TEMPLATE = """You are Themis Speaks, an expert assistant on the FIA regulations.
You have been given the full text of one or more official FIA regulation documents below.
Answer questions ONLY using this material. When you answer:
- Cite the specific Article/Section number whenever possible (e.g. "Article 3.1.2").
- If the regulations don't cover something, or a value isn't stated in the text you can see,
  say so plainly rather than guessing or estimating. Never invent a number, tolerance, or
  dimension that isn't explicitly present in the text below.
- Many FIA dimensional specs are defined on diagrams/drawings rather than in prose. Since you
  only see extracted text, you may be missing figures shown only as diagram annotations. If a
  question seems like it should have a numeric answer but you can't find it in the text, say
  that explicitly and suggest the person check the relevant diagram in the source PDF, rather
  than filling the gap with a plausible-sounding guess.
- If the person's question contains an incorrect premise or an incorrect figure (e.g. they
  assert a wrong minimum/maximum), correct them directly and cite the actual text — do not
  simply go along with an incorrect assumption to be agreeable.
- Be precise and concise; this is a technical/legal reference tool, not casual chat.

--- BEGIN FIA REGULATIONS TEXT ---
{regs_text}
--- END FIA REGULATIONS TEXT ---
"""


@st.cache_data(show_spinner=False)
def load_regulations():
    """Extract text from every PDF in the docs/ folder."""
    pdf_paths = sorted(glob.glob(os.path.join(DOCS_FOLDER, "*.pdf")))
    if not pdf_paths:
        return "", []

    combined = []
    loaded_files = []
    total_chars = 0

    for path in pdf_paths:
        filename = os.path.basename(path)
        try:
            reader = PdfReader(path)
            text_parts = [f"\n\n===== DOCUMENT: {filename} =====\n"]
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
            doc_text = "".join(text_parts)
        except Exception as e:
            doc_text = f"\n\n[Could not read {filename}: {e}]\n"

        total_chars += len(doc_text)
        if total_chars > MAX_CONTEXT_CHARS:
            loaded_files.append(f"{filename} (SKIPPED — context limit reached)")
            continue

        combined.append(doc_text)
        loaded_files.append(filename)

    return "".join(combined), loaded_files


def get_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error(
            "No Anthropic API key found. Add ANTHROPIC_API_KEY in your app's Secrets "
            "(Settings → Secrets on Streamlit Community Cloud)."
        )
        st.stop()
    return anthropic.Anthropic(api_key=api_key)


# ---------- UI ----------
st.title("⚖️ Themis Speaks")
st.caption("Ask questions about the FIA regulations. Answers are grounded in the documents you've loaded.")

regs_text, loaded_files = load_regulations()

with st.sidebar:
    st.subheader("Loaded regulations")
    if loaded_files:
        for f in loaded_files:
            st.write(f"📄 {f}")
    else:
        st.warning(
            "No PDFs found in the `docs/` folder. Add your FIA regulation PDFs "
            "there and redeploy."
        )
    st.divider()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about the FIA regulations..."):
    if not regs_text:
        st.error("No regulations loaded — add PDFs to the docs/ folder first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = get_client()
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(regs_text=regs_text)

    api_messages = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=2000,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=api_messages,
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Error calling Claude API: {e}"
            placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
