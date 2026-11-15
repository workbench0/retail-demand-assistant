import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from src import service as sv

PALETTE = ["#C96442", "#2F4F4F", "#D9A441", "#7A8F6A", "#9C6B53", "#A89F94"]
FONT = '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif'
SERIF = '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif'

RANGE_BUTTONS = dict(
    buttons=[dict(count=1, label="1M", step="month", stepmode="backward"),
             dict(count=3, label="3M", step="month", stepmode="backward"),
             dict(count=6, label="6M", step="month", stepmode="backward"),
             dict(count=1, label="1Y", step="year", stepmode="backward"),
             dict(step="all", label="All")],
    bgcolor="#FFFFFF", activecolor="#F1DCCF", bordercolor="rgba(60,40,20,.15)", borderwidth=1,
    x=1, xanchor="right", y=1.02, yanchor="bottom")

CSS = """
<style>
.stApp, .stApp p, .stApp label, .stApp button, .stApp input, .stApp textarea,
[data-testid="stMarkdownContainer"] {font-family: __FONT__;}
.stApp h1, .stApp h2, .stApp h3 {font-family: __SERIF__; letter-spacing: -0.015em; color: #2B2622; font-weight: 600;}
.block-container {padding-top: 2rem; max-width: 1180px;}
.stDeployButton {display: none;}
@keyframes up {from {opacity: 0; transform: translateY(14px);} to {opacity: 1; transform: none;}}
@keyframes pulse {0% {box-shadow: 0 0 0 0 rgba(192,57,43,.5);} 70% {box-shadow: 0 0 0 9px rgba(192,57,43,0);} 100% {box-shadow: 0 0 0 0 rgba(192,57,43,0);}}
@keyframes pulseg {0% {box-shadow: 0 0 0 0 rgba(123,224,160,.7);} 70% {box-shadow: 0 0 0 9px rgba(123,224,160,0);} 100% {box-shadow: 0 0 0 0 rgba(123,224,160,0);}}
@keyframes bounce {0%,80%,100% {transform: translateY(0); opacity: .4;} 40% {transform: translateY(-6px); opacity: 1;}}
section[data-testid="stSidebar"] {border-right: 1px solid rgba(60,40,20,.10);}
[data-testid="stMetric"], .kpi {background: #fff; border: 1px solid rgba(60,40,20,.09); border-radius: 18px; padding: 16px 18px;
    box-shadow: 0 2px 12px rgba(60,40,20,.06); animation: up .6s both; transition: transform .25s, box-shadow .25s;}
[data-testid="stMetric"]:hover, .kpi:hover {transform: translateY(-3px); box-shadow: 0 12px 28px rgba(60,40,20,.12);}
[data-testid="stMetricLabel"] p {color: #7A6F66; font-size: .85rem;}
[data-testid="stMetricValue"] {font-size: 1.7rem; font-weight: 600; font-family: __SERIF__;}
.kpi .l {color: #7A6F66; font-size: .78rem; text-transform: uppercase; letter-spacing: .05em;}
.kpi .v {font-size: 1.4rem; font-weight: 600; margin-top: 2px;} .kpi .s {color: #7A6F66; font-size: .8rem;}
.ph {margin: 0 0 1.4rem 0; animation: up .6s both;}
.ph h1 {font-size: 2.6rem; font-weight: 600; margin: 0;}
.ph p {color: #7A6F66; font-size: 1.1rem; margin: .3rem 0 0 0;}
.fcard {border-radius: 22px; padding: 22px; height: 100%; background: #fff; border: 1px solid rgba(60,40,20,.09);
    box-shadow: 0 2px 12px rgba(60,40,20,.06); transition: transform .3s, box-shadow .3s; animation: up .7s both;}
.fcard:hover {transform: translateY(-6px); box-shadow: 0 18px 40px rgba(60,40,20,.14);}
.fcard .ic {width: 46px; height: 46px; border-radius: 14px; background: #F6E7DB; display: flex; align-items: center;
    justify-content: center; font-size: 1.5rem;}
.fcard h4 {margin: .8rem 0 .2rem 0; font-size: 1.1rem; font-weight: 600;}
.fcard p {margin: 0; color: #7A6F66; font-size: .92rem; line-height: 1.5;}
.big {border-radius: 24px; padding: 26px; text-align: center; background: #fff; border: 1px solid rgba(60,40,20,.09);
    box-shadow: 0 10px 34px rgba(60,40,20,.10); animation: up .5s both;}
.big .n {font-size: 4rem; font-weight: 600; line-height: 1; font-family: __SERIF__;
    background: linear-gradient(90deg,#C96442,#D9A441); -webkit-background-clip: text; background-clip: text; color: transparent;}
.big .t {color: #7A6F66; font-size: .92rem; margin-top: 8px;}
.tile {background: #fff; border: 1px solid rgba(60,40,20,.09); border-radius: 18px; padding: 14px 16px; margin-bottom: 14px;
    box-shadow: 0 2px 10px rgba(60,40,20,.05); transition: transform .25s, box-shadow .25s; animation: up .6s both;}
.tile:hover {transform: translateY(-4px); box-shadow: 0 14px 30px rgba(60,40,20,.14);}
.tile .id {font-size: .75rem; color: #7A6F66; font-weight: 500;}
.tile .d {font-size: 1.7rem; font-weight: 600; margin: 6px 0 2px 0; font-family: __SERIF__;}
.tile .sub {font-size: .78rem; color: #7A6F66;}
.dot {display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 6px;}
.dot.red {background: #C0392B; animation: pulse 1.8s infinite;} .dot.amber {background: #D9A441;} .dot.green {background: #5E8C61;}
.bar {height: 5px; border-radius: 3px; background: #EFE7DC; margin-top: 10px; overflow: hidden;}
.bar i {display: block; height: 100%; border-radius: 3px;}
.bar i.red {background: #C0392B;} .bar i.amber {background: #D9A441;} .bar i.green {background: #5E8C61;}
.stButton > button, .stDownloadButton > button {border-radius: 980px; font-weight: 500; padding: .5rem 1.2rem;
    border: 1px solid rgba(60,40,20,.18); background: #fff; transition: transform .2s, box-shadow .2s;}
.stButton > button:hover, .stDownloadButton > button:hover {transform: translateY(-2px); box-shadow: 0 6px 18px rgba(60,40,20,.12);}
button[data-testid="stBaseButton-primary"] {background: #C96442; color: #fff; border: 0; padding: .65rem 1.2rem;}
button[data-testid="stBaseButton-primary"]:hover {background: #B8573A; box-shadow: 0 8px 22px rgba(201,100,66,.38);}
[data-testid="stAlert"] {border-radius: 16px; border: 0;}
[data-testid="stDataFrame"] {border: 1px solid rgba(60,40,20,.10); border-radius: 14px; overflow: hidden;}
div[data-baseweb="select"] > div, .stNumberInput input {border-radius: 12px;}
[data-testid="stChatMessage"] {background: #fff; border: 1px solid rgba(60,40,20,.09); border-radius: 18px; box-shadow: 0 2px 10px rgba(60,40,20,.05);}
[data-testid="stChatInput"] {border-radius: 20px;}
.aihero {border-radius: 26px; padding: 28px 32px; margin-bottom: 1.2rem; color: #fff; animation: up .6s both;
    background: linear-gradient(135deg,#B4573A 0%,#C96442 50%,#D98A63 100%); box-shadow: 0 14px 40px rgba(201,100,66,.30);}
.stApp .aihero h1 {color: #fff; font-size: 2.3rem; margin: .5rem 0 .3rem 0;}
.stApp .aihero p {color: rgba(255,255,255,.88); font-size: 1.02rem; margin: 0; max-width: 640px;}
.aihero .st {font-size: .85rem; font-weight: 500; opacity: .95;}
.livedot {display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px;}
.livedot.on {background: #7BE0A0; animation: pulseg 1.8s infinite;} .livedot.off {background: #F2C2B3;}
.chips {margin: .4rem 0 .2rem 0;}
.chip {display: inline-block; padding: 4px 12px; margin: 4px 6px 0 0; border-radius: 999px; background: #F6E7DB; color: #8A4A2F;
    font-size: .78rem; font-weight: 500; border: 1px solid rgba(201,100,66,.25);}
.sug {background: #fff; border: 1px solid rgba(60,40,20,.09); border-radius: 20px; padding: 16px 18px; margin-bottom: 8px; min-height: 118px;
    box-shadow: 0 2px 10px rgba(60,40,20,.05); transition: transform .25s, box-shadow .25s; animation: up .6s both;}
.sug:hover {transform: translateY(-4px); box-shadow: 0 14px 30px rgba(60,40,20,.13);}
.sug .ic {font-size: 1.4rem;} .sug b {display: block; margin: .3rem 0 .15rem 0; font-size: 1rem;}
.sug span {color: #7A6F66; font-size: .86rem; line-height: 1.4;}
.empty {border: 1.5px dashed rgba(60,40,20,.22); border-radius: 20px; padding: 26px; text-align: center; color: #7A6F66; margin: 1rem 0;}
.typing span {display: inline-block; width: 8px; height: 8px; margin: 6px 3px; border-radius: 50%; background: #C96442; animation: bounce 1.2s infinite;}
.typing span:nth-child(2) {animation-delay: .15s;} .typing span:nth-child(3) {animation-delay: .3s;}
@media (prefers-reduced-motion: reduce) {* {animation: none !important;}}
</style>
""".replace("__FONT__", FONT).replace("__SERIF__", SERIF)


def _register_plotly_template():
    ax = dict(gridcolor="rgba(60,40,20,.07)", linecolor="rgba(60,40,20,.20)", zeroline=False, automargin=True,
              title=dict(standoff=12))
    pio.templates["retail"] = go.layout.Template(layout=dict(
        colorway=PALETTE, font=dict(family=FONT, color="#2B2622", size=13),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=ax, yaxis=ax,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=dict(text="")),
        margin=dict(l=20, r=20, t=80, b=40),
        title=dict(font=dict(size=17, family=SERIF), x=0, xanchor="left"),
        hoverlabel=dict(bgcolor="#FFFFFF", font_color="#2B2622"),
    ))
    pio.templates.default = "retail"


def _route_html():
    """Send st.markdown(..., unsafe_allow_html=True) through st.html, which renders HTML/CSS consistently."""
    if getattr(st.markdown, "_html_wrapped", False):
        return
    original = st.markdown

    def md(body, *args, **kwargs):
        if kwargs.pop("unsafe_allow_html", False):
            return st.html(body)
        return original(body, *args, **kwargs)

    md._html_wrapped = True
    st.markdown = md


def apply_style():
    _route_html()
    st.markdown(CSS, unsafe_allow_html=True)
    _register_plotly_template()
    if not getattr(st.plotly_chart, "_retail_wrapped", False):
        original = st.plotly_chart

        def wrapped(fig, *args, **kwargs):
            kwargs.setdefault("theme", None)
            kwargs.setdefault("config", {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
            try:
                fig.update_layout(legend_title_text="")
                if any(getattr(t, "type", "") == "scatter" for t in fig.data):
                    fig.update_layout(hovermode="x unified")
            except Exception:
                pass
            return original(fig, *args, **kwargs)

        wrapped._retail_wrapped = True
        st.plotly_chart = wrapped


def kpi(label, value, sub=""):
    st.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{value}</div>'
                f'<div class="s">{sub}</div></div>', unsafe_allow_html=True)


def page_header(title, sub=""):
    st.markdown(f'<div class="ph"><h1>{title}</h1><p>{sub}</p></div>', unsafe_allow_html=True)


def product_picker(label="Product"):
    prods = sv.products()
    cur = st.session_state.get("_product", prods[0])
    pid = st.selectbox(label, prods, index=prods.index(cur))
    st.session_state["_product"] = pid
    return pid
