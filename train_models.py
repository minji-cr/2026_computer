"""MLP 및 LSTM 모델 학습 스크립트."""

from models.lstm_predictor import train_and_save_lstm
from models.mlp_recommender import train_and_save_mlp


def main():
    print("MLP 정책 추천 모델 학습 중...")
    train_and_save_mlp()
    print("MLP 모델 저장 완료.")

    print("LSTM 비용 예측 모델 학습 중...")
    train_and_save_lstm()
    print("LSTM 모델 저장 완료.")

    print("모든 모델 학습이 완료되었습니다.")


if __name__ == "__main__":
    main()
