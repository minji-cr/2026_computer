"""에너지 정보 제공 페이지."""

import plotly.express as px
import streamlit as st

from utils.data_loader import load_energy_news, load_energy_stats, load_policies
from utils.ui_helpers import apply_custom_css, init_session_state

st.set_page_config(page_title="Energy Information", page_icon="📚", layout="wide")

apply_custom_css()
init_session_state()

st.markdown('<p class="main-header">📚 Energy Information</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">에너지 빈곤 현황, 국가 복지 정책, 최신 뉴스 및 통계를 제공합니다.</p>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs([
    "에너지 빈곤 개념",
    "국가 에너지 복지 정책",
    "에너지 통계",
    "최신 에너지 뉴스",
])

with tab1:
    st.subheader("에너지 빈곤이란?")
    st.markdown(
        """
        **에너지 빈곤(Energy Poverty)** 은 가구가 적정 수준의 에너지 서비스를 이용하기에
        소득 대비 에너지 비용 부담이 과도한 상태를 말합니다.

        ### 주요 판단 기준
        - **에너지지출비율**: 가구 소득 대비 에너지 비용 비율이 **10% 이상**이면 에너지빈곤 위험
        - **에너지 접근성**: 난방·냉방·조명 등 필수 에너지 서비스 이용 제약 여부
        - **에너지 효율**: 주거 환경의 단열·설비 노후로 인한 과다 소비

        ### 우리나라 에너지 빈곤 현황
        - 에너지경제연구원에 따르면, 국내 에너지빈곤 가구 비율은 약 **7~8%** 수준
        - 저소득층의 에너지지출비율은 평균 **12% 이상**으로 전체 평균의 2배
        - 겨울철 난방비 부담으로 계절적 에너지빈곤이 심화
        - 1인 가구, 고령 가구, 임차 가구에서 에너지빈곤 비율이 높음

        ### 에너지 빈곤의 영향
        - 건강 악화 (저체온증, 결핵 등)
        - 교육·사회활동 제약
        - 가계 부채 증가
        - 에너지 절약을 위한 위험한 행동 (난방 축소 등)
        """
    )

    st.info(
        "출처: 에너지경제연구원 「에너지빈곤 지표 비교분석 및 정책 활용방안 연구」, "
        "대한민국 정책브리핑, 국가정책연구포털(NKIS)"
    )

with tab2:
    st.subheader("국가 에너지 복지 정책 소개")
    policies_df = load_policies()

    for _, policy in policies_df.iterrows():
        with st.expander(f"📋 {policy['policy_name']} ({policy['category']})"):
            st.markdown(f"**지원 대상:** {policy['eligibility_desc']}")
            st.markdown(f"**지원 내용:** {policy['support_content']}")
            st.markdown(f"**신청 방법:** {policy['application_method']}")
            if policy["electric_discount_rate"] > 0:
                st.markdown(f"- 전기요금 할인율: **{policy['electric_discount_rate']*100:.0f}%**")
            if policy["fuel_discount_rate"] > 0:
                st.markdown(f"- 연료비 할인율: **{policy['fuel_discount_rate']*100:.0f}%**")
            if policy["monthly_support_amount"] > 0:
                st.markdown(f"- 월 지원금: **{policy['monthly_support_amount']:,.0f}원**")

    st.subheader("저소득층 지원 제도 안내")
    st.markdown(
        """
        | 제도 | 주요 대상 | 지원 내용 |
        |------|----------|----------|
        | 에너지바우처 | 기준중위소득 60% 이하 | 연간 에너지 구매비 지원 |
        | 기초생활수급자 전기할인 | 기초수급 가구 | 전기요금 30% 할인 |
        | 차상위계층 전기할인 | 차상위계층 | 전기요금 20% 할인 |
        | 취약계층 난방비 지원 | 기준중위소득 50% 이하 | 난방비 월 최대 5만원 |
        | 에너지효율개선 사업 | 저소득·취약 가구 | LED·단열재 무료 교체 |

        **신청 경로:** [복지로(bokjiro.go.kr)](https://www.bokjiro.go.kr) · 주민센터 · 한국전력 고객센터(123)
        """
    )

with tab3:
    st.subheader("에너지 관련 통계")
    stats_df = load_energy_stats()

    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        ratio_data = stats_df[stats_df["indicator"].str.contains("에너지지출비율|에너지빈곤")]
        if not ratio_data.empty:
            fig1 = px.bar(
                ratio_data,
                x="indicator",
                y="value",
                color="year",
                title="에너지빈곤·지출비율 추이",
                labels={"value": "비율 (%)", "indicator": "지표"},
                barmode="group",
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        cost_data = stats_df[stats_df["indicator"].str.contains("전기요금|난방연료비")]
        if not cost_data.empty:
            fig2 = px.pie(
                cost_data,
                names="indicator",
                values="value",
                title="월평균 에너지 비용 구성 (2024)",
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("전국 에너지 빈곤 현황")
    region_data = {
        "지역": ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
                "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"],
        "에너지빈곤율(%)": [5.2, 9.1, 10.3, 7.8, 11.2, 8.5, 7.1, 4.8,
                          6.9, 12.5, 9.8, 10.1, 11.8, 13.2, 11.5, 10.7, 8.9],
    }
    import pandas as pd
    region_df = pd.DataFrame(region_data)
    fig_bar = px.bar(
        region_df.sort_values("에너지빈곤율(%)", ascending=True),
        x="에너지빈곤율(%)",
        y="지역",
        orientation="h",
        title="지역별 에너지빈곤율 비교",
        color="에너지빈곤율(%)",
        color_continuous_scale="Reds",
    )
    fig_bar.update_layout(height=500)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.caption("※ 지역별 수치는 에너지경제연구원 보고서 및 지표누리 자료 기반 추정치입니다.")

with tab4:
    st.subheader("최신 에너지 뉴스")
    news_list = load_energy_news()

    if news_list:
        for item in news_list:
            st.markdown(f"- 📰 {item}")
    else:
        st.info("뉴스 데이터를 불러올 수 없습니다. 인터넷 연결을 확인해 주세요.")

    st.markdown("---")
    st.markdown(
        """
        **참고 자료**
        - [에너지경제연구원](https://www.keei.re.kr)
        - [대한민국 정책브리핑](https://www.korea.kr)
        - [국가정책연구포털 (NKIS)](https://www.nkis.re.kr)
        - [지표누리](https://www.index.go.kr)
        - [복지로](https://www.bokjiro.go.kr)
        """
    )
