import streamlit as st

st.set_page_config(page_title="Retail Demand Assistant", page_icon="📦", layout="wide")

import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
from src import service as sv
from src.config import DEMO
from src.hero import build_hero
from src.ui import apply_style, RANGE_BUTTONS

apply_style()

try:
    art = sv.artifacts()
except Exception as e:
    st.error(f"Model artifacts could not be loaded: {e}. Run `python -m src.train` first.")
    st.stop()


def go_to(page):
    st.switch_page(page)


def open_planner():
    st.session_state["_product"] = st.session_state.get("board_pick", sv.products()[0])
    st.switch_page("pages/inventory_planner.py")


def risk_board():
    st.subheader("Stock runway board")
    st.caption("Demo stock values. Each tile shows the first forecast day when demand would exceed stock "
               "(stock on order excluded). Red = within 7 days, amber = within 14.")
    tbl = sv.inventory_table()
    mode = st.segmented_control("Filter", ["All", "At risk", "Healthy"], default="All", key="board_filter",
                                label_visibility="collapsed") or "All"
    rows = []
    for r in tbl.itertuples():
        d = None if pd.isna(r.first_stockout_day) else int(r.first_stockout_day)
        status = "red" if d is not None and d <= 7 else "amber" if d is not None and d <= 14 else "green"
        rows.append((r.product_id, d, status, int(r.suggested_order_units), int(r.current_stock_units)))
    if mode == "At risk":
        rows = [x for x in rows if x[2] != "green"]
    elif mode == "Healthy":
        rows = [x for x in rows if x[2] == "green"]
    rows.sort(key=lambda x: (x[1] is None, x[1] or 99))
    if not rows:
        st.info("No products in this group.")
    for i in range(0, len(rows), 5):
        cols = st.columns(5)
        for col, (pid, d, status, order, stock) in zip(cols, rows[i:i + 5]):
            big = f"Day {d}" if d else "No gap"
            width = 100 if d is None else max(6, int(d / 28 * 100))
            col.markdown(f'<div class="tile"><span class="dot {status}"></span><span class="id">{pid}</span>'
                         f'<div class="d">{big}</div><div class="sub">stock {stock} &middot; suggested order {order}</div>'
                         f'<div class="bar"><i class="{status}" style="width:{width}%"></i></div></div>',
                         unsafe_allow_html=True)
    a, b = st.columns([3, 1])
    a.selectbox("Open a product in the planner", sv.products(), key="board_pick", label_visibility="collapsed")
    b.button("Open in planner", key="open_planner", on_click=open_planner, use_container_width=True)


def overview():
    hist = sv.history_all()
    r = sv.reports()
    s, bp = r["summary"], r["by_product"]
    ho = s[s.split == "holdout"].set_index("model")
    gain = (1 - ho.loc["lgbm", "MAE"] / ho.loc["baseline", "MAE"]) * 100

    tot = hist.groupby("date").units_sold.sum().rolling(7).mean().dropna().tail(120).tolist()
    fc = pd.read_parquet(DEMO / "forecast_next28.parquet").groupby("date").lgbm.sum().sort_index().tolist()
    try:
        components.html(build_hero(hist.product_id.nunique(), art["horizon"], gain, tot, fc), height=540)
    except Exception:
        st.title("Retail Demand Forecasting & Inventory Planning")

    c = st.columns(3)
    with c[0]:
        st.button("Explore forecasts", type="primary", use_container_width=True, key="cta1",
                  on_click=go_to, args=("pages/forecast_explorer.py",))
    with c[1]:
        st.button("Plan inventory", type="primary", use_container_width=True, key="cta2",
                  on_click=go_to, args=("pages/inventory_planner.py",))
    with c[2]:
        st.button("Ask the AI assistant", type="primary", use_container_width=True, key="cta3",
                  on_click=go_to, args=("pages/ai_assistant.py",))
    st.caption("The dataset is historical (Walmart M5, ends May 2016). Forecasts are demonstrations on old data, not current "
               "predictions. Stock levels are demo or user-entered values.")

    st.write("")
    risk_board()

    st.write("")
    st.subheader("Try it live")
    st.caption("Move the sliders and watch the suggested order change. Uses demo stock values from the saved forecast.")
    left, right = st.columns([1.2, 1])
    with left:
        pid = st.selectbox("Product", sv.products(), key="try_pid")
        d = sv.default_inputs(pid)
        lead = st.slider("Delivery lead time (days)", 0, 14, 7, key="try_lead")
        stock = st.slider("Units in stock", 0, max(60, int(d["on_hand"]) * 3), int(d["on_hand"]), key=f"try_stock_{pid}")
    with right:
        try:
            rec = sv.get_inventory_recommendation(pid, {"on_hand": stock, "lead_time_days": lead}, source="demo_try_it")
            st.markdown(f'<div class="big"><div class="n">{rec["suggested_order_units"]}</div>'
                        f'<div class="t">suggested order, units<br>planning horizon {rec["planning_horizon_days"]} days '
                        f'&middot; demand {rec["forecast_demand_units"]:.1f}</div></div>', unsafe_allow_html=True)
            if rec["possible_stockout_before_replenishment"]:
                st.error(f"Possible stockout on forecast day {rec['first_stockout_day']}, before a new order would arrive "
                         f"(day {lead + 1}). Ordering more does not prevent this.")
            elif rec["first_stockout_day"]:
                st.warning(f"Demand exceeds stock on day {rec['first_stockout_day']}, after a new order would arrive.")
            else:
                st.success("No stockout in the 28-day forecast.")
        except ValueError as e:
            st.error(str(e))

    st.write("")
    st.subheader("What's inside")
    f = st.columns(4)
    cards = [("📈", "Forecast Explorer", "28-day LightGBM forecast vs a seasonal baseline, with an animated playback and CSV export."),
             ("📦", "Inventory Planner", "Stock, lead time and safety stock in, suggested order and stockout warning out."),
             ("🤖", "AI Assistant", "Plain-English answers; every number comes from a tool call you can inspect."),
             ("🧪", "Model Evaluation", "Honest metrics, baseline comparison and the products where the model loses.")]
    for col, (ic, t, tx) in zip(f, cards):
        col.markdown(f'<div class="fcard"><div class="ic">{ic}</div><h4>{t}</h4><p>{tx}</p></div>', unsafe_allow_html=True)

    st.write("")
    mae = bp[bp.split == "holdout"].pivot(index="product_id", columns="model", values="MAE")
    wins = int((mae["baseline"] < mae["lgbm"]).sum())
    st.subheader("Measured results (untouched 28-day holdout)")
    m = st.columns(4)
    m[0].metric("LightGBM MAE", f"{ho.loc['lgbm', 'MAE']:.2f} units/day")
    m[1].metric("Seasonal baseline MAE", f"{ho.loc['baseline', 'MAE']:.2f} units/day")
    m[2].metric("LightGBM WAPE", f"{ho.loc['lgbm', 'WAPE']:.2f}")
    m[3].metric("Baseline wins on", f"{wins} of {len(mae)} products")
    st.caption("Lower is better. LightGBM improves on the baseline overall but not on every product.")

    st.write("")
    st.subheader("Data at a glance")
    t1, t2, t3 = st.tabs(["Total sales", "Weekly pattern", "Products"])
    with t1:
        total = hist.groupby("date").units_sold.sum().to_frame("units")
        total["7-day average"] = total["units"].rolling(7).mean()
        fig = px.line(total, y=["units", "7-day average"], title="Total daily units (use the range buttons)",
                      labels={"value": "units", "date": ""})
        fig.update_xaxes(rangeselector=RANGE_BUTTONS,
                         range=[str(total.index[-365].date()), str(total.index[-1].date())])
        st.plotly_chart(fig, width="stretch")
    with t2:
        wd = hist.groupby(hist.date.dt.day_name()).units_sold.mean().reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        st.plotly_chart(px.bar(x=wd.index, y=wd.values, title="Average units per product by weekday",
                               labels={"x": "", "y": "units"}), width="stretch")
    with t3:
        a, b = st.columns(2)
        mean = hist.groupby("product_id").units_sold.mean().sort_values()
        zero = hist.groupby("product_id").units_sold.apply(lambda x: (x == 0).mean() * 100).sort_values()
        a.plotly_chart(px.bar(mean, orientation="h", title="Average daily units",
                              labels={"value": "units/day", "product_id": ""}), width="stretch")
        b.plotly_chart(px.bar(zero, orientation="h", title="Zero-sales days (%)",
                              labels={"value": "% of days", "product_id": ""}), width="stretch")
    st.caption("Zero-sales days are kept as genuine zeros. Low sales may reflect low demand or no stock; the data cannot tell which.")

    if st.button("Load / reset demo data"):
        for k in [k for k in st.session_state if str(k).startswith("inv_")]:
            del st.session_state[k]
        st.session_state.pop("_saved_inputs", None)
        st.success("Demo data loaded. Inventory scenarios reset to demo values.")


pg = st.navigation([
    st.Page(overview, title="Overview", default=True),
    st.Page("pages/forecast_explorer.py", title="Forecast Explorer"),
    st.Page("pages/inventory_planner.py", title="Inventory Planner"),
    st.Page("pages/ai_assistant.py", title="AI Assistant"),
    st.Page("pages/model_evaluation.py", title="Model Evaluation"),
])
st.sidebar.caption("Historical M5 demo data (to May 2016). Forecasts are demonstrations, not current predictions.")
pg.run()
