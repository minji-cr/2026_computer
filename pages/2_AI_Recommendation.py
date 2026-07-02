"""AI 기반 국가 복지 정책 추천 페이지."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from models.lstm_predictor import get_monthly_forecast, predict_cost_with_lstm
from models.mlp_recommender import recommend_policies
from utils.ui_helpers import apply_custom_css, init_session_state

st.set_page_config(page_title="AI Recommendation", page_icon="🤖", layout="wide")

apply_custom_css()
init_session_state()

st.markdown('<p class="main-header">🤖 AI Recommendation</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">MLP 모델이 가구 정보를 분석하여 적합한 국가 에너지 복지 정책을 추천합니다.</p>',
    unsafe_allow_html=True,
)

if not st.session_state.get("input_complete") or st.session_state.get("household") is None:
    st.warning("먼저 **Information Input** 페이지에서 가구 정보를 입력하고 '추천 결과 보기' 버튼을 클릭해 주세요.")
    st.stop()

household = st.session_state["household"]

if st.button("🔄 AI 추천 실행", type="primary") or st.session_state.get("recommendations") is None:
    with st.spinner("MLP 모델이 정책 적합도를 분석 중입니다..."):
        try:
            recommendations = recommend_policies(household, top_k=5)
            st.session_state["recommendations"] = recommendations

            eligible_recs = [r for r in recommendations if r["eligible"]]
            if eligible_recs:
                top_policy = eligible_recs[0]["policy"]
                with st.spinner("LSTM 모델이 정책 적용 후 비용을 예측 중입니다..."):
                    savings = predict_cost_with_lstm(household, top_policy)
                    forecast = get_monthly_forecast(household, top_policy)
                st.session_state["savings"] = savings
                st.session_state["forecast"] = forecast
                st.session_state["selected_policy"] = eligible_recs[0]
            else:
                st.session_state["savings"] = None
                st.session_state["forecast"] = None
        except Exception as e:
            st.error(f"AI 분석 중 오류가 발생했습니다. 인터넷 연결을 확인하고 다시 시도해 주세요.\n\n상세: {e}")
            st.stop()

recommendations = st.session_state.get("recommendations", [])

if not recommendations:
    st.info("추천 가능한 정책이 없습니다. 입력값을 다시 확인해 주세요.")
    st.stop()

eligible_count = sum(1 for r in recommendations if r["eligible"])
if eligible_count == 0:
    st.warning("현재 입력 조건에 맞는 지원 대상 정책이 없습니다. 소득·지역·에너지지출 정보를 재확인해 주세요.")

st.subheader("추천 정책 목록")

for i, rec in enumerate(recommendations, 1):
    badge_class = "eligible-badge" if rec["eligible"] else "ineligible-badge"
    badge_text = "지원 대상" if rec["eligible"] else "지원 비대상"

    st.markdown(
        f"""
        <div class="policy-card">
            <h4>{i}. {rec['policy_name']}
                <span class="{badge_class}">{badge_text}</span>
                <span style="float:right; color:#2e86c1; font-weight:bold;">적합도 {rec['fitness']:.1f}%</span>
            </h4>
            <p><b>분류:</b> {rec['category']} | <b>추천 이유:</b> {rec['reason']}</p>
            <p><b>지원 대상:</b> {rec['eligibility_desc']}</p>
            <p><b>지원 내용:</b> {rec['support_content']}</p>
            <p><b>신청 방법:</b> {rec['application_method']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.subheader("정책 적용 후 예상 절감 효과 (LSTM 예측)")

savings = st.session_state.get("savings")
forecast = st.session_state.get("forecast")
selected = st.session_state.get("selected_policy")

if savings and selected:
    st.info(f"최우선 추천 정책 **{selected['policy_name']}** 적용 시 예상 효과")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("예상 전기요금", f"{savings['predicted_electric']:,.0f}원")
    c2.metric("예상 연료비", f"{savings['predicted_fuel']:,.0f}원")
    c3.metric("절감 금액", f"{savings['savings_amount']:,.0f}원/월", delta=f"-{savings['savings_rate']:.1f}%")
    c4.metric("적용 후 총 비용", f"{savings['predicted_total']:,.0f}원")

    compare_df = pd.DataFrame({
        "항목": ["전기요금", "연료비", "총 에너지비"],
        "적용 전 (원)": [
            savings["original_electric"],
            savings["original_fuel"],
            savings["original_total"],
        ],
        "적용 후 (원)": [
            savings["predicted_electric"],
            savings["predicted_fuel"],
            savings["predicted_total"],
        ],
    })
    compare_df["절감액 (원)"] = compare_df["적용 전 (원)"] - compare_df["적용 후 (원)"]
    compare_df["절감률 (%)"] = (
        compare_df["절감액 (원)"] / compare_df["적용 전 (원)"] * 100
    ).round(1)

    col_table, col_chart = st.columns(2)

    with col_table:
        st.markdown("**비용 비교 표**")
        st.dataframe(
            compare_df.style.format({
                "적용 전 (원)": "{:,.0f}",
                "적용 후 (원)": "{:,.0f}",
                "절감액 (원)": "{:,.0f}",
                "절감률 (%)": "{:.1f}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with col_chart:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="적용 전",
            x=compare_df["항목"],
            y=compare_df["적용 전 (원)"],
            marker_color="#e74c3c",
        ))
        fig_bar.add_trace(go.Bar(
            name="적용 후",
            x=compare_df["항목"],
            y=compare_df["적용 후 (원)"],
            marker_color="#27ae60",
        ))
        fig_bar.update_layout(
            title="정책 적용 전·후 비용 비교",
            barmode="group",
            yaxis_title="금액 (원)",
            height=400,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    if forecast:
        forecast_df = pd.DataFrame(forecast)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=forecast_df["month"],
            y=forecast_df["before_total"],
            mode="lines+markers",
            name="적용 전",
            line=dict(color="#e74c3c", width=2),
        ))
        fig_line.add_trace(go.Scatter(
            x=forecast_df["month"],
            y=forecast_df["after_total"],
            mode="lines+markers",
            name="적용 후",
            line=dict(color="#27ae60", width=2),
        ))
        fig_line.update_layout(
            title="향후 6개월 에너지 비용 예측 (LSTM)",
            xaxis_title="기간",
            yaxis_title="총 비용 (원)",
            height=400,
        )
        st.plotly_chart(fig_line, use_container_width=True)

        fig_pie = go.Figure(go.Pie(
            labels=["절감 금액", "잔여 비용"],
            values=[savings["savings_amount"], savings["predicted_total"]],
            hole=0.4,
            marker_colors=["#27ae60", "#bdc3c7"],
        ))
        fig_pie.update_layout(title="월간 절감 효과 비율", height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("지원 대상 정책이 확인되면 LSTM 기반 절감 효과 예측이 표시됩니다.")
