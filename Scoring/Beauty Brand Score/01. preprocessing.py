import pandas as pd
import datetime as dt
import numpy as np
import re
from functools import reduce

# brand group indicator 삽입
def add_brand_indicator(df):
    df = df.copy()
    indicators = {
        '설화수': ['설화수', '랑콤', '라메르', '에스티로더'],
        '헤라': ['헤라', '맥', '나스', '입생로랑']
    }
    df['indicator'] = '기타'
    for indicator, brands in indicators.items():
        df.loc[df['brand'].isin(brands), 'indicator'] = indicator
    return df

# yyyymm 추출
def extract_yyyymm(df, date_column, new_column_name='yyyymm'):
    df = df.copy()
    
    # 먼저 가장 일반적인 형식으로 변환 시도
    df[new_column_name] = pd.to_datetime(df[date_column], format='%Y-%m-%d', errors='coerce')
    
    # 변환에 실패한 행에 대해서만 다른 형식 시도
    mask = df[new_column_name].isna()
    if mask.any():
        df.loc[mask, new_column_name] = pd.to_datetime(df.loc[mask, date_column], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce')
    
    mask = df[new_column_name].isna()
    if mask.any():
        df.loc[mask, new_column_name] = pd.to_datetime(df.loc[mask, date_column], format='%m/%d/%Y %H:%M', errors='coerce')
    
    # 여전히 변환되지 않은 값들에 대해 일반적인 파싱 시도
    mask = df[new_column_name].isna()
    if mask.any():
        df.loc[mask, new_column_name] = pd.to_datetime(df.loc[mask, date_column], errors='coerce')
    
    # YYYYMM 형식으로 변환 및 정수로 변환
    df[new_column_name] = df[new_column_name].dt.strftime('%Y%m').astype('float').astype('Int64')
    
    return df

    # 사용법
        # 기본 사용 (새 컬럼 이름은 'yyyymm'으로 생성)
        # df = extract_yyyymm(df, 'Date')
        # 새 컬럼 이름을 'YearMonth'로 지정
        # df = extract_yyyymm(df, 'DateColumn', 'YearMonth')

#1. 인스타그램

### 1-1. [타사] apify

# apify 수집 데이터
insta_data = pd.read_csv(r'위치 지정', encoding='utf-8')

# 상수 정의
REQUIRED_BRANDS = ['yslbeauty', 'lancomeofficial', 'lamer.korea', 'lamer', 'esteelauderkr', 
                   'maccosmeticskorea', 'maccosmetics', 'narscosmeticskorea', 'narsissist']
BRAND_MAPPING = {'lamer.korea': '라메르', 'maccosmeticskorea':'맥', 'narscosmeticskorea':'나스',
                 'lancomeofficial':'랑콤', 'yslbeauty':'입생로랑', 'esteelauderkr':'에스티로더'}

def process_insta_data(insta_data):
    # yyyymm 추출 및 필요한 데이터만 선택
    insta_data = extract_yyyymm(insta_data, 'timestamp', new_column_name='yyyymm')
    insta_data = insta_data[(insta_data['yyyymm'] >= 202307) & (insta_data['yyyymm'] <= 202406) & 
                            (insta_data['ownerUsername'].isin(REQUIRED_BRANDS))]

    # 필요한 컬럼만 선택하고 NaN 값을 0으로 채우기
    insta_data = insta_data[['ownerUsername', 'yyyymm', 'likesCount', 'commentsCount', 'videoViewCount']].fillna(0)
    
    # 컬럼명 변경
    insta_data.columns = ['brand', 'yyyymm', 'insta_contents_like_cnt', 'insta_contents_comment_cnt', 'insta_reels_view_cnt']
    
    # 브랜드별 월별 그룹핑
    return insta_data.groupby(['brand', 'yyyymm']).sum().reset_index()

def mac_kr_prop(kr_df, world_df):
    metrics = ['insta_contents_like_cnt', 'insta_contents_comment_cnt', 'insta_reels_view_cnt']
    kr_mean = kr_df[metrics].mean()
    world_mean = world_df[metrics].mean()
    return np.mean(kr_mean / world_mean)

# 메인 처리
insta_data = process_insta_data(insta_data)

# 맥 코리아 및 글로벌 비교
mac_kr = insta_data[insta_data.brand == 'maccosmeticskorea']
mac_world = insta_data[insta_data.brand == 'maccosmetics']
prop_of_mac_kr = mac_kr_prop(mac_kr, mac_world)
print(f"맥글로벌 대비 맥코리아 비중: {prop_of_mac_kr*100:.2f}%")

# 글로벌 브랜드 데이터 조정
global_brands = ['yslbeauty', 'lancomeofficial']
insta_data.loc[insta_data['brand'].isin(global_brands), insta_data.columns[2:]] = (
    insta_data.loc[insta_data['brand'].isin(global_brands), insta_data.columns[2:]] * prop_of_mac_kr
).round()

# 브랜드명 한글로 통일
insta_data['brand'] = insta_data['brand'].map(BRAND_MAPPING).fillna(insta_data['brand'])

# 최종 데이터셋
insta_data = insta_data[insta_data['brand'].isin(BRAND_MAPPING.values())].reset_index(drop=True)

### 1-2. [자사] 아모레 제공 헤라 설화수 인스타 데이터

amore_insta = pd.read_csv(r"위치 지정", encoding='utf-8')

def process_amore_insta(amore_insta):
    # yyyymm 추출, 필요한 컬럼 섭셋
    amore_insta = extract_yyyymm(amore_insta, 'post_date', new_column_name='yyyymm')
    amore_insta = amore_insta[['brand', 'yyyymm', 'insta_contents_like_cnt', 'insta_contents_comment_cnt', 'insta_reels_view_cnt']]

    # brand명 통일
    def replace_brand(brand):
        brand = str(brand).strip()  # 문자열로 변환하고 앞뒤 공백 제거
        if '헤라' in brand or 'HERA' in brand:
            return '헤라'
        elif '설화수' in brand or 'Sulwhasoo' in brand:
            return '설화수'
        print(f"Unmatched brand: {brand}")  # 매칭되지 않은 브랜드명 출력
        return brand

    amore_insta['brand'] = amore_insta['brand'].apply(replace_brand)

    # 브랜드별 월별 그룹핑 sum (NA값은 자동으로 0으로 처리됨)
    return amore_insta.groupby(['brand', 'yyyymm']).sum().reset_index()

# 함수 실행
amore_insta = process_amore_insta(amore_insta)

### 1-3. [최종] 인스타 데이터
final_insta = pd.concat([amore_insta, insta_data], axis=0).reset_index(drop=True)

# indicator
final_insta = add_brand_indicator(final_insta)

## 2. 유튜브
youtube_data = pd.read_csv(r"위치 지정", encoding = 'utf-8')

# yyyymm
youtube_data = extract_yyyymm(youtube_data, 'upload_date', new_column_name='yyyymm')

# 연월, 브랜드명으로 그룹바이 후 집계 
youtube_data = youtube_data[['yyyymm', 'channel_name', 'view_count', 'video_likes', 'comment_no']].groupby(['yyyymm', 'channel_name']).sum().reset_index()

# 브랜드명 한글로 통일
replacement_dict = {'헤라HERA': '헤라', 'Sulwhasoo': '설화수'}
youtube_data['channel_name'] = youtube_data['channel_name'].replace(replacement_dict)

# 컬럼명 변경
youtube_data.columns = ['yyyymm', 'brand', 'youtube_contents_view_cnt', 'youtube_contents_like_cnt', 'youtube_contents_comment_cnt']

# indicator
youtube_data = add_brand_indicator(youtube_data)

## 3. 네이버 검색량
naver_data = pd.read_csv(r'위치 지정', encoding='utf-8')
naver_ysl_bty = pd.read_csv(r'위치 지정', encoding='utf-8')

def process_naver_data(naver_data, naver_ysl_bty):
    # 입생로랑 뷰티 데이터 처리
    naver_ysl_bty = naver_ysl_bty[['date', 'final_value']].rename(columns={'final_value': 'bty_val'})

    # 입생로랑 데이터 처리
    naver_ysl = naver_data[naver_data.keywords == '입생로랑'].merge(naver_ysl_bty, on='date', how='left')
    naver_ysl['final_value'] = (naver_ysl.final_value * 0.06) + naver_ysl.bty_val
    naver_ysl = naver_ysl[['brand_name', 'keyword_rank', 'date', 'final_value']]

    # 메인 데이터 처리
    naver_data = naver_data[naver_data.keywords != '입생로랑']
    naver_data = naver_data[['brand_name', 'keyword_rank', 'date', 'final_value']]

    # 데이터 합치기
    naver_data = pd.concat([naver_data, naver_ysl], ignore_index=True)

    # 날짜 형식 변환
    naver_data = extract_yyyymm(naver_data, 'date', new_column_name='yyyymm')
    naver_data = naver_data.drop('date', axis=1)

    # 브랜드명 검색량
    naver_bdata = naver_data[naver_data.keyword_rank == 'brand_name'].groupby(['brand_name', 'yyyymm'])['final_value'].sum().reset_index()
    naver_bdata = naver_bdata.rename(columns={'final_value': 'naver_brand_search_volume', 'brand_name': 'brand'})

    # 브랜드명 + 프로덕트 검색량
    naver_pdata = naver_data[~naver_data.keyword_rank.isin(['brand_name', np.nan])]
    naver_pdata = naver_pdata[~((naver_pdata.brand_name == '맥') & (naver_pdata.keyword_rank == 'Rank_3'))]
    naver_pdata = naver_pdata.groupby(['brand_name', 'yyyymm'])['final_value'].sum().reset_index()
    naver_pdata = naver_pdata.rename(columns={'final_value': 'naver_brand_product_search_volume', 'brand_name': 'brand'})

    # 최종 데이터 병합
    return pd.merge(naver_bdata, naver_pdata, on=['brand', 'yyyymm'], how='left')

# 함수 실행
naver_data = process_naver_data(naver_data, naver_ysl_bty)

# indicator
naver_data = add_brand_indicator(naver_data)

## 4. 뉴스/카페/커뮤니티

buzz = pd.read_csv(r"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\브랜드스코어\브랜드스코어 활용 데이터\Table for GCP\news_cafe_comm.csv")

# 기간 설정
buzz = buzz.copy()
buzz = extract_yyyymm(buzz, 'tstamp', new_column_name='yyyymm')
buzz = buzz[(buzz['yyyymm'] >= 202307) & (buzz['yyyymm'] <= 202406)]

# 브랜드그룹 indicator 추가
buzz = add_brand_indicator(buzz)

# 집계 함수
def aggregate_counts(group):
    total = len(group)
    sentiments = group['sentiment'].value_counts()
    return pd.Series({
        'cnt': total,
        'pos': sentiments.get('pos', 0),
        'neg': sentiments.get('neg', 0),
        'neu': sentiments.get('neu', 0)
    })

# 데이터 집계
prefixes = ['news', 'cafe', 'comm']
aggregated_data = []

for prefix in prefixes:
    agg = buzz[buzz['medium'] == prefix].groupby(['yyyymm', 'indicator', 'brand'], as_index=False).apply(
        aggregate_counts, include_groups=False
    ).reset_index(drop=True)
    agg.columns = ['yyyymm', 'indicator', 'brand'] + [f'{prefix}_{col}' for col in agg.columns[3:]]
    aggregated_data.append(agg)

# 결과 병합
merged_data = aggregated_data[0]
for i in range(1, len(aggregated_data)):
    merged_data = pd.merge(merged_data, aggregated_data[i], on=['yyyymm', 'indicator', 'brand'], how='outer')

# 결측치 처리 및 데이터 타입 변환
merged_data = merged_data.fillna(0)
for col in merged_data.columns:
    if col.endswith(('cnt', 'pos', 'neg', 'neu')):
        merged_data[col] = merged_data[col].astype(int)

# 열 순서 정리
columns = ['yyyymm', 'indicator', 'brand']
for prefix in prefixes:
    columns.extend([f'{prefix}_cnt', f'{prefix}_pos', f'{prefix}_neg', f'{prefix}_neu'])

merged_data = merged_data[columns]
buzz_data = merged_data

## 5. 웹 (브랜드사이트)

#### 1) Similarweb
sw = pd.read_csv(r"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\브랜드스코어\브랜드스코어 활용 데이터\Table for GCP\similarweb.csv",
                   encoding='utf-8')

# yyyymm
sw2 = extract_yyyymm(sw, 'date', new_column_name='yyyymm')

# duration 초단위로 변환
def duration_to_seconds(duration_str):
    h, m, s = map(int, duration_str.split(':'))
    total_seconds = h * 3600 + m * 60 + s
    return total_seconds

sw2['duration_seconds'] = sw2['avg_visit_duration'].apply(duration_to_seconds)

# indicator 삽입
sw2 = add_brand_indicator(sw2)

#### 2) GA
ga_monthly = pd.read_csv(r"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\브랜드스코어\BigQuery_GA\GA_2307_2406_설화수_헤라_월간.csv", encoding = 'utf-8')

# GA - similarweb 값 비교 (설화수, 헤라)

sw_filtered = sw2[sw2['brand'].isin(['설화수', '헤라'])].reset_index(drop=True)

ga_monthly['newVisitors'] = ga_monthly['newVisitors'].astype(int)
sw_filtered['new_users'] = sw_filtered['new_users'].astype(int)
ga_monthly['returningVisitors'] = ga_monthly['returningVisitors'].astype(int)
sw_filtered['returning_users'] = sw_filtered['returning_users'].astype(int)
ga_monthly['avgTimeOnSitePerUser'] = ga_monthly['avgTimeOnSitePerUser'].astype(int)
sw_filtered['duration_seconds'] = sw_filtered['duration_seconds'].astype(int)
ga_monthly['avgTimeOnSitePerMember'] = ga_monthly['avgTimeOnSitePerMember'].astype(int)

print("신규방문자 : GA가 SW보다",np.mean(ga_monthly['newVisitors'].reset_index(drop=True)/sw_filtered['new_users'].reset_index(drop=True)),"배 더 큼")
print("설화수 신규방문자 : GA가 SW보다",np.mean(ga_monthly[ga_monthly['brand'] == '설화수']['newVisitors'].reset_index(drop=True)/sw_filtered[sw_filtered['brand'] == '설화수']['new_users'].reset_index(drop=True)),"배 더 큼")
print("헤라 신규방문자 : GA가 SW보다",np.mean(ga_monthly[ga_monthly['brand'] == '헤라']['newVisitors'].reset_index(drop=True)/sw_filtered[sw_filtered['brand'] == '헤라']['new_users'].reset_index(drop=True)),"만큼 더 큼")

print("재방문자 : GA가 SW보다",np.mean(ga_monthly['returningVisitors'].reset_index(drop=True)-sw_filtered['returning_users'].reset_index(drop=True)),"배 더 큼")
print("설화수 재방문자 : GA가 SW보다",np.mean(ga_monthly[ga_monthly['brand'] == '설화수']['returningVisitors'].reset_index(drop=True)-sw_filtered[sw_filtered['brand'] == '설화수']['returning_users'].reset_index(drop=True)),"배 더 큼")
print("헤라 재방문자 : GA가 SW보다",np.mean(ga_monthly[ga_monthly['brand'] == '헤라']['returningVisitors'].reset_index(drop=True)-sw_filtered[sw_filtered['brand'] == '헤라']['returning_users'].reset_index(drop=True)),"만큼 더 큼")

print("신규방문자 : GA가 SW보다",np.mean(ga_monthly['newVisitors']/sw_filtered['new_users']),"배 더 큼")
print("신규방문자 : GA가 SW보다",np.mean(ga_monthly['newVisitors']-sw_filtered['new_users']),"만큼 더 큼")

print("재방문자 : GA가 SW보다",np.mean(ga_monthly['returningVisitors']/sw_filtered['returning_users']),"배 더 큼")
print("재방문자 : GA가 SW보다",np.mean(ga_monthly['returningVisitors']-sw_filtered['returning_users']),"만큼 더 큼")

print("체류시간 : GA가 SW보다",np.mean(ga_monthly['avgTimeOnSitePerUser']/sw_filtered['duration_seconds']),"배 더 큼")
print("체류시간 : GA가 SW보다",np.mean(ga_monthly['avgTimeOnSitePerUser']-sw_filtered['duration_seconds']),"만큼 더 큼")

# GA(회원) - GA(전체) 값 비교
print("GA(회원) 체류시간이 GA(전체) 체류시간보다",np.mean(ga_monthly['avgTimeOnSitePerMember']/ga_monthly['avgTimeOnSitePerUser']),"배 더 큼")
print("GA(회원) 체류시간이 GA(전체) 체류시간보다",np.mean(ga_monthly['avgTimeOnSitePerMember']-ga_monthly['avgTimeOnSitePerUser']),"만큼 더 큼")

# similarweb - GA에 맞춰서 값 조정
# 설화수 & 헤라는 GA값 그대로 쓰고, 그 외에는 환산한 값 적용  -- 240809 변경된 사항

def calculate_user_percentages(df):
    total_users = df['new_users_f'] + df['returning_users_f']
    df['new_users_prop_f'] = df['new_users_f'] / total_users
    df['returning_users_prop_f'] = df['returning_users_f'] / total_users
    return df

def prepare_ga_data(ga_monthly):
    ga_cols = ['brand', 'yyyymm', 'newVisitors', 'returningVisitors', 'avgTimeOnSitePerUser', 'avgTimeOnSitePerMember']
    new_cols = ['brand', 'yyyymm', 'new_users_f', 'returning_users_f', 'duration_seconds_f', 'mem_duration_f']
    
    ga_data = ga_monthly[ga_cols].copy()
    ga_data.columns = new_cols
    ga_data['indicator'] = ga_data['brand']
    
    ga_data = calculate_user_percentages(ga_data)
    
    return ga_data[['yyyymm', 'indicator', 'brand', 'new_users_f', 'returning_users_f', 
                    'duration_seconds_f', 'mem_duration_f', 'new_users_prop_f', 'returning_users_prop_f']]

def prepare_sw_data(sw2, ga_monthly, sw_filtered):
    sw_data = sw2[~sw2['brand'].isin(['헤라', '설화수'])].reset_index(drop=True)
    
    # Calculate adjustment factors
    new_users_factor = np.mean(ga_monthly['newVisitors'] / sw_filtered['new_users'])
    returning_users_diff = np.mean(ga_monthly['returningVisitors'] - sw_filtered['returning_users'])
    duration_factor = np.mean(ga_monthly['avgTimeOnSitePerUser'] / sw_filtered['duration_seconds'])
    mem_duration_factor = np.mean(ga_monthly['avgTimeOnSitePerMember'] / ga_monthly['avgTimeOnSitePerUser'])
    
    # Apply adjustments
    sw_data['new_users_f'] = sw_data['new_users'] * new_users_factor
    sw_data['returning_users_f'] = sw_data['returning_users'] + returning_users_diff
    sw_data['duration_seconds_f'] = sw_data['duration_seconds'] * duration_factor
    sw_data['mem_duration_f'] = sw_data['duration_seconds_f'] * mem_duration_factor
    
    sw_data = calculate_user_percentages(sw_data)
    
    return sw_data[['yyyymm', 'indicator', 'brand', 'new_users_f', 'returning_users_f', 
                    'duration_seconds_f', 'mem_duration_f', 'new_users_prop_f', 'returning_users_prop_f']]

# Main execution
ga_data = prepare_ga_data(ga_monthly)
sw_data = prepare_sw_data(sw2, ga_monthly, sw_filtered)

web_final = pd.concat([ga_data, sw_data], axis=0, ignore_index=True)

## 6. 리뷰
### 네이버 쇼핑 리뷰로 한정

df1 = pd.read_csv(r"위치 지정",
           encoding='utf-8')

df2 = pd.read_csv(r"위치 지정",
           encoding='utf-8')

def contains_loyalty_keyword(review, keyword_list):
    return any(re.search(keyword, review) if keyword.startswith(r'\d+') else keyword in review for keyword in keyword_list)

def process_data(df1, df2):
    dfs = [df1, df2]
    for i, df in enumerate(dfs):
        dfs[i] = extract_yyyymm(df, 'date', new_column_name='yyyymm')
        dfs[i]['brand'] = dfs[i]['brand'].replace('MAC', '맥')

    df1, df2 = dfs
        
    review_cnt_rate = df1.groupby(['yyyymm', 'brand'])['rating'].mean().reset_index()
    review_cnt_rate = review_cnt_rate.rename(columns={'rating': 'average_rate'})

    df2_unique = df2[['yyyymm', 'brand', 'product', 'review_contents', 'sentiment']].drop_duplicates()
    review_counts = df2_unique.groupby(['yyyymm', 'brand']).size().reset_index(name='review_cnt')
    
    sentiment_counts = df2_unique.groupby(['yyyymm', 'brand', 'sentiment']).size().unstack(fill_value=0).reset_index()
    sentiment_counts.columns = ['yyyymm', 'brand', 'positive_cnt', 'negative_cnt', 'neutral_cnt']

    review_sent_final = pd.merge(review_counts, sentiment_counts, on=['yyyymm', 'brand'])
    review_final = pd.merge(review_cnt_rate, review_sent_final, on=['yyyymm', 'brand'])

    review_final['positive_rate'] = review_final['positive_cnt'] / review_final['review_cnt']
    review_final['negative_rate'] = review_final['negative_cnt'] / review_final['review_cnt']
    review_final['neutral_rate'] = review_final['neutral_cnt'] / review_final['review_cnt']
    review_final['review_snps'] = review_final['positive_rate'] - review_final['negative_rate']

    review_final = add_brand_indicator(review_final)

    return review_final, df2
    
def process_loyalty_keywords(df, loyalty_keyword_f):
    df = df[['yyyymm','brand', 'review_contents']].drop_duplicates()
    df['review_contents'] = df['review_contents'].fillna('').astype(str)
    df['contains_loyalty_keyword'] = df['review_contents'].apply(lambda x: contains_loyalty_keyword(x, loyalty_keyword_f))

    brand_loyalty_ratio = df.groupby(['yyyymm', 'brand']).agg({
        'contains_loyalty_keyword': ['sum', 'count']
    }).reset_index()

    brand_loyalty_ratio.columns = ['yyyymm', 'brand', 'review_loyalty_cnt', 'review_total_cnt']
    brand_loyalty_ratio['review_loyalty_ratio'] = brand_loyalty_ratio['review_loyalty_cnt'] / brand_loyalty_ratio['review_total_cnt']

    return brand_loyalty_ratio

# 메인 실행 코드
review_final, df2 = process_data(df1, df2)

loyalty_keyword_f = ['또구매할게요', '항상쓰던거', '쓰던거에요', '애용해요', '쟁였어요', '재구매의사있어요', '재구매합니다', 
                     '재구매하겠습니다', '믿고쓰는', '쓰던거라', '꾸준히', '믿고씁니다', '또구매할께요', '항상쓰던거라', '쓰는제품이에요', '사용하던거라',
                     '늘쓰던제품이라', '정착했습니다', '쟁여놓고', '추천드립니다', '항상쓰는거라', '잘쓰고있습니다', '쓰던거예요', '몇통째', 
                     '재주문했어요', '재구매의사있습니다', '재구매해서', '항상쓰던거에요', '잘사용하고있어요', '정착하려구요', '강추입니다', '구매하세요', 
                     '늘사용하는', '항상쓰던제품', '재주문합니다', '항상쓰는거에요', '최애템입니다', '항상쓰는제품입니다', '쓰던제품이예요', '구매중이에요', 
                     '애용합니다', '계속사용하는', '늘쓰던거라', '두통째', '항상쓰는제품이에요', '늘쓰는제품입니다', '잘쓰고있어요', 
                     '사용하던거에요', '쓰던제품입니다', '적극추천합니다', '재구매했어요', '쓰던제품이라', '추천드려요', '늘쓰던거에요', '재구매해요', '쟁여놨어요', 
                     '사용하는거라', '늘쓰던제품', '사용하는제품입니다', '인생템입니다', '세통째', '사용하던제품', '이것만써요', '사용중이예요', 
                     '필수템입니다', '재구매각입니다', '사용중입니다', '사용하고있습니다', '재구매할께요', '믿고써요', '구매중입니다', '재구매중입니다', 
                     '항상쓰던제품입니다', '쓰는제품입니다', '추천해요', '재구매입니다', '구매하고있어요', '잘사용중입니다', '추천합니다', '재구매예정', '정착템입니다', 
                     '잘쓰고잇어요', '늘쓰던제품입니다', '재구매에요', '강추합니다', '재구매할게요', '재구매예요', '재구매하는', '재구매각', '쟁여두고', 
                     '재구매했습니다', '몇통째인지', '항상쓰던제품이라', '재구매하려구요', '쟁여둡니다', '항상사용하는', '강추', '인생템', '쟁여두려고', '쓰는제품이라', 
                     '추천입니다', '항상쓰는제품', r'\d+통째']

brand_loyalty_ratio = process_loyalty_keywords(df2[['yyyymm', 'brand', 'review_contents']], loyalty_keyword_f)
review_final2 = pd.merge(review_final, brand_loyalty_ratio, on=['yyyymm', 'brand'], how='left')
review_final2 = review_final2.fillna(0)

## 7. 카카오 친구추가
# 카카오 친구추가 건수는 시계열이 아니라 현재기준으로 점으로 표현되므로, 개설일을 기반으로 과거를 추정하는 로직이 필요할 듯
# 첫게시물 혹은 개설일 기준으로 현재까지 등차수열로 오르도록

# 나스 3 / 190415
# 맥 24.3 / 190809
# 에스티 13.9 / 170202
# 라메르 4.5천 / 190102
# 헤라 7.3 / 201231
# 입생 55.3 / 180601
# 설 6.8 / 210308
# 랑콤 13 / 230818 
### 위 개설일은 확인가능한 첫 게시물 기준임(몇몇은 OPEN일이라고 명시하였고, 몇몇은 안되어있음) ###

kakao_data = pd.read_csv(r'위치 지정')

# 날짜 형식 데이터타입 변경 후 필요 날짜만 섭셋
kakao_data['yyyymm'] = kakao_data.yyyymm.astype(int)
kakao_data = kakao_data[(kakao_data['yyyymm'] >= 202307) & (kakao_data['yyyymm'] <= 202406)].reset_index(drop=True)

# inidicator
kakao_data = add_brand_indicator(kakao_data)

## 8. 블로그
blogs = pd.read_csv(r"위치 지정",
             encoding='utf-8')

blogs = blogs.fillna(0)
blogs = add_brand_indicator(blogs)

## 9. 전처리 완료본 결합

def merge_dfs(dfs, on, how='left'):
    # 가장 긴 DataFrame 찾기
    base_df = max(dfs, key=len)
    
    # 나머지 DataFrame들
    other_dfs = [df for df in dfs if df is not base_df]
    
    # 병합 함수
    def merge_df(left, right):
        return pd.merge(left, right, on=on, how=how)
    
    # reduce를 사용하여 모든 DataFrame 병합
    merged_df = reduce(merge_df, [base_df] + other_dfs)
    
    # 열 순서 재정렬
    first_columns = [col for col in ['yyyymm', 'indicator', 'brand'] if col in merged_df.columns]
    
    # dfs의 순서대로 나머지 컬럼 정렬
    other_columns = []
    for df in dfs:
        other_columns.extend([col for col in df.columns if col not in first_columns and col not in other_columns])
    
    reordered_columns = first_columns + other_columns
    
    return merged_df[reordered_columns]

dfs = [final_insta, youtube_data, naver_data, buzz_data, web_final, review_final2, kakao_data, blogs]  # 병합할 DataFrame들의 리스트
result = merge_dfs(dfs, on=['yyyymm','brand','indicator'])
result = result.reset_index(drop=True).fillna(0)
result.to_csv(r"위치 지정",
              encoding = 'utf-8', index=False)
