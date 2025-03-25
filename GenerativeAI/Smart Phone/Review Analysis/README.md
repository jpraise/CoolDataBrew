# **📌 Galaxy S25 리뷰 분석 자동화 프로젝트**  

## **📌 프로젝트 개요**  
이 프로젝트는 **Galaxy S25** 제품에 대한 **소셜 미디어 및 리뷰 데이터**를 분석하여  
소비자 피드백을 요약하고, 경쟁 브랜드와의 비교 내용을 도출하는 자동화 시스템입니다.  

OpenAI의 **GPT-4o**를 활용하여 리뷰 데이터를 분석하고, **소비자 만족도, 개선점, 주요 발견 사항**을 추출합니다.  
또한, 리뷰에서 **Xiaomi, Huawei, Oppo, Google, Apple 및 기타 중국 브랜드와의 비교 여부**를 확인하고,  
비교된 특성을 함께 기록합니다.  

## **🚀 주요 기능**  
✅ **Excel 파일에서 리뷰 데이터 읽기 및 필터링**  
✅ **OpenAI GPT-4o를 활용한 리뷰 요약 및 분석**  
✅ **소비자 만족도, 개선점, 주요 인사이트 추출**  
✅ **경쟁 브랜드(Xiaomi, Huawei, Oppo, Google, Apple 등)와 비교 여부 확인**  
✅ **멀티쓰레딩을 활용한 병렬 처리로 빠른 데이터 분석**  
✅ **분석 결과를 Excel 파일로 저장**  

---

## **🎯 활용 사례**  
🔹 **Galaxy S25에 대한 소비자 리뷰 분석**  
🔹 **경쟁 브랜드와의 비교를 통한 시장 분석**  
🔹 **제품 개선을 위한 주요 피드백 도출**  
🔹 **마케팅 및 제품 전략 수립을 위한 인사이트 제공**  

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

✅ **코드가 실행되면 리뷰 데이터를 분석하고, 최종 결과를 엑셀 파일(`final_results.xlsx`)로 저장합니다.**

---

## **📊 출력 결과 (Excel 파일 구조)**  

### **📄 생성되는 파일**  
✅ **Galaxy S25 리뷰 분석 결과가 포함된 엑셀 파일 (`final_results.xlsx`)**  
✅ **각 리뷰별 소비자 만족도, 개선점 및 주요 인사이트 정리**  
✅ **각 리뷰에서 경쟁 브랜드 비교 여부 및 비교된 특성 포함**  

### **📌 엑셀 파일 구조 예시**  

| Customer Satisfaction | Areas for Improvement | Key Findings | Xiaomi Mentioned | Xiaomi Features | Huawei Mentioned | Huawei Features | Oppo Mentioned | Oppo Features | Chinese Brand Mentioned | Chinese Brand Features | Google Mentioned | Google Features | Apple Mentioned | Apple Features |
|----------------------|----------------------|-------------|----------------|----------------|----------------|----------------|----------------|----------------|----------------------|----------------------|----------------|----------------|----------------|----------------|
| Customers loved the AI-based personalization and camera. | Battery life needs improvement. | The chipset performance was unexpectedly high. | True | Price, Performance | False | NA | True | Fast charging | True | Build quality, Affordability | False | NA | True | Design, Ecosystem |
| Users appreciated the high refresh rate display. | Camera software needs optimization. | The phone's build quality was praised. | False | NA | True | AI capabilities | False | NA | True | Price, Performance | False | NA | True | User experience |

📌 **컬럼 설명**  
- `Customer Satisfaction`: 소비자가 긍정적으로 평가한 요소  
- `Areas for Improvement`: 소비자가 지적한 개선 사항  
- `Key Findings`: 리뷰에서 발견된 핵심 인사이트  
- `Xiaomi Mentioned`: 리뷰에서 Xiaomi와 비교했는지 여부 (`True/False`)  
- `Xiaomi Features`: Xiaomi와 비교한 특징 (예: 가격, 성능 등)  
- `Huawei Mentioned`: 리뷰에서 Huawei와 비교했는지 여부 (`True/False`)  
- `Huawei Features`: Huawei와 비교한 특징 (예: AI 성능, 보안 등)  
- `Oppo Mentioned`: 리뷰에서 Oppo와 비교했는지 여부 (`True/False`)  
- `Oppo Features`: Oppo와 비교한 특징 (예: 배터리 수명, 디자인 등)  
- `Chinese Brand Mentioned`: 기타 중국 브랜드와 비교했는지 여부 (`True/False`)  
- `Chinese Brand Features`: 기타 중국 브랜드와 비교한 특징 (예: 가격, 품질 등)  
- `Google Mentioned`: 리뷰에서 Google과 비교했는지 여부 (`True/False`)  
- `Google Features`: Google과 비교한 특징 (예: 소프트웨어 경험, AI 등)  
- `Apple Mentioned`: 리뷰에서 Apple과 비교했는지 여부 (`True/False`)  
- `Apple Features`: Apple과 비교한 특징 (예: 디자인, 생태계 등)  

---

## **📢 기여 및 문의**  
이 프로젝트에 기여하고 싶거나 문의사항이 있다면 **깃허브 이슈**를 통해 의견을 남겨주세요! 🚀  
