"""에너지 빈곤 해결을 위한 AI 기반 국가 복지 정책 추천 웹앱."""

import streamlit as st

from utils.calculations import HouseholdInput, REGIONS
from utils.ui_helpers import apply_custom_css, household_to_dict, init_session_state

st.set_page_config(
    page_title="에너지 복지 정책 추천",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
init_session_state()

st.markdown('<p class="main-header">⚡ 에너지 복지 정책 추천 시스템</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">가구 정보를 입력하면 AI가 적합한 국가 에너지 복지 정책을 추천하고 절감 효과를 예측합니다.</p>',
    unsafe_allow_html=True,
)

st.markdown("---")
st.subheader("① Information Input — 가구 정보 입력")

col1, col2 = st.columns(2)

with col1:
    monthly_income = st.number_input(
        "월평균 소득 (원)",
        min_value=0,
        value=2_000_000,
        step=100_000,
        help="가구의 월평균 총 소득을 입력하세요.",
    )
    household_size = st.number_input(
        "가구원 수 (명)",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    )
    region = st.selectbox("주소 (지역)", REGIONS, index=0)
    monthly_electric = st.number_input(
        "월평균 전기요금 (원)",
        min_value=0,
        value=80_000,
        step=5_000,
    )

with col2:
    monthly_fuel = st.number_input(
        "월평균 연료비 (원)",
        min_value=0,
        value=100_000,
        step=5_000,
        help="난방·가스·기름 등 연료 비용",
    )
    monthly_water = st.number_input(
        "월평균 수도요금 (원) — 선택",
        min_value=0,
        value=20_000,
        step=1_000,
    )
    monthly_consumption = st.number_input(
        "월평균 에너지 소비량 (kWh) — 선택",
        min_value=0.0,
        value=350.0,
        step=10.0,
        help="입력하지 않으면 비용 기반으로 추정합니다.",
    )

household = HouseholdInput(
    monthly_income=monthly_income,
    household_size=household_size,
    region=region,
    monthly_electric=monthly_electric,
    monthly_fuel=monthly_fuel,
    monthly_water=monthly_water,
    monthly_energy_consumption=monthly_consumption if monthly_consumption > 0 else None,
)

st.markdown("---")
st.subheader("자동 계산 결과")

m1, m2, m3, m4 = st.columns(4)
m1.metric("총 에너지 비용", f"{household.total_energy_cost:,.0f}원/월")
m2.metric("소득 대비 에너지 지출 비율", f"{household.energy_ratio * 100:.1f}%")
m3.metric(
    "에너지빈곤 여부",
    "⚠️ 해당" if household.is_energy_poor else "✅ 해당 없음",
)
m4.metric("가구원당 에너지비", f"{household.total_energy_cost / household.household_size:,.0f}원")

if household.is_energy_poor:
    st.markdown(
        '<div class="info-box">⚠️ 소득 대비 에너지 지출 비율이 10% 이상입니다. '
        "에너지빈곤 위험에 해당할 수 있으며, 국가 복지 정책 지원을 적극 검토해 보세요.</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

if st.button("🔍 추천 결과 보기", type="primary", use_container_width=True):
    if monthly_income <= 0:
        st.error("월평균 소득을 입력해 주세요.")
    elif monthly_electric + monthly_fuel <= 0:
        st.error("전기요금 또는 연료비를 입력해 주세요.")
    else:
        st.session_state["household"] = household
        st.session_state["household_dict"] = household_to_dict(household)
        st.session_state["input_complete"] = True
        st.session_state["recommendations"] = None
        st.session_state["savings"] = None
        st.session_state["forecast"] = None
        st.success("입력이 완료되었습니다. 왼쪽 메뉴에서 **AI Recommendation** 페이지로 이동하세요.")
        st.balloons()

if st.session_state.get("input_complete"):
    st.info("✅ 가구 정보가 저장되었습니다. 사이드바에서 **AI Recommendation** 페이지로 이동해 추천 결과를 확인하세요.")

with st.sidebar:
    st.markdown("### 📋 사용 안내")
    st.markdown(
        """
        1. **Information Input** — 가구 정보 입력
        2. **AI Recommendation** — AI 정책 추천
        3. **Result Summary** — 결과 요약 및 다운로드
        4. **Energy Information** — 에너지 정보
        """
    )
    st.markdown("---")
    st.caption("에너지경제연구원 · 정책브리핑 · NKIS 데이터 기반")
