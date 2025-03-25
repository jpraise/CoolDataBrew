# **📌 뉴스 및 소셜 미디어 기사 분석 프로젝트**  

## **📌 프로젝트 개요**  
이 프로젝트는 **뉴스 및 소셜 미디어 기사**를 분석하여 주요 **토픽(Topic)을 추출**하고,  
도메인 간 **전파 패턴, 영향력 있는 도메인 분석, 유사도 네트워크 그래프** 등을 시각화하는 **자동화된 분석 시스템**입니다.  

OpenAI GPT 및 **자연어 처리(NLP)** 기법을 활용하여 기사 데이터를 분석하고,  
**토픽 모델링, 영향력 있는 도메인 파악, 네트워크 기반 전파 분석**을 수행합니다.  

---

## **🚀 주요 기능**  
✅ **기사 데이터 전처리 및 텍스트 클리닝**  
✅ **LDA 토픽 모델링을 활용한 주요 토픽 추출**  
✅ **토픽별 주요 키워드 도출**  
✅ **기사 간 유사도를 측정하여 네트워크 그래프 생성**  
✅ **도메인별 토픽 분포 분석 및 영향력 있는 도메인 분석**  
✅ **시각화를 통한 데이터 분석 결과 제공**  
✅ **결과를 엑셀 파일(`fin_article_analysis.xlsx`)로 저장**  

---

## **🎯 활용 사례**  
🔹 **뉴스 및 소셜 미디어에서 특정 주제가 확산되는 방식 분석**  
🔹 **특정 도메인이 어떤 토픽을 주도하는지 파악**  
🔹 **도메인 간 정보 전파 네트워크 파악**  
🔹 **브랜드 및 기업의 미디어 노출 분석**  
🔹 **주요 키워드 및 트렌드 추출을 통한 마케팅 전략 수립**  

---

## **⚙️ 설치 및 실행 방법**  

### **1️⃣ 필수 라이브러리 설치**  
아래 명령어를 실행하여 프로젝트에 필요한 라이브러리를 설치하세요.

```bash
pip install numpy pandas matplotlib seaborn networkx nltk scikit-learn openpyxl
```

### **2️⃣ NLTK 데이터 다운로드**  
NLTK의 불용어(stopwords) 및 토큰화(tokenization) 데이터를 다운로드해야 합니다.

```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

### **3️⃣ 데이터 파일 준비**  
📂 분석할 **뉴스 및 소셜 미디어 기사 데이터**를 준비하세요.  
`english_data` 변수를 **실제 데이터 파일**로 교체하세요.

```python
df = english_data  # Replace with actual dataset
```

### **4️⃣ 코드 실행**  
다음 명령어를 실행하여 분석을 시작하세요.

```bash
python script.py
```

✅ **코드가 실행되면 뉴스 및 소셜 미디어 데이터를 분석하고, 최종 결과를 엑셀 파일(`fin_article_analysis.xlsx`)로 저장합니다.**

---

## **📊 출력 결과 (Excel 파일 및 시각화 자료)**  

### **📄 생성되는 파일**  
✅ **기사 데이터 및 분석 결과가 포함된 엑셀 파일 (`fin_article_analysis.xlsx`)**  
✅ **토픽별 키워드 및 도메인별 영향력 분석**  
✅ **기사 간 유사도 기반 네트워크 그래프**  
✅ **도메인별 토픽 확산 시각화 차트 저장**  

### **📌 엑셀 파일 구조 예시**  

| CreatedTime | Domain         | Title                        | Message                                       | Processed Text | Main Topic | InfluenceMetric | Keywords               |
|------------|---------------|-----------------------------|----------------------------------------------|---------------|------------|----------------|------------------------|
| 2024-03-15 | nytimes.com    | AI Revolution in Healthcare | "AI is transforming the medical field..."   | ai revolution | 2          | 89.5           | AI, Healthcare, Tech  |
| 2024-03-16 | bbc.com        | Climate Change Updates      | "Recent research shows alarming trends..."  | climate change | 1         | 72.1           | Climate, Earth, Green |
| 2024-03-17 | techcrunch.com | Future of Smartphones       | "Apple and Google are competing in AI..."   | future smartphones | 0  | 65.3 | Smartphones, AI, Market |

📌 **컬럼 설명**  
- `CreatedTime`: 기사 작성 시간  
- `Domain`: 해당 기사가 속한 도메인 (ex. `nytimes.com`, `bbc.com`)  
- `Title`: 기사 제목  
- `Message`: 기사 본문 요약  
- `Processed Text`: NLP 기반 전처리된 텍스트  
- `Main Topic`: 해당 기사가 속한 주요 토픽  
- `InfluenceMetric`: 기사 영향력 점수  
- `Keywords`: 해당 기사에서 추출된 주요 키워드  

---

## **📊 주요 분석 차트 소개**  

### **1️⃣ 토픽 확산 추이 (Topic Spread Over Time)**  
📌 **시간에 따른 각 토픽별 기사 누적 개수 변화**  
📌 **어떤 토픽이 특정 시기에 많이 언급되는지 확인 가능**  
📌 **도메인 간 전파 여부 확인 (CDS: Cross-Domain Spread)**  

✅ **저장 파일:** `topic_spread.png`  

---

### **2️⃣ 주요 도메인의 토픽 분포 (Topic Distribution Across Top 20 Domains)**  
📌 **가장 많이 언급된 20개 도메인에서 각 토픽의 점유율 분석**  
📌 **어떤 도메인이 특정 주제를 집중적으로 다루는지 확인 가능**  

✅ **저장 파일:** `topic_distribution.png`  

---

### **3️⃣ 영향력 있는 도메인 분석 (Top 20 Influential Domains)**  
📌 **기사 간 유사도를 기반으로 네트워크 그래프 생성**  
📌 **가장 많은 기사 간 연결을 갖는 영향력 높은 도메인 식별**  

✅ **저장 파일:** `Top_20_Influential_Domains.png`  

---

## **📢 기여 및 문의**  
이 프로젝트에 기여하고 싶거나 문의사항이 있다면 **깃허브 이슈**를 통해 의견을 남겨주세요! 🚀  
