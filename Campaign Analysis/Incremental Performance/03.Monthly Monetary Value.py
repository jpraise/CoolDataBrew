import pandas as pd

# 데이터 로드
data = pd.read_excel(r"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\incremental_dataset_v0.6.xlsx")
hera = data[data['brand'] == '헤라'].reset_index(drop=True)
sws = data[data['brand'] == '설화수'].reset_index(drop=True)

# 브랜드와 컬럼 리스트
brands = ['hera', 'sws']
columns = ['naver_brand_search_volume', 'naver_brand_product_search_volume',
           'cafe_cnt', 'comm_cnt', 'blog_cnt', 'cafe_pos', 'comm_pos', 'blog_pos', 'newVisitors', 'returningVisitors', # 2024-08-23 긍정 추가
            'Rank_1_설화수자음2종', 'Rank_1_헤라블랙쿠션', 'Rank_2_설화수탄력크림', 'Rank_2_헤라쿠션',
            'Rank_3_설화수세트', 'Rank_3_헤라썬크림', 'Rank_4_설화수퍼펙팅쿠션', 'Rank_4_헤라파운데이션',
            'Rank_5_설화수윤조에센스', 'Rank_5_헤라란제리'] # 2024-09-04 제품별 검색량, 블로그 추가  

# 기준금액 딕셔너리
price_dict = {
    'naver_brand_search_volume': 46,
    'naver_brand_product_search_volume': 184,
    'Rank_1_설화수자음2종': 184, 
    'Rank_1_헤라블랙쿠션': 184, 
    'Rank_2_설화수탄력크림': 184, 
    'Rank_2_헤라쿠션': 184,
    'Rank_3_설화수세트': 184, 
    'Rank_3_헤라썬크림': 184, 
    'Rank_4_설화수퍼펙팅쿠션': 184, 
    'Rank_4_헤라파운데이션': 184,
    'Rank_5_설화수윤조에센스': 184, 
    'Rank_5_헤라란제리': 184,
    'cafe_cnt': 4450,
    'comm_cnt': 4450,
    'blog_cnt': 4450,
    'cafe_pos': 8900,
    'comm_pos': 8900,
    'blog_pos': 8900,
    'newVisitors': 640,
    'returningVisitors': 1280
}

# 90일 이동평균
window_size = 90

# 표준편차 1배수
n_std_dev = 1

# 결과를 저장할 리스트
results = []

# 루프를 통해 각 브랜드, 컬럼에 대해 작업 수행
for df_name in brands:
    for column_name in columns:
        # 데이터프레임 로드
        df = eval(df_name)[['std_date', column_name]].copy()
        df['std_date'] = pd.to_datetime(df['std_date'])

        # 전체 기간의 평균 및 표준편차 계산
        overall_mean = df[column_name].mean()
        overall_std = df[column_name].std()

        # 이동 평균 계산을 위한 대체된 값 생성 (초과할 경우에만 대체)
        threshold = overall_mean + 3 * overall_std
        df['adjusted_for_moving_avg'] = df[column_name].apply(lambda x: x if x <= threshold else threshold)

        # 이동 평균 및 이동 표준 편차 계산
        df['moving_avg'] = df['adjusted_for_moving_avg'].rolling(window=window_size, min_periods=window_size).mean()
        df['moving_std'] = df['adjusted_for_moving_avg'].rolling(window=window_size, min_periods=window_size).std()

        # 동적으로 적정 범위 계산
        df['lower_bound'] = df['moving_avg'] - n_std_dev * df['moving_std']
        df['upper_bound'] = df['moving_avg'] + n_std_dev * df['moving_std']
        
        # 초과량 및 미달량 계산
        df['above_amount'] = df[column_name] - df['upper_bound']
        df['below_amount'] = df['lower_bound'] - df[column_name]

        # 초과량 및 미달량에서 음수값을 0으로 처리
        df['above_amount'] = df['above_amount'].apply(lambda x: x if x > 0 else 0)
        df['below_amount'] = df['below_amount'].apply(lambda x: x if x > 0 else 0)
        
        # 월별 초과량 및 미달량 합산
        df['year_month'] = df['std_date'].dt.to_period('M')  # 연월 컬럼 생성
        monthly_summary = df.groupby('year_month').agg(
            Monthly_Above_Amount=('above_amount', 'sum'),
            Monthly_Below_Amount=('below_amount', 'sum')
        ).reset_index()

        # 기준금액 가져오기
        unit_price = price_dict[column_name]

        # 월별 monetary value 계산
        monthly_summary['Monetary_Value'] = (monthly_summary['Monthly_Above_Amount'] - monthly_summary['Monthly_Below_Amount']) * unit_price

        # 월별 데이터를 결과 리스트에 추가
        for _, row in monthly_summary.iterrows():
            results.append({
                'Brand': df_name,
                'Column': column_name,
                'Year-Month': row['year_month'],
                'Monthly Above Amount': row['Monthly_Above_Amount'],
                'Monthly Below Amount': row['Monthly_Below_Amount'],
                'Monthly Incremental Performance': row['Monthly_Above_Amount'] - row['Monthly_Below_Amount'],
                'Monetary Value': row['Monetary_Value']
            })

# 결과를 DataFrame으로 변환
result_df = pd.DataFrame(results)

# 기간 설정 (결과를 2023-10 부터로 절삭해서 보기)
result_df = result_df[(result_df['Year-Month'] >= '2023-10') & (result_df['Year-Month'] <= '2024-06')].reset_index(drop=True)

# 결과를 엑셀로 저장
result_df.to_excel(rf"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\monthly_range_analysis_results_{window_size}day_moving_avg_{n_std_dev}std_dev.xlsx", index=False)

# 결과 출력
result_df


