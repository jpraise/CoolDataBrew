### **📌 README.md (한글)**  

# **👜 GPT-4o-mini를 활용한 브랜드별 소셜 미디어 콘텐츠 분석**  

## **📌 프로젝트 개요**  
이 프로젝트는 **소셜 미디어 콘텐츠**를 분석하여 특정 **럭셔리 브랜드**에 대한 언급을 분류하고,  
OpenAI의 **GPT-4o-mini**를 활용해 상세한 **주제별 분석**을 수행하는 자동화된 시스템입니다.  

브랜드별로 **특정 키워드**를 추출하고, 내용을 요약하여 **데이터 분석 및 인사이트 도출**을 지원합니다.  

---

## **🚀 주요 기능**  
✅ **엑셀 파일 데이터 로드 및 브랜드별 필터링**  
✅ **OpenAI API를 활용한 소셜 미디어 콘텐츠 분석**  
✅ **브랜드별 주요 주제 (로고, 소재, 색상, 착용 방식 등) 분류**  
✅ **멀티쓰레딩을 활용한 빠른 데이터 처리**  
✅ **분석된 데이터를 엑셀 파일로 저장**  

---

## **🎯 활용 사례**  
🔹 **패션 및 럭셔리 브랜드의 온라인 인지도 분석**  
🔹 **소셜 미디어에서 브랜드 관련 트렌드 파악**  
🔹 **제품별, 카테고리별, 컬러별 소비자 선호도 분석**  
🔹 **마케팅 및 홍보 전략 수립을 위한 데이터 기반 인사이트 도출**  

---

## **⚙️ 설치 및 실행 방법**  

### **1️⃣ 필수 라이브러리 설치**  
아래 명령어를 실행하여 프로젝트에 필요한 라이브러리를 설치하세요.

```bash
pip install openai pandas numpy
```

### **2️⃣ OpenAI API 키 설정**  
🔑 OpenAI API 키를 `my_openai_api_key` 변수에 입력하세요.

```python
my_openai_api_key = "your_api_key"
```

### **3️⃣ 데이터 파일 준비**  
📂 분석할 **엑셀 파일**을 준비하고, `file_path` 변수를 해당 파일 경로로 변경하세요.

```python
file_path = r"file_path_here"
```

### **4️⃣ 코드 실행**  
다음 명령어를 실행하여 분석을 시작하세요.

```bash
python script.py
```

✅ **코드가 실행되면 브랜드별 데이터를 분석하고, 최종 결과를 엑셀 파일(`final_results.xlsx`)로 저장합니다.**

---

## **📊 출력 결과 (Excel 파일 구조)**  

### **📄 생성되는 파일**  
✅ **브랜드별 분석 결과가 포함된 엑셀 파일 (`final_results.xlsx`)**  
✅ **각 브랜드별 언급된 주요 주제 및 키워드 정리**  
✅ **분석된 데이터와 원본 데이터 결합 제공**  

### **📌 엑셀 파일 구조 예시**  

| Query Id | Query Name | Date       | Title         | Full Text                                       | Brand_1       | Brand_2 | Color | Material | Format  | Keywords          | Topics                   |
|----------|-----------|------------|--------------|------------------------------------------------|--------------|---------|-------|----------|---------|------------------|--------------------------|
| 1001     | Handbag Review | 2024-03-15 | New Bag      | "I love this black leather tote bag!"         | LOEWE        | NaN     | Black | Leather  | Tote    | Black, Leather   | Logo, Material, Format   |
| 1002     | Fashion Trend  | 2024-03-17 | Designer Picks | "Miu Miu's bucket bag is trending!"         | Miu Miu      | NaN     | Beige | Canvas   | Bucket  | Beige, Canvas    | Format, Coordinated Outfit |
| 1003     | Luxury Haul    | 2024-03-20 | My New Celine | "This Celine mini bag is so versatile!"      | Celine       | NaN     | White | Leather  | Crossbody | White, Leather  | Size, Format, Color       |
| 1004     | Seasonal Collection | 2024-03-22 | Spring Picks | "Bottega Veneta's rattan bags are amazing!" | Bottega Veneta | NaN   | Brown | Rattan   | Basket  | Brown, Rattan    | Material, Format         |

📌 **컬럼 설명**  
- `Query Id`: 데이터의 고유 ID  
- `Query Name`: 게시글의 카테고리  
- `Date`: 게시글 날짜  
- `Title`: 게시글 제목  
- `Full Text`: 게시글 전체 내용  
- `Brand_1`: 주요 브랜드  
- `Brand_2`: 서브 브랜드 (해당 없음 시 `NaN`)  
- `Color`: 언급된 가방 색상  
- `Material`: 언급된 소재 (가죽, 캔버스 등)  
- `Format`: 가방 착용 방식 (토트백, 크로스바디 등)  
- `Keywords`: 주요 키워드 (색상, 소재 등)  
- `Topics`: 해당 게시글에서 언급된 주요 주제  

---

## **📢 기여 및 문의**  
이 프로젝트에 기여하고 싶거나 문의사항이 있다면 **깃허브 이슈**를 통해 의견을 남겨주세요! 🚀  
