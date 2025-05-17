# 🧪 MixUp_BOSS : Grammar Error Correction Promptathon

본 레포지토리는 Grammar Error Correction Promptathon 실험을 재현하고 확장하기 위한 코드 및 가이드를 제공합니다.

## 📌 프로젝트 개요

- **목표**: ex. Solar Pro API를 활용하여 프롬프트 만으로 한국어 맞춤법 교정 성능을 개선한다.
- **접근 전략**:
  한국어 오류 유형 & Few-shot 예시 제공 -> Function 구조 프롬프트 & Multi-turn 형식 사용 -> Self-consistency & Reranking 방식 사용

- **주요 실험 내용**:

1. 한국어 오류 유형 분석 & 실제 많이 발생하는 오류 유형 수집
2. 프롬프트에게 제공할 오류 유형 & Few-shot 예시 결정
3. 명확하고 구체적인 지침을 주기 위한 Function call 구조 & Multi - turn도입
4. 2개의 방식으로 API 호출 및 결과물 중간 생성 & 이를 입력으로 평가하여 최종 출력 문장 판단

---

## ⚙️ 환경 세팅 & 실행 방법

### 1. 사전 준비

```bash
git clone https://github.com/lkj626/Upstage_GEC_Promptathon.git
cd Upstage_GEC_Promptathon
```

### 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 실험 실행

```bash
python -m code.main
```

> 📎 생성 파일 및 생성 경로:
> code/ 경로에 submission_compare.csv 이 생성됩니다.

---

## 🚧 실험의 한계 및 향후 개선

- **한계**:

  - 2개의 Prompt 활용을 통한 Prompt Token
  - 1개의 case 처리시에 3번의 API call 에 따른 성능과 비용 간의 trade-off

- **향후 개선 방향**:
  - 단일 프롬프트 방식으로 변경
  - 다른 Prompt 기법을 사용해 API call 횟수 감소

---

## 📂 폴더 구조

```
📁 code/
├── main.py              # 메인 실행 파일
├── config.py            # 설정 파일
├── requirements.txt     # 필요한 패키지 목록
├── __init__.py         # 패키지 초기화 파일
├── utils/              # 유틸리티 함수들
│   ├── __init__.py     # utils 패키지 초기화
│   ├── experiment.py   # 실험 실행 및 API 호출
│   └── metrics.py      # 평가 지표 계산
└── prompts/            # 프롬프트 템플릿 저장
    ├── __init__.py     # prompts 패키지 초기화
    └── templates.py    # 프롬프트 템플릿 정의
```
