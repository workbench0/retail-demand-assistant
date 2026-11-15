import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src import service as sv
from src.ui import product_picker, page_header

art = sv.artifacts()
page_header("Forecast Explorer", "Pick a horizon, drag the range slider, or press Play to watch the forecast unfold")
pid = product_picker()
tab_fc, tab_bt = st.tabs(["Forecast (after data cutoff)", "Historical backtest (actuals known)"])

with tab_fc:
    st.info(f"Sales data ends {art['training_cutoff']}. The forecast covers {art['forecast_start']} to "
            f"{art['forecast_end']}. No actual sales exist for these dates, and the dataset is historical, "
            "so this is a demo forecast, not a current prediction.")
    HZ = {"7 days": 7, "14 days": 14, "28 days": 28}
    HS = {"1 month": 30, "3 months": 90, "6 months": 180, "1 year": 365}
    c1, c2, c3 = st.columns([1, 1.3, 1])
    h = HZ[c1.segmented_control("Forecast horizon", list(HZ), default="28 days", key="fx_h") or "28 days"]
    n_hist = HS[c2.segmented_control("History shown", list(HS), default="6 months", key="fx_n") or "6 months"]
    show_base = c3.toggle("Show seasonal baseline", True, key="fx_base")

    fc, hist = sv.forecast_frame(pid, h), sv.history_frame(pid).tail(n_hist)
    fig = go.Figure()
    fig.add_scatter(x=hist.date, y=hist.units_sold, name="Historical sales (actual)", line=dict(color="#A89F94", width=1.5))
    fig.add_scatter(x=fc.date, y=fc.lightgbm_forecast, name="LightGBM forecast", line=dict(color="#C96442", width=3))
    idx = [1]
    if show_base:
        fig.add_scatter(x=fc.date, y=fc.seasonal_naive_forecast, name="Seasonal naive baseline",
                        line=dict(color="#2F4F4F", dash="dot", width=2))
        idx.append(2)
    frames = []
    for k in range(1, len(fc) + 1):
        data = [go.Scatter(x=fc.date.iloc[:k], y=fc.lightgbm_forecast.iloc[:k])]
        if show_base:
            data.append(go.Scatter(x=fc.date.iloc[:k], y=fc.seasonal_naive_forecast.iloc[:k]))
        frames.append(go.Frame(data=data, traces=idx, name=str(k)))
    fig.frames = frames
    cut = art["training_cutoff"]
    fig.add_shape(type="line", x0=cut, x1=cut, y0=0, y1=1, yref="paper", line=dict(dash="dash", color="#C0392B", width=1))
    fig.add_annotation(x=cut, y=1, yref="paper", text="data cutoff", showarrow=False, xanchor="right")
    fig.update_layout(
        yaxis_title="units/day", height=480,
        updatemenus=[dict(type="buttons", showactive=False, x=1, xanchor="right", y=1.02, yanchor="bottom",
                          buttons=[dict(label="▶  Play forecast", method="animate",
                                        args=[None, dict(frame=dict(duration=90, redraw=True),
                                                         transition=dict(duration=0), fromcurrent=True, mode="immediate")])])])
    fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.06))
    st.plotly_chart(fig, width="stretch")

    c = st.columns(2)
    c[0].metric(f"LightGBM total, {h} days", f"{fc.lightgbm_forecast.sum():.1f} units")
    c[1].metric(f"Seasonal naive total, {h} days", f"{fc.seasonal_naive_forecast.sum():.1f} units")
    out = fc[["product_id", "date", "lightgbm_forecast", "seasonal_naive_forecast"]].copy()
    out["date"] = out.date.dt.date
    st.dataframe(out.round(3), width="stretch", hide_index=True)
    st.download_button("Download forecast (CSV)", out.to_csv(index=False), f"forecast_{pid}.csv", "text/csv")
    st.caption("Forecasts are continuous expected values; negatives are clipped to 0. No uncertainty bands are shown "
               "because none were validated.")

with tab_bt:
    bt = sv.backtest_frame()
    bt = bt[bt.product_id == pid]
    split = st.segmented_control("Split", ["holdout", "validation"], default="holdout", key="bt_split") or "holdout"
    d = bt[bt.split == split]
    if split == "validation":
        origins = sorted(d.origin.unique())
        o = st.selectbox("Forecast origin", origins, format_func=lambda x: str(pd.Timestamp(x).date()))
        d = d[d.origin == o]
    st.info("Backtest: actual sales are known for these 28 days and were used only for scoring, never as model input.")
    fig = go.Figure()
    fig.add_scatter(x=d.date, y=d.actual, name="Actual", line=dict(color="#A89F94", width=2))
    fig.add_scatter(x=d.date, y=d.lgbm, name="LightGBM (recursive)", line=dict(color="#C96442", width=3))
    fig.add_scatter(x=d.date, y=d.baseline, name="Seasonal naive", line=dict(color="#2F4F4F", dash="dot", width=2))
    fig.update_layout(yaxis_title="units/day", height=420)
    st.plotly_chart(fig, width="stretch")
    m = sv.get_model_metrics(pid)
    st.dataframe(pd.DataFrame(m["metrics"]), width="stretch", hide_index=True)
    st.caption(f"{m['bias_sign_convention']}. WAPE blank = undefined (zero actual sales).")
    with st.expander("Raw tool output"):
        st.json(m, expanded=False)
