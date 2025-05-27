### 일자별 날짜 데이터 생성 (2023.07.01 ~ 2024.06.30)

import pandas as pd
start_date = '2023-07-01'
end_date = '2024-06-30'
date_range = pd.date_range(start=start_date, end=end_date, freq='D')
formatted_dates = date_range.strftime('%Y-%m-%d')
date_df = pd.DataFrame({'기준일자': formatted_dates})
date_df

### 캠페인 데이터

hera = pd.read_excel(r"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\BY24_헤라_디지털광고성과_수정.xlsx")
sws = pd.read_excel(r"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\BY24_설화수_디지털광고성과_수정.xlsx")

hera['브랜드'] = '헤라'
sws['브랜드'] = '설화수'
all = pd.concat([hera, sws], ignore_index=True)

"""
캠페인유형 & 광고매체 filtering
포함기준

	- IMC & 유튜브/인스타
	- Performance, etc & 유튜브/인스타
	- IMC & 제외 (hiclass, toss, 애드패커, 버즈스크린 등 타겟팅성 광고상품)
            	(매출지향적, 즉각보상성 캠페인, 단타성)
"""

# filtering
c1 = all['캠페인유형'] == 'IMC'
c2 = all['광고매체'].isin(['youtube', 'instagram'])
c3 = all['캠페인유형'].isin(['Performance','Other'])
c4 = ~all['광고매체'].isin(['buzzscreen', 'hiclass', 'targetinggates', 'adpacker', 'widerplanet', 'toss', 'okcashbag'])
result = all[(c1 & c2) | (c3 & c2) | (c1 & c4)]

# 광고비 sum
agg = result.groupby(['브랜드','기준일자','광고유형','광고매체']).agg({'광고비' : 'sum'}).reset_index()

# date + 캠페인
date_agg = pd.merge(left = date_df, right = agg, how = 'left', on = '기준일자')
date_agg = date_agg.fillna(0)
date_agg = date_agg.rename(columns = {'기준일자':'std_date', '브랜드':'brand', '광고유형':'ad_type', '광고매체':'ad_medium', '광고비':'ad_spend'})

### Buzz

file_path = "버즈데이터.xlsx"
sheet1_name = "집계"
sheet2_name = "News"
sheet3_name = "Cafe"
sheet4_name = "Community"

def read_four_sheets(file_path, sheet1_name, sheet2_name, sheet3_name, sheet4_name):
    by24_agg = pd.read_excel(file_path, sheet_name=sheet1_name)
    by24_news = pd.read_excel(file_path, sheet_name=sheet2_name)
    by24_cafe = pd.read_excel(file_path, sheet_name=sheet3_name)
    by24_comm = pd.read_excel(file_path, sheet_name=sheet4_name)
    return by24_agg, by24_news, by24_cafe, by24_comm

by24_agg, by24_news, by24_cafe, by24_comm = read_four_sheets(file_path, sheet1_name, sheet2_name, sheet3_name, sheet4_name)

def process_sentiment_data(df_raw, prefix):
    # 1. 헤더 및 본문 분리
    df_raw.columns = df_raw.iloc[0]
    df = df_raw.iloc[1:, 1:].copy()
    df['tstamp'] = pd.to_datetime(df['tstamp'])

    # 2. 전체 게시글 수 집계
    total_counts = df.groupby(['tstamp', 'brand'])['title'].count().reset_index()
    total_counts = total_counts.rename(columns={'title': f'{prefix}_cnt'})

    # 3. 감성별 게시글 수 집계
    sentiment_map = {'pos': f'{prefix}_pos', 'neg': f'{prefix}_neg', 'neu': f'{prefix}_neu'}
    sentiment_counts = []

    for sentiment, col_name in sentiment_map.items():
        count = (
            df[df['sentiment'] == sentiment]
            .groupby(['tstamp', 'brand'])
            .size()
            .reset_index(name=col_name)
        )
        sentiment_counts.append(count)

    # 4. 병합
    df_merged = df.merge(total_counts, on=['tstamp', 'brand'], how='left')
    for sentiment_df in sentiment_counts:
        df_merged = df_merged.merge(sentiment_df, on=['tstamp', 'brand'], how='left')

    # 5. 결과 정리
    result = df_merged[
        ['tstamp', 'brand', f'{prefix}_cnt', f'{prefix}_pos', f'{prefix}_neg', f'{prefix}_neu']
    ].fillna(0).drop_duplicates().reset_index(drop=True)

    result[f'{prefix}_neg'] = result[f'{prefix}_neg'].astype(int)

    return result

by24_news_final = process_sentiment_data(by24_news, prefix='news')
by24_cafe_final = process_sentiment_data(by24_cafe, prefix='cafe')
by24_comm_final = process_sentiment_data(by24_comm, prefix='comm')

## merge : news + cafe + community

news_cafe = pd.merge(left = by24_news_final, right = by24_cafe_final, how = 'outer', on = ['tstamp','brand'])
news_cafe_comm = pd.merge(left = news_cafe, right = by24_comm_final, how = 'outer', on = ['tstamp','brand'])

## 기간 설정
news_cafe_comm = news_cafe_comm[(news_cafe_comm['tstamp'] >= '2023-07-01') & (news_cafe_comm['tstamp'] <= '2024-06-30')].reset_index(drop=True)
news_cafe_comm = news_cafe_comm[['tstamp','brand','news_cnt','news_pos','news_neg','news_neu','cafe_cnt','cafe_pos','cafe_neg','cafe_neu',
                'comm_cnt','comm_pos','comm_neg','comm_neu']]
news_cafe_comm = news_cafe_comm.rename(columns = {'tstamp':'std_date'})
buzz = news_cafe_comm[news_cafe_comm['brand'].isin(['헤라', '설화수'])].reset_index(drop=True)

### 브랜드 사이트 유입

ga = pd.read_csv("GA_2307_2406_설화수_헤라_일간.csv")
ga = ga.fillna(0).rename(columns = {'date':'std_date'}) 
ga['std_date'] = pd.to_datetime(ga['std_date'].astype(str), format='%Y%m%d')

### 블로그

path = "S-Core_버즈데이터_요청_브랜드코드추가_데이터추가_블로그 추가(일일포함)_F.xlsx"
sheet1 = 'Blog'
blog_buzz = pd.read_excel(path, sheet_name=sheet1)

blog_buzz.columns = blog_buzz.iloc[0]
blog_buzz = blog_buzz.drop(blog_buzz.index[0]).reset_index(drop=True)
blog_buzz = blog_buzz.drop(columns=[col for col in blog_buzz.columns if 'Unnamed' in col])
blog_buzz = blog_buzz[blog_buzz['Date'] != 'Total Count']
blog_buzz['Date'] = pd.to_datetime(blog_buzz['Date'])

sulwhasoo = blog_buzz.iloc[:, [0, 1, 2, 3, 4]].copy()
sulwhasoo.columns = ['Date', 'total', 'pos', 'neu', 'neg']
sulwhasoo['brand'] = '설화수'

hera = blog_buzz.iloc[:, [0, 5, 6, 7, 8]].copy()
hera.columns = ['Date', 'total', 'pos', 'neu', 'neg']
hera['brand'] = '헤라'

blog_buzz2 = pd.concat([sulwhasoo, hera]).reset_index()
blog_buzz2 = blog_buzz2[['Date', 'brand', 'total', 'pos', 'neu', 'neg']]

for col in ['total', 'pos', 'neu', 'neg']:
    blog_buzz2[col] = pd.to_numeric(blog_buzz2[col], errors='coerce')

blog_buzz2 = blog_buzz2.fillna(0)
blog_buzz2 = blog_buzz2.rename(columns = {'Date':'std_date', 'total':'blog_cnt', 'pos':'blog_pos', 'neu':'blog_neu', 'neg':'blog_neg'})

### 네이버 검색량 (브랜드명, 각 브랜드+제품명)

path = "2024-08-29 검색어 데이터_v0.4.xlsx"
sheet = '검색량 데이터'

search = pd.read_excel(path, sheet_name=sheet)
search = search[search['brand_name'].isin(['헤라','설화수'])]
search = search[search['top5_yn'] == 1].reset_index(drop=True)
search['rank_keyword'] = search['keyword_rank'] + '_' + search['keywords']
search = search.rename(columns = {'brand_name':'brand', 'date':'std_date'})
search = search[['brand','rank_keyword','std_date','final_value']]

search_pv = pd.pivot_table(search, 
                            values='final_value', 
                            index=['brand', 'std_date'], 
                            columns='rank_keyword', 
                            aggfunc='first')  # 중복값이 없다고 가정하고 'first' 사용

search_pv = search_pv.reset_index()
search_pv.columns.name = None
search_pv = search_pv.fillna(0)

### 병합 : 366일 + 버즈 + 브랜드 사이트 유입 + 블로그 + 검색량

date_df_new = date_df.rename(columns={'기준일자': 'std_date'})
date_df_new['std_date'] = pd.to_datetime(date_df_new['std_date'])

buzz['std_date'] = pd.to_datetime(buzz['std_date'])
ga['std_date'] = pd.to_datetime(ga['std_date'])
search_pv['std_date'] = pd.to_datetime(search_pv['std_date'])
blog_buzz2['std_date'] = pd.to_datetime(blog_buzz2['std_date'])

date_buzz = pd.merge(left = date_df_new, right = buzz, how = 'outer', on = 'std_date')
buzz_ga = pd.merge(left = date_buzz, right = ga, how = 'outer', on = ['std_date','brand'])
buzz_ga_search = pd.merge(left = buzz_ga, right = search_pv, how = 'outer', on = ['std_date','brand'])
buzz_ga_search_blog = pd.merge(left = buzz_ga_search, right = blog_buzz2, how = 'outer', on = ['std_date','brand'])

print('date_df_new * 2',len(date_df_new)*2)
print('date_buzz',len(date_buzz))
print('buzz_ga',len(buzz_ga),'ga',len(ga))
print('buzz_ga_search',len(buzz_ga_search),'search_pv',len(search_pv))
print('buzz_ga_search_blog',len(buzz_ga_search_blog),'blog_buzz2',len(blog_buzz2))

buzz_ga_search_blog2 = buzz_ga_search_blog[buzz_ga_search_blog['brand'].notnull()]
buzz_ga_search_blog3 = buzz_ga_search_blog2.fillna(0)
buzz_ga_search_blog3['std_date'] = buzz_ga_search_blog3['std_date'].astype(str)

