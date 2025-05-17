import os
import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from code.config import ExperimentConfig
from code.prompts.templates import TEMPLATES
from code.utils.experiment import ExperimentRunner

def main():
    # Load .env and get API key
    load_dotenv()
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("API 키가 없습니다. .env 파일에서 'UPSTAGE_API_KEY'를 확인하세요.")

    # Load data
    train = pd.read_csv("data/train.csv")
    test = pd.read_csv("data/test.csv")

    # 샘플링 및 분할
    toy_data = train.sample(n=1000, random_state=42).reset_index(drop=True)
    train_data, valid_data = train_test_split(toy_data, test_size=0.2, random_state=42)

    # 실험 구성
    config1 = ExperimentConfig(template_name="ToT", temperature=0.0)
    config2 = ExperimentConfig(template_name="pot", temperature=0.0)

    # 실험 실행
    runner = ExperimentRunner(config1, config2, api_key)
    result = runner.run_template_experiment(train_data, valid_data)

    # 테스트 예측
    print("\n=== 테스트 데이터 예측 시작 ===")
    test_results = runner.run(test)
    output = pd.DataFrame({
        'id': test['id'],
        'cor_sentence': test_results['cor_sentence']
    })
    output.to_csv("submission_compare.csv", index=False)
    print("\n제출 파일 생성 완료: submission_compare.csv")

if __name__ == "__main__":
    main()

