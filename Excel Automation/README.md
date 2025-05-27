
# 📊 Fine Tune Guide - SEO Status Unpivoting Script

이 저장소는 삼성전자 MX SEO 프로젝트의 SEO 상태 리포트를 *Unpivoting(세로화)*하여, 페이지별 점검 항목을 구조화된 형태로 가공하는 Python 스크립트를 포함하고 있습니다.  
대상 엑셀 파일은 `SEO Status with Fine tune Guide.xlsx`, 결과 파일은 `Fine Tune Guide - Unpivoting Result - PD.xlsx`로 저장됩니다.

---

## 📁 입력 파일 구조

- 엑셀 시트명: `Result`
- 상단 6줄은 메타 정보로 skip됨
- 주요 구성:
  - **기본 정보 (No. ~ Target URL)**: `B~H` 열
  - **점검 항목 정보 (Crawling Value 및 그 외)**: `N열` 이후

---

## 🔍 주요 처리 흐름

### 0. 엑셀 로드

```python
df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=6)
```

6행을 건너뛴 후 `Result` 시트에서 데이터 프레임을 로드합니다.

---

### 1. 기본 정보 전처리 (`result1`)

- `No.`부터 `Target URL`까지의 열을 추출하여 정제합니다.
- 첫 번째 행을 컬럼명으로 사용한 뒤, 이후 데이터만 추출하여 인덱스를 초기화합니다.

---

### 2. 점검 항목 데이터 전처리 (`result2`)

- `Crawling Value` 이후 열들을 복사
- 병합된 상단 2줄을 ffill(좌측으로 채움)로 정제
- 괄호 제거 + 상단/하단 헤더를 조합하여 다층 헤더를 단일 컬럼명으로 병합
- 4행 이후의 실제 데이터를 사용

---

### 3. 두 데이터 통합 (`one_two`)

- `result1`과 `result2_data`를 좌우 결합 (열 방향)
- 불필요한 Twitter_Card 관련 열 제거

---

### 4. 데이터 재구성 (Unpivoting)

- `meta_cols` (기본 정보)와 `audit_cols` (점검 항목)로 나누어 정의
- 각 페이지(행)마다 SEO 항목(`SEO Audit Element`)과 점검 기준(`Audit Standard`)을 분리
- 대응되는 Crawling Value 값은 `AS-IS (Issue)`로, 점검 결과는 `Result`로 저장
- 최종적으로 긴 형태(Long-form)의 DataFrame으로 변환

---

### 5. 액션 우선순위 정의

- 특정 SEO 항목별로 `"Must"`, `"Recommended"` 태그 지정
- 매핑되지 않은 항목은 공백 처리

---

## 💾 출력 파일

- 경로:  
  `C:\Users\User\Documents\업무\2025\삼성전자 MX SEO\Fine Tune Guide\Fine Tune Guide - Unpivoting Result - PD.xlsx`
- 출력 형태는 다음과 같습니다:

| No. | Region | Country | Target URL | SEO Audit Element | Audit Standard | AS-IS (Issue) | Result | Action Necessity |
|-----|--------|---------|-------------|--------------------|----------------|----------------|--------|------------------|

---

## 🔧 사용 패키지

- `pandas`
- `numpy`
- `re` (정규표현식 기반 텍스트 처리)

---

## 🧠 활용 목적

- SEO 점검 결과를 태그 단위로 파악 가능
- 향후 시각화, 필터링, 리포트 작성 시 유용
- 점검 항목별 우선순위 관리를 위한 기반 테이블 생성

---

## 📌 향후 개선 아이디어

- 누락된 점검 항목 자동 탐지
- AS-IS 기준 자동 분류 및 시각화
- Web 기반 인터페이스 연동 (Streamlit 등)
