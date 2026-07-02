"""결과 요약 및 다운로드 페이지."""

import streamlit as st

from utils.download import generate_csv_report, generate_pdf_report
from utils.ui_helpers import apply_custom_css, init_session_state

st.set_page_config(page_title="Result Summary", page_icon="📊", layout="wide")

apply_custom_css()
init_session_state()

st.markdown('<p class="main-header">📊 Result Summary</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">입력 정보, AI 추천 결과, 절감 효과를 한눈에 확인하고 다운로드할 수 있습니다.</p>',
    unsafe_allow_html=True,
)

if not st.session_state.get("input_complete"):
    st.warning("먼저 **Information Input** 페이지에서 가구 정보를 입력해 주세요.")
    st.stop()

household_dict = st.session_state.get("household_dict", {})
recommendations = st.session_state.get("recommendations")
savings = st.session_state.get("savings")

if recommendations is None:
    st.warning("**AI Recommendation** 페이지에서 AI 추천을 먼저 실행해 주세요.")
    st.stop()

st.subheader("사용자 입력 정보 요약")
c1, c2, c3 = st.columns(3)
c1.metric("월평균 소득", f"{household_dict.get('monthly_income', 0):,.0f}원")
c2.metric("가구원 수", f"{household_dict.get('household_size', 0)}명")
c3.metric("지역", household_dict.get("region", "-"))

c4, c5, c6 = st.columns(3)
c4.metric("월평균 전기요금", f"{household_dict.get('monthly_electric', 0):,.0f}원")
c5.metric("월평균 연료비", f"{household_dict.get('monthly_fuel', 0):,.0f}원")
c6.metric("월평균 수도요금", f"{household_dict.get('monthly_water', 0):,.0f}원")

st.markdown("---")
st.subheader("계산된 에너지 지표 요약")

m1, m2, m3 = st.columns(3)
m1.metric("총 에너지 비용", f"{household_dict.get('total_energy_cost', 0):,.0f}원/월")
m2.metric("에너지지출비율", f"{household_dict.get('energy_ratio', 0) * 100:.1f}%")
m3.metric(
    "에너지빈곤 여부",
    "해당" if household_dict.get("is_energy_poor") else "해당 없음",
)

st.markdown("---")
st.subheader("AI 추천 정책 요약")

for i, rec in enumerate(recommendations, 1):
    status = "✅ 지원 대상" if rec["eligible"] else "❌ 비대상"
    st.markdown(
        f"**{i}. {rec['policy_name']}** — 적합도 {rec['fitness']:.1f}% | {status}\n\n"
        f"- 추천 이유: {rec['reason']}\n"
        f"- 지원 내용: {rec['support_content']}"
    )

st.markdown("---")
st.subheader("예상 절감 효과 요약")

if savings:
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("적용 전 총 비용", f"{savings['original_total']:,.0f}원")
    s2.metric("적용 후 총 비용", f"{savings['predicted_total']:,.0f}원")
    s3.metric("월 절감 금액", f"{savings['savings_amount']:,.0f}원")
    s4.metric("절감률", f"{savings['savings_rate']:.1f}%")

    annual_savings = savings["savings_amount"] * 12
    st.success(f"연간 예상 절감액: **{annual_savings:,.0f}원**")
else:
    st.info("지원 대상 정책이 없어 절감 효과를 계산할 수 없습니다.")

st.markdown("---")
st.subheader("결과 다운로드")

col_csv, col_pdf = st.columns(2)

csv_data = generate_csv_report(household_dict, recommendations, savings or {})

with col_csv:
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv_data,
        file_name="energy_policy_recommendation.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col_pdf:
    try:
        pdf_data = generate_pdf_report(household_dict, recommendations, savings or {})
        st.download_button(
            label="📥 PDF 다운로드",
            data=pdf_data,
            file_name="energy_policy_recommendation.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception:
        st.warning("PDF 생성에 실패했습니다. CSV 다운로드를 이용해 주세요.")
