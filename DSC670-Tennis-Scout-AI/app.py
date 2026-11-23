"""Tennis Scout AI: Streamlit front end for the fine-tuned Qwen2.5-0.5B scouting-report model.

The model was fully fine-tuned in Milestone 3 to read a fixed-format "stat card"
(one player on one surface, built from Match Charting Project data) and write a
six-section scouting report. This app feeds it stat cards exactly as in training.

Run:  streamlit run app.py
"""
import os
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---- Configuration: copy these from the Milestone 3 notebook -----------------
# Folder (or Hugging Face repo) holding the fine-tuned model saved in Milestone 3 (outputs/ft_model).
MODEL_PATH = os.getenv("MODEL_PATH", "outputs/ft_model")  # Colab: /content/drive/MyDrive/DSC670_ft_model
# Held-out players saved by Milestone 3 (has columns: key, player, surface, card, primary, secondary, report).
PROFILES_CSV = os.getenv("PROFILES_CSV", "outputs/test_profiles.csv")
# Exact SYSTEM_SHORT string from section 5 of the Milestone 3 notebook (the one-sentence training prompt).
SYSTEM_SHORT = os.getenv(
    "SYSTEM_SHORT",
    "You are a tennis scouting analyst. Write a coach-ready scouting report from the player profile in the standard format.",
)
MAX_NEW_TOKENS = 600  # same limit used in the notebook's evaluation
# -----------------------------------------------------------------------------

SECTIONS = ["PRIMARY ARCHETYPE:", "SECONDARY ARCHETYPE:", "PROFILE SUMMARY:",
            "STRENGTHS:", "WEAKNESSES:", "GAME PLAN FOR THE OPPONENT:"]
NUM = re.compile(r"\d+(?:\.\d+)?")

st.set_page_config(page_title="Tennis Scout AI", page_icon="🎾", layout="wide")


@st.cache_resource(show_spinner="Loading the fine-tuned model...")
def load_model(path: str):
    tok = AutoTokenizer.from_pretrained(path)
    dt = torch.float16 if torch.cuda.is_available() else torch.float32
    try:  # newer transformers use `dtype`; older ones use `torch_dtype`
        model = AutoModelForCausalLM.from_pretrained(path, dtype=dt)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=dt)
    if torch.cuda.is_available():
        model = model.to("cuda")
    model.eval()
    return tok, model


@st.cache_data
def load_profiles(path: str):
    return pd.read_csv(path) if Path(path).exists() else None


def generate_report(tok, model, card: str) -> str:
    msgs = [{"role": "system", "content": SYSTEM_SHORT}, {"role": "user", "content": card}]
    prompt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    enc = tok(prompt, return_tensors="pt", add_special_tokens=False).to(model.device)
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def split_sections(report: str) -> dict:
    """Split the report into its six labelled sections for display."""
    pos = [(report.find(s), s) for s in SECTIONS]
    found = sorted(p for p in pos if p[0] >= 0)
    out = {}
    for i, (start, label) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(report)
        out[label.rstrip(":")] = report[start + len(label):end].strip()
    return out


def grounding(report: str, card: str) -> float:
    """Share of numbers in the report that appear in the stat card (the notebook's 'numeric grounding')."""
    nums = NUM.findall(report)
    if not nums:
        return 1.0
    allowed = set(NUM.findall(card))
    return sum(n in allowed for n in nums) / len(nums)


# ---- Page ------------------------------------------------------------------
st.title("🎾 Tennis Scout AI")
st.caption("Fine-tuned Qwen2.5-0.5B-Instruct that turns a player's statistical profile into a coach-ready scouting report.")

with st.sidebar:
    st.header("Model")
    st.write(f"**Weights:** `{MODEL_PATH}`")
    st.write("**Base model:** Qwen/Qwen2.5-0.5B-Instruct, full fine-tune (no LoRA)")
    st.write("**Decoding:** greedy (deterministic), same as the evaluation")
    st.divider()
    st.caption("Data: Tennis Abstract Match Charting Project (Jeff Sackmann and volunteer charters), CC BY-NC-SA 4.0.")

tab_report, tab_custom, tab_about = st.tabs(["Scout a player", "Paste a stat card", "About"])

profiles = load_profiles(PROFILES_CSV)


def show_result(card: str, reference: str | None = None, label: str | None = None):
    try:
        tok, model = load_model(MODEL_PATH)
    except Exception as e:
        st.error(f"Could not load the model from `{MODEL_PATH}`: {e}")
        return
    with st.spinner("Writing the scouting report..."):
        report = generate_report(tok, model, card)
    if label:
        st.subheader(label)
    parts = split_sections(report)
    if len(parts) == len(SECTIONS):
        c1, c2 = st.columns(2)
        c1.metric("Primary archetype", parts["PRIMARY ARCHETYPE"].title())
        c2.metric("Secondary archetype", parts["SECONDARY ARCHETYPE"].title())
        st.markdown("**Profile summary**")
        st.write(parts["PROFILE SUMMARY"])
        s, w = st.columns(2)
        s.markdown("**Strengths**")
        s.markdown(parts["STRENGTHS"])
        w.markdown("**Weaknesses**")
        w.markdown(parts["WEAKNESSES"])
        st.markdown("**Game plan for the opponent**")
        st.markdown(parts["GAME PLAN FOR THE OPPONENT"])
    else:
        st.warning("The output did not follow the six-section format; showing it as written.")
        st.text(report)
    g = grounding(report, card)
    st.caption(f"Numeric grounding: {g:.0%} of numbers in the report appear in the stat card.")
    st.download_button("Download report (.txt)", report, file_name="scouting_report.txt")
    with st.expander("Stat card the model read"):
        st.code(card)
    if reference:
        with st.expander("Rule-based reference report (training-style target)"):
            st.text(reference)


with tab_report:
    if profiles is None:
        st.info(f"`{PROFILES_CSV}` not found. Copy `test_profiles.csv` from the Milestone 3 outputs next to this app, "
                "or use the 'Paste a stat card' tab.")
    else:
        left, right = st.columns([1, 2])
        with left:
            surface = st.selectbox("Surface", sorted(profiles["surface"].unique()))
            names = sorted(profiles.loc[profiles["surface"] == surface, "player"].unique())
            player = st.selectbox("Player (held-out test set)", names)
            row = profiles[(profiles["surface"] == surface) & (profiles["player"] == player)].iloc[0]
            st.caption("These players were never used in training or validation.")
            go = st.button("Generate scouting report", type="primary")
        with right:
            if go:
                show_result(row["card"], reference=row.get("report"), label=f"{player}, {surface}")
            else:
                st.info("Choose a player and surface, then generate.")

with tab_custom:
    st.write("Paste a stat card in the same format used for training (see the example in the expander below).")
    example = profiles["card"].iloc[0] if profiles is not None else ""
    card_text = st.text_area("Stat card", value="", height=260, placeholder=example)
    if st.button("Generate from pasted card", disabled=not card_text.strip()):
        show_result(card_text.strip())
    if example:
        with st.expander("Example stat card"):
            st.code(example)

with tab_about:
    st.markdown(
        """
## What this app does

Coaches prepare for opponents by reading statistics. This app takes a statistical profile of one player on one
surface and writes a scouting report with six sections: primary archetype, secondary archetype, profile summary,
strengths, weaknesses, and a game plan.

## How it works

1. **Data.** Shot-by-shot charting data is aggregated into one profile per player per surface (about 400 profiles).
2. **Stat card.** Each profile becomes a fixed-format text card with raw statistics and surface percentiles.
3. **Fine-tuning.** Qwen2.5-0.5B-Instruct was fully fine-tuned (all 494M weights) on 279 card-to-report examples.
4. **This app.** The same model and the same prompt format generate reports for players it never saw in training.

## Important limits

- The training reports and archetype labels come from transparent rules, not from tennis experts.
  The model learned that design, so its output reflects those rules.
- The model reliably follows the report format but often picks a different archetype than the rules do.
- The 0.5B model can be wrong. Check numbers against the stat card; the app shows a grounding score for this.
"""
    )
