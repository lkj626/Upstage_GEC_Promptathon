import os
import time
import pandas as pd
from tqdm import tqdm
from typing import Dict, List
import requests
from collections import Counter

from code.config import ExperimentConfig
from code.prompts.templates import TEMPLATES
from code.utils.metrics import evaluate_correction


class ExperimentRunner:
    def __init__(self, config1: ExperimentConfig, config2: ExperimentConfig, api_key: str):
        self.config1 = config1
        self.config2 = config2
        self.api_key = api_key
        self.template1 = TEMPLATES[config1.template_name]
        self.template2 = TEMPLATES[config2.template_name]
        self.api_url = config1.api_url
        self.model = config1.model
        self.temperature = config1.temperature
        self.rpm = 100
        self.min_interval = 60.0 / self.rpm
        self.max_retries = 5

        self.is_multiturn1 = isinstance(self.template1, list) and all("role" in t and "content" in t for t in self.template1)
        self.is_multiturn2 = isinstance(self.template2, list) and all("role" in t and "content" in t for t in self.template2)

    def _make_messages(self, template, text: str, context: dict = None) -> List[Dict[str, str]]:
        context = context or {}
        context["text"] = text
        messages = []
        if isinstance(template, list) and all("role" in t and "content" in t for t in template):
            messages = [{**m} for m in template[:-1]]
            messages.append({"role": "user", "content": text})
        else:
            for entry in template:
                content = entry["content"].format(**context)
                messages.append({"role": entry["role"], "content": content})
        return messages

    def _call_api_single(self, messages: List[Dict[str, str]], temperature: float = None) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature
        }
        for attempt in range(self.max_retries):
            try:
                resp = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get('Retry-After', 5))
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

    def _compare_candidates(self, cand1: str, cand2: str, original: str) -> str:
        comp_prompt = [
            {"role": "system", "content": "당신은 한국어 문장 평가 전문가입니다. 다음 두 교정안 중 원문을 더 정확히 교정한 문장을 고르세요. 이유 없이 '1' 또는 '2'만 답해주세요."},
            {"role": "user", "content": f"원문: {original}\n1) {cand1}\n2) {cand2}"}
        ]
        choice = self._call_api_single(comp_prompt, temperature=0.0)
        return cand1 if choice.strip() == '1' else cand2

    def _run_variant(self, template, is_multiturn, text: str) -> str:
        messages = self._make_messages(template, text)
        return self._call_api_single(messages)


    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        results = []
        for _, row in tqdm(data.iterrows(), total=len(data)):
            text = row['err_sentence']
            try:
                # 순차 실행: 템플릿1 → 템플릿2 → 비교
                cand1 = self._run_variant(self.template1, self.is_multiturn1, text)
                time.sleep(self.min_interval)  # RPM 제한 보호
                cand2 = self._run_variant(self.template2, self.is_multiturn2, text)
                time.sleep(self.min_interval)  # 다음 요청 전에 다시 대기

                best = self._compare_candidates(cand1, cand2, text)
                time.sleep(self.min_interval)

                results.append({
                    'id': row['id'],
                    'original': text,
                    'cor1': cand1,
                    'cor2': cand2,
                    'cor_sentence': best
                })
            except Exception as e:
                print(f"[ERROR] ID {row['id']} failed: {e}")
                results.append({
                    'id': row['id'],
                    'original': text,
                    'cor1': '',
                    'cor2': '',
                    'cor_sentence': ''
                })
        return pd.DataFrame(results)


    def run_template_experiment(self, train_data: pd.DataFrame, valid_data: pd.DataFrame) -> Dict:
        print("\n=== 템플릿 비교 실험 ===")

        print("\n[학습 데이터 실험]")
        train_results = self.run(train_data)
        train_recall = evaluate_correction(train_data, train_results)

        print("\n[검증 데이터 실험]")
        valid_results = self.run(valid_data)
        valid_recall = evaluate_correction(valid_data, valid_results)

        return {
            'train_recall': train_recall,
            'valid_recall': valid_recall,
            'train_results': train_results,
            'valid_results': valid_results
        }
