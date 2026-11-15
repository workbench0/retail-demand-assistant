import os
import time
import pandas as pd
import plotly.express as px
import streamlit as st
from src import service as sv, llm_tools as lt
from src.ui import product_picker

MAX_USER_MESSAGES = 15
art = sv.artifacts()


def api_key():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return None


def _typing(text):
    for w in text.split(" "):
        yield w + " "
        time.sleep(0.015)


def render_extras(trace, prefix):
    """Tool chips, small visuals built from the tool results, and the raw results."""
    if not trace:
        return
    names = []
    for t in trace:
        if t.get("tool") not in names:
            names.append(t.get("tool"))
    st.markdown('<div class="chips">' + "".join(f'<span class="chip">⚙ {n}</span>' for n in names) + "</div>",
                unsafe_allow_html=True)
    for j, t in enumerate(trace):
        out, name, key = t.get("output") or {}, t.get("tool"), f"viz_{prefix}_{j}"
        if not isinstance(out, dict) or "error" in out:
            continue
        if name == "get_product_forecast" and out.get("daily"):
            d = pd.DataFrame(out["daily"])
            fig = px.line(d, x="date", y=["lightgbm", "seasonal_naive"], title=f"{out['product_id']}: forecast",
                          labels={"value": "units/day", "date": ""})
            fig.update_layout(height=300)
            st.plotly_chart(fig, width="stretch", key=key)
        elif name == "get_products_at_risk" and out.get("at_risk"):
            cols = st.columns(4)
            for i, r in enumerate(out["at_risk"][:8]):
                day = int(r["first_stockout_day"])
                status = "red" if day <= 7 else "amber"
                cols[i % 4].markdown(
                    f'<div class="tile"><span class="dot {status}"></span><span class="id">{r["product_id"]}</span>'
                    f'<div class="d">Day {day}</div><div class="sub">stock {int(r["current_stock_units"])} &middot; '
                    f'order {int(r["suggested_order_units"])}</div></div>', unsafe_allow_html=True)
        elif name == "get_top_replenishment" and out.get("products"):
            d = pd.DataFrame(out["products"]).sort_values("suggested_order_units")
            fig = px.bar(d, x="suggested_order_units", y="product_id", orientation="h",
                         title="Suggested order (units)", labels={"suggested_order_units": "units", "product_id": ""})
            fig.update_layout(height=300)
            st.plotly_chart(fig, width="stretch", key=key)
    with st.expander("Underlying tool results"):
        st.json(trace)


def clear_chat():
    st.session_state["chat"] = []


key = api_key()
status = "Connected" if key else "Offline: the dashboard fallback below still works"
st.markdown(f'<div class="aihero"><div class="st"><span class="livedot {"on" if key else "off"}"></span>{status}</div>'
            '<h1>Ask your inventory anything</h1>'
            '<p>Every number comes from a tool call into the same functions as the dashboard. '
            'The chips under each answer show exactly which tools were used.</p></div>', unsafe_allow_html=True)

pid = product_picker("Product context for the assistant")
saved = st.session_state.get("_saved_inputs", {})
scn = saved.get(pid)
st.markdown(f'<div class="chips"><span class="chip">Product: {pid}</span>'
            f'<span class="chip">Inputs: {"your saved scenario" if scn else "demo defaults"}</span>'
            f'<span class="chip">Forecast starts {art["forecast_start"]}</span>'
            '<span class="chip">Historical demo data</span></div>', unsafe_allow_html=True)
if scn:
    st.json(scn, expanded=False)

with st.expander("Get the same numbers without the assistant"):
    st.caption("These use the same functions the assistant's tools call.")
    h = st.slider("At-risk horizon (days)", 1, 28, 7)
    risk = sv.get_products_at_risk(h, saved)
    st.write(f"{risk['n_at_risk']} product(s) may run out within {h} days (stock on order excluded).")
    if risk["at_risk"]:
        st.dataframe(pd.DataFrame(risk["at_risk"]), hide_index=True, width="stretch")
    st.json(sv.get_inventory_recommendation(pid, scn), expanded=False)

st.subheader("Try a question")
SUG = [("⏳", "Stockout risk", "Which products may run out within 7 days?", "Which products may run out within 7 days?"),
       ("📈", "Product forecast", f"28-day outlook for {pid}", f"What is the forecast for {pid}?"),
       ("🚚", "Delivery what-if", f"{pid} with a 10-day delivery", f"How much should I order for {pid} if delivery takes 10 days?"),
       ("📦", "Top replenishment", "The five biggest orders to place", "Which five products need the most replenishment?"),
       ("🎯", "Model performance", f"How well it did on {pid}", f"How well did the model perform for {pid}?"),
       ("🧮", "Explain the order", f"How the order for {pid} is calculated", f"Explain how the suggested order for {pid} is calculated.")]
for row in (SUG[:3], SUG[3:]):
    cols = st.columns(3)
    for col, (ic, title, desc, q) in zip(cols, row):
        with col:
            st.markdown(f'<div class="sug"><div class="ic">{ic}</div><b>{title}</b><span>{desc}</span></div>', unsafe_allow_html=True)
            if st.button("Ask this", key=f"sug_{title}", use_container_width=True):
                st.session_state["_pending"] = q

a, b = st.columns([5, 1])
a.subheader("Conversation")
b.button("Clear chat", on_click=clear_chat, use_container_width=True)

chat = st.session_state.setdefault("chat", [])
if not chat:
    st.markdown('<div class="empty">✨ Nothing here yet. Pick a card above or type a question below.</div>', unsafe_allow_html=True)
for i, m in enumerate(chat):
    with st.chat_message(m["role"], avatar="👤" if m["role"] == "user" else "✨"):
        st.markdown(m["content"])
        render_extras(m.get("trace"), f"h{i}")

prompt = st.chat_input("Ask about forecasts, inventory or model performance") or st.session_state.pop("_pending", None)
if prompt:
    n_user = sum(m["role"] == "user" for m in chat)
    if n_user >= MAX_USER_MESSAGES:
        st.warning(f"Session limit of {MAX_USER_MESSAGES} questions reached. Reload the page to start over.")
    elif not key:
        st.error("The assistant is not configured (no API key). The Forecast Explorer and Inventory Planner still work, "
                 "and the panel above shows the same numbers.")
    else:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        history = [{"role": m["role"], "content": m["content"]} for m in chat] + [{"role": "user", "content": prompt}]
        with st.chat_message("assistant", avatar="✨"):
            ph = st.empty()
            ph.markdown('<div class="typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)
            try:
                text, trace = lt.chat(history, key, lt.build_context(pid, scn, art), saved)
                ph.empty()
                st.write_stream(_typing(text))
                render_extras(trace, f"n{len(chat)}")
                chat += [{"role": "user", "content": prompt}, {"role": "assistant", "content": text, "trace": trace}]
            except Exception as e:
                ph.empty()
                st.error(f"The assistant is temporarily unavailable ({type(e).__name__}). Forecasts, the inventory "
                         "planner, and the panel above still work and give the same numbers.")
