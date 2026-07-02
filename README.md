# 에너지 빈곤 해결을 위한 AI 기반 국가 복지 정책 추천 웹앱

저소득층 가구의 에너지 빈곤 문제 해결을 위해 AI가 적합한 국가 에너지 복지 정책을 추천하고, 정책 적용 후 예상 절감 효과를 예측하는 Streamlit 웹 애플리케이션입니다.

## 주요 기능

- **정보 입력**: 가구 소득, 인원, 지역, 에너지 비용 입력 및 자동 지표 계산
- **AI 정책 추천**: MLP 모델 기반 국가 복지 정책 적합도 예측
- **절감 효과 예측**: LSTM 모델 기반 정책 적용 전·후 비용 예측
- **결과 요약**: CSV/PDF 다운로드
- **에너지 정보**: 에너지 빈곤 개념, 정책 안내, 통계, 뉴스

## 기술 스택

- Python, Streamlit
- TensorFlow (Keras) — MLP, LSTM
- Pandas, NumPy, Plotly

## 설치 및 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. AI 모델 학습 (최초 1회)
python train_models.py

# 3. 웹앱 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속합니다.

## 페이지 구성

| 페이지 | 설명 |
|--------|------|
| Information Input | 가구 정보 입력 및 자동 계산 |
| AI Recommendation | MLP 정책 추천 + LSTM 절감 예측 |
| Result Summary | 결과 요약 및 CSV/PDF 다운로드 |
| Energy Information | 에너지 빈곤 정보, 정책, 통계, 뉴스 |

## 프로젝트 구조

```
├── app.py                      # 메인 (정보 입력)
├── train_models.py             # 모델 학습 스크립트
├── requirements.txt
├── data/
│   ├── policies.csv            # 국가 복지 정책 데이터
│   ├── energy_stats.csv        # 에너지 통계
│   └── energy_news.txt         # 에너지 뉴스
├── models/
│   ├── mlp_recommender.py      # MLP 정책 추천
│   └── lstm_predictor.py       # LSTM 비용 예측
├── pages/
│   ├── 2_AI_Recommendation.py
│   ├── 3_Result_Summary.py
│   └── 4_Energy_Information.py
└── utils/
    ├── calculations.py
    ├── data_loader.py
    ├── download.py
    └── ui_helpers.py
```

## 데이터 출처

- 에너지경제연구원 「에너지빈곤 지표 비교분석 및 정책 활용방안 연구」
- 대한민국 정책브리핑
- 국가정책연구포털 (NKIS)
- 지표누리

## 제한 사항

- 정책 정보 자동 업데이트 불가
- 실시간 정부 데이터 연동 불가
- 로그인 및 사용자 비교 기능 없음
