import html
import re
from typing import Optional

import streamlit as st

from pipeline import run_reserach_pipeline


st.set_page_config(
    page_title="MASS | Research Studio",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Content
# ---------------------------------------------------------------------------

# (key used by the pipeline callback, name, sidebar description, live status text)
STEPS = (
    ("search", "Search", "Finds reliable sources on your topic.", "Searching for reliable sources"),
    ("read", "Read", "Opens the strongest result and pulls out the details.", "Reading the strongest source"),
    ("write", "Write", "Drafts a detailed report from what it read.", "Drafting the report"),
    ("review", "Review", "A critic checks the report and points out what to improve.", "The critic is reviewing the report"),
)
STAGE_KEYS = tuple(step[0] for step in STEPS)
STAGE_STATUS = {step[0]: step[3] for step in STEPS}

EXAMPLES = (
    "How is AI changing medical diagnostics?",
    "Where do solid-state batteries stand today?",
    "How do new vaccines get approved?",
)

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700;12..96,800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap');

:root {
    --bg: #100C09;
    --surface: #1A1410;
    --raised: #261D16;
    --line: #3B2E24;
    --text: #F6EEE7;
    --text-soft: #DCCFC4;
    --muted: #A39384;
    --accent: #FF7A2F;
    --accent-rgb: 255, 122, 47;
    --crit: #5ED3C1;
    --crit-rgb: 94, 211, 193;
}

/* The block that carries this stylesheet should not take up space */
[data-testid="stElementContainer"]:has(style),
[data-testid="element-container"]:has(style) { display: none; }

/* ---- Base ---------------------------------------------------------------- */
.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'Bricolage Grotesque', system-ui, sans-serif;
    font-optical-sizing: auto;
}
.stApp button, .stApp input, .stApp textarea { font-family: inherit; }
.stApp [data-testid="stHeader"] { background: transparent; }
.stApp [data-testid="stAppDeployButton"], .stApp footer { display: none; }
.stApp .block-container { max-width: 1120px; padding: 2.75rem 2rem 5rem; }
.stApp * { scrollbar-color: #4A392C transparent; }

/* ---- Sidebar ------------------------------------------------------------- */
.stApp [data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--line);
}
.brand { display: flex; align-items: center; gap: .7rem; }
.brand-mark {
    display: grid; place-items: center;
    width: 2.4rem; height: 2.4rem;
    border-radius: 12px;
    background: var(--raised);
    border: 1px solid var(--line);
}
.brand-name { font-size: 1.4rem; font-weight: 800; letter-spacing: -.03em; }
.tagline { margin: .6rem 0 0; color: var(--muted); font-size: .95rem; }
.side-title { margin: 0 0 1rem; font-size: .95rem; font-weight: 600; }
.agents { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 1.15rem; }
.agent { --c: var(--accent); display: grid; grid-template-columns: 1.8rem 1fr; gap: .8rem; align-items: start; }
.agent.crit { --c: var(--crit); }
.agent-num {
    display: grid; place-items: center;
    width: 1.8rem; height: 1.8rem;
    border: 1.5px solid var(--c); border-radius: 50%;
    color: var(--c); font-size: .8rem; font-weight: 700;
}
.agent-name { font-size: .97rem; font-weight: 600; }
.agent-desc { margin-top: .15rem; color: var(--muted); font-size: .86rem; line-height: 1.5; }
.side-note { margin: 0; color: var(--muted); font-size: .84rem; line-height: 1.6; }

/* ---- Hero ---------------------------------------------------------------- */
.hero { margin: .25rem 0 1.75rem; }
.hero-title {
    max-width: 18ch;
    font-size: clamp(2.4rem, 5.4vw, 3.9rem);
    font-weight: 700;
    line-height: 1.03;
    letter-spacing: -.04em;
}
.hero-sub {
    max-width: 52ch;
    margin: 1.1rem 0 0;
    color: var(--muted);
    font-size: 1.1rem;
    line-height: 1.6;
}

/* ---- Prompt form --------------------------------------------------------- */
.stApp [data-testid="stForm"] {
    padding: .55rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 20px;
    transition: border-color .15s ease, box-shadow .15s ease;
}
.stApp [data-testid="stForm"]:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px rgba(var(--accent-rgb), .16);
}
.stApp [data-testid="stForm"] [data-testid="stHorizontalBlock"] { align-items: center; gap: .6rem; }
.stApp .stTextInput div[data-baseweb="input"],
.stApp .stTextInput div[data-baseweb="base-input"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
.stApp .stTextInput input {
    min-height: 3.2rem;
    padding: .85rem 1rem;
    background: transparent;
    color: var(--text);
    font-size: 1.12rem;
}
.stApp .stTextInput input::placeholder { color: #7A6B5E; opacity: 1; }
.stApp [data-testid="InputInstructions"] { color: var(--muted); }

.stApp [data-testid="stFormSubmitButton"] button {
    width: 100%;
    min-height: 3.2rem;
    border: 0;
    border-radius: 14px;
    background: var(--accent);
    color: #1A0D05;
    transition: background .15s ease, transform .15s ease;
}
.stApp [data-testid="stFormSubmitButton"] button p {
    color: #1A0D05; font-size: 1rem; font-weight: 700;
}
.stApp [data-testid="stFormSubmitButton"] button:hover {
    background: #FF9255; border: 0; color: #1A0D05;
}
.stApp [data-testid="stFormSubmitButton"] button:active { transform: translateY(1px); }
.stApp [data-testid="stFormSubmitButton"] button:focus-visible {
    outline: 2px solid var(--text); outline-offset: 2px;
}

/* ---- Example prompts ----------------------------------------------------- */
.chip-label { margin: .35rem 0 .6rem; color: var(--muted); font-size: .9rem; }
.stApp .stButton button {
    width: 100%;
    min-height: 2.9rem;
    padding: .55rem 1rem;
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 14px;
    transition: border-color .15s ease, background .15s ease;
}
.stApp .stButton button p {
    color: var(--text-soft); font-size: .92rem; font-weight: 500; line-height: 1.35; text-align: left;
}
.stApp .stButton button:hover { border-color: var(--accent); background: rgba(var(--accent-rgb), .1); }
.stApp .stButton button:hover p { color: var(--text); }
.stApp .stButton button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ---- Pipeline rail ------------------------------------------------------- */
.rail-wrap {
    margin: 1.4rem 0 1.1rem;
    padding: 1.45rem 1.6rem 1.3rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 20px;
}
.rail { display: flex; align-items: center; gap: .9rem; }
.rail-step { --c: var(--accent); --c-rgb: var(--accent-rgb); display: flex; align-items: center; gap: .6rem; flex: none; }
.rail-step.crit { --c: var(--crit); --c-rgb: var(--crit-rgb); }
.rail-node {
    display: grid; place-items: center;
    width: 2.1rem; height: 2.1rem;
    border: 1.5px solid var(--line); border-radius: 50%;
    color: var(--muted); font-size: .86rem; font-weight: 700;
}
.rail-name { color: var(--muted); font-size: .98rem; font-weight: 600; }
.rail-step.active .rail-node {
    border-color: var(--c); color: var(--c);
    animation: rail-pulse 1.7s ease-out infinite;
}
.rail-step.active .rail-name, .rail-step.done .rail-name { color: var(--text); }
.rail-step.done .rail-node { background: var(--c); border-color: var(--c); color: #1A0D05; }
.rail-link { flex: 1; height: 2px; min-width: 1rem; background: var(--line); border-radius: 2px; }
.rail-link.done { background: var(--accent); }
.rail-status { margin: 1.1rem 0 0; color: var(--muted); font-size: .93rem; }
@keyframes rail-pulse {
    0%   { box-shadow: 0 0 0 0 rgba(var(--c-rgb), .5); }
    100% { box-shadow: 0 0 0 11px rgba(var(--c-rgb), 0); }
}
@media (prefers-reduced-motion: reduce) {
    .rail-step.active .rail-node { animation: none; }
}
@media (max-width: 640px) {
    .rail-name { display: none; }
    .rail-step.active .rail-name { display: inline; }
    .rail-wrap { padding: 1.1rem; }
}

/* ---- Results ------------------------------------------------------------- */
.result-head { margin: 2rem 0 1.2rem; }
.status-pill {
    display: inline-flex; align-items: center; gap: .5rem;
    padding: .3rem .85rem;
    background: rgba(var(--accent-rgb), .14);
    border-radius: 999px;
    color: var(--accent); font-size: .84rem; font-weight: 600;
}
.status-pill i { width: .45rem; height: .45rem; border-radius: 50%; background: currentColor; }
.result-title {
    margin-top: .95rem;
    font-size: clamp(1.8rem, 3.6vw, 2.7rem);
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -.035em;
    overflow-wrap: anywhere;
}
.stats {
    display: grid; grid-template-columns: repeat(3, 1fr);
    margin: 1.3rem 0 1.7rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 16px;
}
.stat { padding: 1rem 1.35rem; }
.stat + .stat { border-left: 1px solid var(--line); }
.stat-label { display: block; color: var(--muted); font-size: .84rem; }
.stat-value { display: block; margin-top: .2rem; font-size: 1.3rem; font-weight: 700; letter-spacing: -.02em; }
.stat-value.crit { color: var(--crit); }
@media (max-width: 640px) {
    .stats { grid-template-columns: 1fr; }
    .stat + .stat { border-left: 0; border-top: 1px solid var(--line); }
}

/* Report + critic panels */
.stApp .st-key-panel_report,
.stApp .st-key-panel_critic {
    padding: 1.5rem 1.75rem 1.9rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 20px;
}
.stApp .st-key-panel_report { box-shadow: inset 3px 0 0 var(--accent); }
.stApp .st-key-panel_critic {
    background: #161915;
    border-color: rgba(var(--crit-rgb), .26);
    box-shadow: inset 3px 0 0 var(--crit);
}
.panel-title { margin: 0 0 .4rem; font-size: 1.08rem; font-weight: 700; letter-spacing: -.01em; }
.panel-title.report { color: var(--accent); }
.panel-title.critic { color: var(--crit); }

.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] :is(p, li),
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] :is(p, li) {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.1rem;
    line-height: 1.75;
    color: var(--text-soft);
}
.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] :is(h1, h2, h3, h4),
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] :is(h1, h2, h3, h4) {
    font-family: 'Bricolage Grotesque', system-ui, sans-serif;
    color: var(--text);
    letter-spacing: -.02em;
    line-height: 1.25;
    padding: 1.1rem 0 .3rem;
}
.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] h1,
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] h1 { font-size: 1.7rem; }
.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] h2,
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] h2 { font-size: 1.4rem; }
.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] h3,
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] h3 { font-size: 1.18rem; }
.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] strong,
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] strong { color: var(--text); font-weight: 600; }
.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] a { color: var(--accent); text-underline-offset: 3px; }
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] a { color: var(--crit); text-underline-offset: 3px; }
.stApp .st-key-panel_report li::marker { color: var(--accent); }
.stApp .st-key-panel_critic li::marker { color: var(--crit); }
.stApp .st-key-panel_report [data-testid="stMarkdownContainer"] blockquote,
.stApp .st-key-panel_critic [data-testid="stMarkdownContainer"] blockquote {
    border-left: 3px solid var(--line); color: var(--muted);
}

/* ---- Sources expander + tabs -------------------------------------------- */
.stApp [data-testid="stExpander"] {
    margin-top: 1.6rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 16px;
}
.stApp [data-testid="stExpander"] details { border: 0; background: transparent; }
.stApp [data-testid="stExpander"] summary { font-weight: 600; }
.stApp button[data-baseweb="tab"] p { font-weight: 600; }
.stApp [data-baseweb="tab-highlight"] { background: var(--accent); }
.stApp [data-baseweb="tab-border"] { background: var(--line); }

/* ---- Download + alerts --------------------------------------------------- */
.stApp [data-testid="stDownloadButton"] button {
    min-height: 3rem;
    padding: 0 1.4rem;
    background: transparent;
    border: 1px solid var(--line);
    border-radius: 14px;
    transition: border-color .15s ease, background .15s ease;
}
.stApp [data-testid="stDownloadButton"] button p { color: var(--text); font-weight: 600; }
.stApp [data-testid="stDownloadButton"] button:hover {
    border-color: var(--accent); background: rgba(var(--accent-rgb), .1);
}
.stApp [data-testid="stAlert"] { border-radius: 14px; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def sidebar_html() -> str:
    agents = "".join(
        f'<li class="agent{" crit" if key == "review" else ""}">'
        f'<span class="agent-num">{number}</span>'
        f'<div><div class="agent-name">{name}</div><div class="agent-desc">{desc}</div></div>'
        "</li>"
        for number, (key, name, desc, _) in enumerate(STEPS, start=1)
    )
    mark = (
        '<svg width="22" height="22" viewBox="0 0 32 32" fill="none" aria-hidden="true">'
        '<path d="M5 23 L12 12 L20 19 L27 7" stroke="#FF7A2F" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>'
        '<circle cx="5" cy="23" r="3" fill="#FF7A2F"/>'
        '<circle cx="12" cy="12" r="3" fill="#FF7A2F"/>'
        '<circle cx="20" cy="19" r="3" fill="#FF7A2F"/>'
        '<circle cx="27" cy="7" r="3" fill="#5ED3C1"/>'
        "</svg>"
    )
    return (
        f'<div class="brand"><span class="brand-mark">{mark}</span>'
        '<span class="brand-name">MASS</span></div>'
        '<p class="tagline">Research, distilled.</p>'
        '<hr style="border:0;border-top:1px solid #3B2E24;margin:1.4rem 0">'
        '<p class="side-title">How it works</p>'
        f'<ul class="agents">{agents}</ul>'
        '<hr style="border:0;border-top:1px solid #3B2E24;margin:1.4rem 0">'
        '<p class="side-note">A full run can take a minute or two while the agents gather and check sources.</p>'
    )


def rail_html(completed: set, active: Optional[str], running: bool) -> str:
    """Four-step pipeline rail. Idle: all steps dim. Running: live state."""
    if running and active is None:
        # Callback only reported completions so far; the next stage is the busy one.
        active = next((key for key in STAGE_KEYS if key not in completed), None)

    parts = []
    for index, (key, name, _, _) in enumerate(STEPS):
        if key in completed:
            state, glyph = "done", "✓"
        elif running and key == active:
            state, glyph = "active", str(index + 1)
        else:
            state, glyph = "", str(index + 1)
        crit = " crit" if key == "review" else ""
        current = ' aria-current="step"' if state == "active" else ""
        parts.append(
            f'<div class="rail-step {state}{crit}" role="listitem"{current}>'
            f'<span class="rail-node">{glyph}</span><span class="rail-name">{name}</span></div>'
        )
        if index < len(STEPS) - 1:
            link_state = "done" if key in completed else ""
            parts.append(f'<span class="rail-link {link_state}"></span>')

    if running and active:
        note = f"{STAGE_STATUS[active]}…"
    elif running:
        note = "Wrapping up…"
    else:
        note = "Each question passes through four steps, one after another."

    return (
        '<div class="rail-wrap" aria-live="polite">'
        f'<div class="rail" role="list" aria-label="Research progress">{"".join(parts)}</div>'
        f'<p class="rail-status">{note}</p>'
        "</div>"
    )


def panel(name: str):
    """Keyed container so each panel can be styled separately."""
    try:
        return st.container(key=f"panel_{name}")
    except TypeError:  # older Streamlit without `key` on containers
        return st.container(border=True)


def use_example(example: str) -> None:
    st.session_state["topic_input"] = example



def to_text(value) -> str:
    """Convert agent output into displayable text."""
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
                else:
                    parts.append(str(item))
            else:
                parts.append(str(item))
        return "\n".join(parts)

    if isinstance(value, dict):
        return str(value)

    return str(value)


def show_results(topic: str, results: dict) -> None:
    report = to_text(results.get("report"))
    feedback = to_text(results.get("feedback"))
    search_text = to_text(results.get("search_results"))
    scraped = to_text(results.get("scraped_content"))

    source_count = len(
        re.findall(r"(?im)^URL:\s*https?://", search_text)
    )
    word_count = len(report.split())

    st.markdown(
        '<div class="result-head">'
        '<span class="status-pill"><i></i>Research complete</span>'
        f'<div class="result-title" role="heading" aria-level="2">{html.escape(topic)}</div>'
        "</div>"
        '<div class="stats">'
        f'<div class="stat"><span class="stat-label">Sources found</span><span class="stat-value">{source_count}</span></div>'
        f'<div class="stat"><span class="stat-label">Report length</span><span class="stat-value">{word_count:,} words</span></div>'
        '<div class="stat"><span class="stat-label">Critic’s review</span><span class="stat-value crit">Complete</span></div>'
        "</div>",
        unsafe_allow_html=True,
    )

    report_col, review_col = st.columns([1.7, 1], gap="large")
    with report_col:
        with panel("report"):
            st.markdown('<div class="panel-title report">Research report</div>', unsafe_allow_html=True)
            st.markdown(report or "No report was returned.")
    with review_col:
        with panel("critic"):
            st.markdown('<div class="panel-title critic">Critic’s review</div>', unsafe_allow_html=True)
            st.markdown(feedback or "No review was returned.")

    with st.expander("See the sources behind this report"):
        search_tab, reading_tab = st.tabs(["Search results", "Detailed reading"])
        with search_tab:
            with st.container(height=420):
                st.markdown(search_text or "No search results returned.")
        with reading_tab:
            with st.container(height=420):
                st.markdown(scraped or "No scraped content returned.")

    download_content = (
        f"# {topic}\n\n"
        f"{report}\n\n"
        f"## Critic's review\n\n{feedback}\n"
    )
    safe_name = re.sub(r"[^a-zA-Z0-9-]+", "-", topic).strip("-").lower()
    st.markdown("")
    st.download_button(
        "Download report (.md)",
        data=download_content,
        file_name=f"{safe_name or 'research-report'}.md",
        mime="text/markdown",
    )


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)

st.markdown(
    '<div class="hero">'
    '<div class="hero-title" role="heading" aria-level="1">What do you want to find out?</div>'
    '<p class="hero-sub">MASS searches the web, reads the strongest source, writes a report, '
    "and has a critic check it.</p>"
    "</div>",
    unsafe_allow_html=True,
)

st.session_state.setdefault("topic_input", "")

with st.form("research_form"):
    field_col, action_col = st.columns([5, 1.3])
    with field_col:
        topic = st.text_input(
            "Research topic",
            key="topic_input",
            placeholder="e.g. How is AI changing medical diagnostics?",
            max_chars=500,
            label_visibility="collapsed",
        )
    with action_col:
        submitted = st.form_submit_button("Start research", type="primary")

rail_slot = st.empty()

if submitted:
    clean_topic = topic.strip()
    if not clean_topic:
        st.warning("Enter a research topic to get started.")
    else:
        completed_stages: set = set()
        active_stage = {"name": None}

        def update_progress(stage: str, status: str) -> None:
            if stage not in STAGE_KEYS:
                return
            if status == "complete":
                completed_stages.add(stage)
                if active_stage["name"] == stage:
                    active_stage["name"] = None
            else:
                active_stage["name"] = stage
            rail_slot.markdown(
                rail_html(completed_stages, active_stage["name"], running=True),
                unsafe_allow_html=True,
            )

        rail_slot.markdown(rail_html(set(), None, running=True), unsafe_allow_html=True)
        try:
            new_results = run_reserach_pipeline(clean_topic, update_progress)
        except Exception as exc:  # surface pipeline/API failures in the UI
            rail_slot.empty()
            st.error(
                "Research stopped before it finished. "
                "Check your API keys and internet connection, then try again."
            )
            with st.expander("Error details"):
                st.code(f"{type(exc).__name__}: {exc}")
            st.stop()

        st.session_state["research_results"] = new_results
        st.session_state["research_topic"] = clean_topic
        rail_slot.empty()

results = st.session_state.get("research_results")
if results:
    show_results(st.session_state["research_topic"], results)
else:
    rail_slot.markdown(rail_html(set(), None, running=False), unsafe_allow_html=True)
    st.markdown('<div class="chip-label">Or start from an example</div>', unsafe_allow_html=True)
    example_cols = st.columns(len(EXAMPLES))
    for index, (column, example) in enumerate(zip(example_cols, EXAMPLES)):
        with column:
            st.button(example, key=f"example_{index}", on_click=use_example, args=(example,))