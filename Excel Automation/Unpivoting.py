import pandas as pd
import numpy as np
import re

### 0. Load Result
file_path = r'C:\Users\User\Documents\업무\2025\삼성전자 MX SEO\250516_Galaxy_S25 Edge_(PD)_SEO Status with Fine tune Guide.xlsx'
sheet_name = 'Result'

df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=6)


### 1. result1 (No. ~ Target URL) 전처리

result1_raw = df.iloc[2:,1:8]
result1_raw.columns = result1_raw.iloc[0]
result1 = result1_raw[1:].reset_index(drop=True)

### 2. result2 (Crawling Value ~) 전처리

result2 = df.iloc[:, 13:].copy()

# (1) 상단 2행: 병합된 헤더 전처리
header_raw = result2.iloc[0:2].ffill(axis=1)

# 괄호 제거 함수
def remove_parentheses(text):
    return re.sub(r"\s*\(.*?\)", "", str(text)).strip()

# 헤더 구성
header_upper = header_raw.iloc[0].map(remove_parentheses)
header_lower = header_raw.iloc[1].astype(str).str.strip()

# (2) 병합된 컬럼 이름 생성
combined_headers = [
    f"{u} - {l}" if u and l else u or l or f"Unnamed_{i}"
    for i, (u, l) in enumerate(zip(header_upper, header_lower))
]

# (3) 실제 데이터 (3행 이후) 추출
result2_data = result2.iloc[3:].reset_index(drop=True)
result2_data.columns = combined_headers

### 3. result1 + result2

one_two = pd.concat([result1, result2_data], axis=1)
one_two = one_two.drop(columns=['Twitter_Card - O', 'Twitter_Card - Total'])


### 4. 재구성 시작

df = one_two

# 고정 메타 컬럼 자동 추출
meta_cols = ['No.', 'Region', 'Country', 'Site_Code', 'Products', 'Page Type', 'Target URL']

# 점검 항목 컬럼 추출: " - " 포함 + "Crawling Value" 제외
audit_cols = [
    col for col in df.columns
    if ' - ' in str(col)
    and not str(col).endswith('Crawling Value')
]

# 각 행에서 'SEO 항목 + 점검 항목' 조합마다 새로운 행 만들기
records = []

for _, row in df.iterrows():
    meta_info = {col: row[col] for col in meta_cols}

    for audit_col in audit_cols:
        # 항목 분리
        try:
            seo_element, audit_standard = audit_col.split(' - ', 1)
        except ValueError:
            continue  # 형식 안 맞으면 skip

        seo_element = seo_element.strip()
        audit_standard = audit_standard.strip()
        asis_col = f"{seo_element} - Crawling Value"

        records.append({
            **meta_info,
            "SEO Audit Element": seo_element,
            "Audit Standard": audit_standard,
            "AS-IS": row.get(asis_col, ""),
            "Result": row.get(audit_col, "")
        })

# 최종 DataFrame 구성
df_long = pd.DataFrame(records)
df_long["No."] = range(1, len(df_long) + 1)
df_long = df_long[df_long['Region'].notna()]
df_long.rename(columns={'AS-IS': 'AS-IS (Issue)'}, inplace=True)


# Action Necessity 매핑 테이블 
action_map = {
    "Title": "Must",
    "Description": "Must",
    "H1": "Must",
    "Canonical": "Must",
    "Google Indexation": "Must",

    "OG_Title": "Recommended",
    "OG_Description": "Recommended",
    "OG_Image": "Recommended",
    "Twitter_Title": "Recommended",
    "Twitter_Description": "Recommended",
    "Twitter_Site": "Recommended",
    "Twitter_Creator": "Recommended",
    "Twitter_Image": "Recommended",
    "Twitter_Card": "Recommended"
}

df_long['Action Necessity'] = df_long['SEO Audit Element'].map(action_map).fillna("")

### 5. 완료 파일 저장
# 저장 위치 지정
output_path = r'C:\Users\User\Documents\업무\2025\삼성전자 MX SEO\Fine Tune Guide\Fine Tune Guide - Unpivoting Result - PD.xlsx'
df_long.to_excel(output_path, index=False)
