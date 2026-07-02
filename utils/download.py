"""결과 다운로드 유틸리티."""

from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
from fpdf import FPDF


def generate_csv_report(
    household_data: dict,
    recommendations: list[dict],
    savings: dict,
) -> bytes:
    rows = []

    rows.append({"구분": "입력 정보", "항목": "월평균 소득", "값": f"{household_data['monthly_income']:,.0f}원"})
    rows.append({"구분": "입력 정보", "항목": "가구원 수", "값": f"{household_data['household_size']}명"})
    rows.append({"구분": "입력 정보", "항목": "지역", "값": household_data["region"]})
    rows.append({"구분": "입력 정보", "항목": "월평균 전기요금", "값": f"{household_data['monthly_electric']:,.0f}원"})
    rows.append({"구분": "입력 정보", "항목": "월평균 연료비", "값": f"{household_data['monthly_fuel']:,.0f}원"})
    rows.append({"구분": "계산 결과", "항목": "총 에너지 비용", "값": f"{household_data['total_energy_cost']:,.0f}원"})
    rows.append({"구분": "계산 결과", "항목": "에너지지출비율", "값": f"{household_data['energy_ratio']*100:.1f}%"})
    rows.append({"구분": "계산 결과", "항목": "에너지빈곤 여부", "값": "해당" if household_data["is_energy_poor"] else "해당 없음"})

    for i, rec in enumerate(recommendations, 1):
        rows.append({"구분": f"추천 정책 {i}", "항목": "정책명", "값": rec["policy_name"]})
        rows.append({"구분": f"추천 정책 {i}", "항목": "적합도", "값": f"{rec['fitness']:.1f}%"})
        rows.append({"구분": f"추천 정책 {i}", "항목": "지원 대상", "값": "대상" if rec["eligible"] else "비대상"})
        rows.append({"구분": f"추천 정책 {i}", "항목": "추천 이유", "값": rec["reason"]})

    if savings:
        rows.append({"구분": "절감 효과", "항목": "예상 절감 금액", "값": f"{savings['savings_amount']:,.0f}원/월"})
        rows.append({"구분": "절감 효과", "항목": "예상 절감률", "값": f"{savings['savings_rate']:.1f}%"})

    df = pd.DataFrame(rows)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue().encode("utf-8-sig")


def generate_pdf_report(
    household_data: dict,
    recommendations: list[dict],
    savings: dict,
) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font("NanumGothic", "", "C:/Windows/Fonts/malgun.ttf")
    pdf.set_font("NanumGothic", size=12)

    pdf.cell(0, 10, "에너지 복지 정책 추천 결과 보고서", ln=True, align="C")
    pdf.cell(0, 8, f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("NanumGothic", size=11)
    pdf.cell(0, 8, "[ 입력 정보 ]", ln=True)
    pdf.cell(0, 7, f"  월평균 소득: {household_data['monthly_income']:,.0f}원", ln=True)
    pdf.cell(0, 7, f"  가구원 수: {household_data['household_size']}명", ln=True)
    pdf.cell(0, 7, f"  지역: {household_data['region']}", ln=True)
    pdf.cell(0, 7, f"  월평균 전기요금: {household_data['monthly_electric']:,.0f}원", ln=True)
    pdf.cell(0, 7, f"  월평균 연료비: {household_data['monthly_fuel']:,.0f}원", ln=True)
    pdf.ln(3)

    pdf.cell(0, 8, "[ 에너지 지표 ]", ln=True)
    pdf.cell(0, 7, f"  총 에너지 비용: {household_data['total_energy_cost']:,.0f}원", ln=True)
    pdf.cell(0, 7, f"  에너지지출비율: {household_data['energy_ratio']*100:.1f}%", ln=True)
    status = "에너지빈곤 해당" if household_data["is_energy_poor"] else "에너지빈곤 해당 없음"
    pdf.cell(0, 7, f"  상태: {status}", ln=True)
    pdf.ln(3)

    pdf.cell(0, 8, "[ 추천 정책 ]", ln=True)
    for i, rec in enumerate(recommendations, 1):
        eligible = "대상" if rec["eligible"] else "비대상"
        pdf.cell(0, 7, f"  {i}. {rec['policy_name']} (적합도 {rec['fitness']:.1f}%, {eligible})", ln=True)
        pdf.cell(0, 7, f"     {rec['reason']}", ln=True)
    pdf.ln(3)

    if savings:
        pdf.cell(0, 8, "[ 절감 효과 (최우선 정책 적용 시) ]", ln=True)
        pdf.cell(0, 7, f"  예상 절감 금액: {savings['savings_amount']:,.0f}원/월", ln=True)
        pdf.cell(0, 7, f"  예상 절감률: {savings['savings_rate']:.1f}%", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()
