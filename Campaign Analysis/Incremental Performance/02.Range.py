# 전처리 완료본 불러오기
import pandas as pd
data = pd.read_excel("incremental_dataset_v0.6.xlsx")

hera = data[data['brand'] == '헤라'].reset_index(drop=True)
sws = data[data['brand'] == '설화수'].reset_index(drop=True)

# 광고비 데이터
spend = pd.read_excel("Incremental_Spend.xlsx")

# 광고비 집계
spend2 = spend[(spend['ad_medium'] == 'instagram') | (spend['ad_medium'] == 'youtube')].reset_index(drop=True)
spend3 = spend2.groupby(['std_date','brand']).agg({'ad_spend':'sum'}).reset_index()

# merge : 3차반응 + 광고비
hera = pd.merge(left = hera, right = spend3, how = 'left', on = ['std_date','brand'])
sws = pd.merge(left = sws, right = spend3, how = 'left', on = ['std_date','brand'])

# [Loop] 동적 이상치 제거 X, min_periods = window_size, 표준편차 1배수 확정 (2024-08-20), 특별 이상치 대체

import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import matplotlib.font_manager as fm

# 맞춤 포맷터 함수 정의
def format_number(x, pos):
    if x >= 1e6:
        return f'{x/1e6:.1f}M'
    elif x >= 1e3:
        return f'{x/1e3:.1f}K'
    else:
        return f'{x:.0f}'

# 한글 폰트 설정
font_path = r'C:\Users\User\AppData\Local\Microsoft\Windows\Fonts\SamsungOneKorean-400_v1.2_hinted.ttf'  
font_prop = fm.FontProperties(fname=font_path)


# 브랜드와 컬럼 리스트
brands = ['hera', 'sws']

columns = [
            # 'naver_brand_search_volume', 'naver_brand_product_search_volume',
           # 'cafe_cnt', 'comm_cnt', 'newVisitors', 'returningVisitors',
           # 'avgTimeOnSitePerUser', 'avgTimeOnSitePerMember',
           # 'cafe_pos', 'comm_pos' # 버즈 긍정량 추가로 돌리기 (2024-08-23)
           #  'Rank_1_설화수자음2종', 'Rank_1_헤라블랙쿠션', 'Rank_2_설화수탄력크림', 'Rank_2_헤라쿠션',
           # 'Rank_3_설화수세트', 'Rank_3_헤라썬크림', 'Rank_4_설화수퍼펙팅쿠션', 'Rank_4_헤라파운데이션',
           # 'Rank_5_설화수윤조에센스', 'Rank_5_헤라란제리', 'brand_name_설화수', 'brand_name_헤라',# 검색량 (브랜드, 각 제품) 추가로 돌리기 (2024-09-02)
             'blog_cnt', 'blog_pos']  

# 90일 이동평균
window_size = 90

# 표준편차 1배수
n_std_dev = 1

# 루프를 통해 각 브랜드, 컬럼에 대해 작업 수행
for df_name in brands:
    for column_name in columns:
        # 데이터프레임 로드
        df = eval(df_name)[['std_date', column_name, 'ad_spend']].copy()  # .copy()를 사용하여 명시적으로 복사
        df.loc[:, 'std_date'] = pd.to_datetime(df['std_date'])

        # 해당 컬럼의 모든 값이 0인지 확인
        if df[column_name].sum() == 0:
            print(f"브랜드: {df_name}, 컬럼: {column_name}의 모든 값이 0입니다. 이 컬럼은 건너뜁니다.")
            continue  # 다음 컬럼으로 넘어감
        
        # 전체 기간의 평균 및 표준편차 계산
        overall_mean = df[column_name].mean()
        overall_std = df[column_name].std()

        # 이동 평균 계산을 위한 대체된 값 생성 (초과할 경우에만 대체)
        threshold = overall_mean + 3 * overall_std
        df.loc[:, 'adjusted_for_moving_avg'] = df[column_name].apply(lambda x: x if x <= threshold else threshold)

        # 이동 평균 및 이동 표준 편차 계산
        df.loc[:, 'moving_avg'] = df['adjusted_for_moving_avg'].rolling(window=window_size, min_periods=window_size).mean()
        df.loc[:, 'moving_std'] = df['adjusted_for_moving_avg'].rolling(window=window_size, min_periods=window_size).std()

        # 동적으로 적정 범위 계산
        df.loc[:, 'lower_bound'] = df['moving_avg'] - n_std_dev * df['moving_std']
        df.loc[:, 'upper_bound'] = df['moving_avg'] + n_std_dev * df['moving_std']

        # 적정 범위 미달 및 초과 날짜 필터링
        below_range = df[df[column_name] < df['lower_bound']]
        above_range = df[df[column_name] > df['upper_bound']]
        within_range = df[(df[column_name] >= df['lower_bound']) & (df[column_name] <= df['upper_bound'])]

        # 적정범위 일수 계산
        total_days = len(within_range) + len(above_range) + len(below_range)
        print(f"브랜드: {df_name}, 컬럼: {column_name}, 표준편차 배수: {n_std_dev}")
        print(f"적정 범위 내 일수: {len(within_range)}일")
        print(f"적정 범위 초과 일수: {len(above_range)}일")
        print(f"적정 범위 미달 일수: {len(below_range)}일")
        print(f"총 일수: {total_days}일")

        # 결과를 엑셀로 저장
        df.to_excel(rf"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\확정본\광고비 추가\{df_name}_{column_name}_{window_size}_movig_av_{n_std_dev}_std_dev_moved.xlsx", index=False)

                
        # 시계열 그래프 생성
        fig, ax1 = plt.subplots(figsize=(14, 7))

        
        # 주 축 (왼쪽 y축) 설정
        ax1.plot(df['std_date'], df[column_name], label=f'{column_name}', color='black', alpha=0.5)
        ax1.plot(df['std_date'], df['moving_avg'], label=f'{window_size}-Day Moving Average', color='orange')
        ax1.plot(df['std_date'], df['lower_bound'], color='red', linestyle='--', label='Lower Bound')
        ax1.plot(df['std_date'], df['upper_bound'], color='green', linestyle='--', label='Upper Bound')

        ax1.set_xlabel('Date')
        ax1.set_ylabel(f'{column_name}', color='black', fontproperties=font_prop)
        ax1.tick_params(axis='y', labelcolor='black')

        # 보조 축 (오른쪽 y축) 설정
        ax2 = ax1.twinx()
        ax2.plot(df['std_date'], df['ad_spend'], label='Ad Spend', color='purple', alpha=0.5)
        ax2.set_ylabel('Ad Spend', color='purple')
        ax2.tick_params(axis='y', labelcolor='purple')

        # 맞춤 포맷터 적용
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_number))
        
        # 그래프 제목 설정
        plt.title(f'{df_name} - {column_name} Time Series with Dynamic Appropriate Range and Ad Spend', fontproperties=font_prop)

        # 범례 설정
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', prop=font_prop)

        # 적정 범위 텍스트 추가
        texts = [
            ax1.text(df['std_date'].iloc[-1], df['upper_bound'].iloc[-1], f"Upper Bound: {df['upper_bound'].iloc[-1]:.2f}", 
                     color='green', verticalalignment='bottom'),
            ax1.text(df['std_date'].iloc[-1], df['lower_bound'].iloc[-1], f"Lower Bound: {df['lower_bound'].iloc[-1]:.2f}", 
                     color='red', verticalalignment='top'),
            ax1.text(df['std_date'].iloc[-1], df['moving_avg'].iloc[-1], f"Mean: {df['moving_avg'].iloc[-1]:.2f}", 
                     color='orange', verticalalignment='bottom'),
            ax1.text(df['std_date'].max(), df[column_name].max(), 
                     f"Within Days: {len(within_range)}\n Above Days: {len(above_range)}\n Below Days: {len(below_range)}",
                     horizontalalignment='right', verticalalignment='top', color='black', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
        ]

        # 텍스트 위치 조정
        adjust_text(texts, only_move={'points': 'y', 'texts': 'y'}, arrowprops=dict(arrowstyle='->', color='gray'))

        plt.grid(True)
        
        # 그래프를 이미지로 저장
        plt.savefig(rf'C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\확정본\광고비 추가\{df_name}_{column_name}_{window_size}_movig_av_{n_std_dev}_std_dev_moved_with_ad_spend.png', format='png', dpi=300, bbox_inches='tight')
        
        # 그래프 출력
        plt.show()
        plt.close()


# window size에 따른 적정범위 차이 설명을 위한 코드


import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import matplotlib.font_manager as fm

# 맞춤 포맷터 함수 정의
def format_number(x, pos):
    if x >= 1e6:
        return f'{x/1e6:.1f}M'
    elif x >= 1e3:
        return f'{x/1e3:.1f}K'
    else:
        return f'{x:.0f}'

# 한글 폰트 설정
font_path = r'C:\Users\User\AppData\Local\Microsoft\Windows\Fonts\SamsungOneKorean-400_v1.2_hinted.ttf'  
font_prop = fm.FontProperties(fname=font_path)

# 브랜드와 컬럼 지정
df_name = 'sws'
column_name = 'returningVisitors'

# 표준편차 1배수
n_std_dev = 1

# window_size 리스트
window_sizes = [30, 60, 90, 120, 180]

# 각 window_size에 대해 루프 실행
for window_size in window_sizes:
    # 데이터프레임 로드
    df = eval(df_name)[['std_date', column_name, 'ad_spend']].copy()
    df.loc[:, 'std_date'] = pd.to_datetime(df['std_date'])

    # 해당 컬럼의 모든 값이 0인지 확인
    if df[column_name].sum() == 0:
        print(f"브랜드: {df_name}, 컬럼: {column_name}의 모든 값이 0입니다. 이 컬럼은 건너뜁니다.")
        continue  # 다음 window_size로 넘어감
    
    # 전체 기간의 평균 및 표준편차 계산
    overall_mean = df[column_name].mean()
    overall_std = df[column_name].std()

    # 이동 평균 계산을 위한 대체된 값 생성 (초과할 경우에만 대체)
    threshold = overall_mean + 3 * overall_std
    df.loc[:, 'adjusted_for_moving_avg'] = df[column_name].apply(lambda x: x if x <= threshold else threshold)

    # 이동 평균 및 이동 표준 편차 계산
    df.loc[:, 'moving_avg'] = df['adjusted_for_moving_avg'].rolling(window=window_size, min_periods=window_size).mean()
    df.loc[:, 'moving_std'] = df['adjusted_for_moving_avg'].rolling(window=window_size, min_periods=window_size).std()

    # 동적으로 적정 범위 계산
    df.loc[:, 'lower_bound'] = df['moving_avg'] - n_std_dev * df['moving_std']
    df.loc[:, 'upper_bound'] = df['moving_avg'] + n_std_dev * df['moving_std']

    # 적정 범위 미달 및 초과 날짜 필터링
    below_range = df[df[column_name] < df['lower_bound']]
    above_range = df[df[column_name] > df['upper_bound']]
    within_range = df[(df[column_name] >= df['lower_bound']) & (df[column_name] <= df['upper_bound'])]

    # 적정범위 일수 계산
    total_days = len(within_range) + len(above_range) + len(below_range)
    print(f"브랜드: {df_name}, 컬럼: {column_name}, 윈도우 사이즈: {window_size}, 표준편차 배수: {n_std_dev}")
    print(f"적정 범위 내 일수: {len(within_range)}일")
    print(f"적정 범위 초과 일수: {len(above_range)}일")
    print(f"적정 범위 미달 일수: {len(below_range)}일")
    print(f"총 일수: {total_days}일")

    # 결과를 엑셀로 저장
    df.to_excel(rf"C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\windowsize 설명용\{df_name}_{column_name}_{window_size}_movig_av_{n_std_dev}_std_dev_moved.xlsx", index=False)
            
    # 시계열 그래프 생성
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # 주 축 (왼쪽 y축) 설정
    ax1.plot(df['std_date'], df[column_name], label=f'{column_name}', color='black', alpha=0.5)
    ax1.plot(df['std_date'], df['moving_avg'], label=f'{window_size}-Day Moving Average', color='orange')
    ax1.plot(df['std_date'], df['lower_bound'], color='red', linestyle='--', label='Lower Bound')
    ax1.plot(df['std_date'], df['upper_bound'], color='green', linestyle='--', label='Upper Bound')

    ax1.set_xlabel('Date')
    ax1.set_ylabel(f'{column_name}', color='black', fontproperties=font_prop)
    ax1.tick_params(axis='y', labelcolor='black')

    # 보조 축 (오른쪽 y축) 설정
    ax2 = ax1.twinx()
    ax2.plot(df['std_date'], df['ad_spend'], label='Ad Spend', color='purple', alpha=0.5)
    ax2.set_ylabel('Ad Spend', color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')

    # 맞춤 포맷터 적용
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_number))
    
    # 그래프 제목 설정
    plt.title(f'{df_name} - {column_name} Time Series with Dynamic Appropriate Range and Ad Spend (Window: {window_size})', fontproperties=font_prop)

    # 범례 설정
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', prop=font_prop)

    # 적정 범위 텍스트 추가
    texts = [
        ax1.text(df['std_date'].iloc[-1], df['upper_bound'].iloc[-1], f"Upper Bound: {df['upper_bound'].iloc[-1]:.2f}", 
                 color='green', verticalalignment='bottom'),
        ax1.text(df['std_date'].iloc[-1], df['lower_bound'].iloc[-1], f"Lower Bound: {df['lower_bound'].iloc[-1]:.2f}", 
                 color='red', verticalalignment='top'),
        ax1.text(df['std_date'].iloc[-1], df['moving_avg'].iloc[-1], f"Mean: {df['moving_avg'].iloc[-1]:.2f}", 
                 color='orange', verticalalignment='bottom'),
        ax1.text(df['std_date'].max(), df[column_name].max(), 
                 f"Within Days: {len(within_range)}\n Above Days: {len(above_range)}\n Below Days: {len(below_range)}",
                 horizontalalignment='right', verticalalignment='top', color='black', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
    ]

    # 텍스트 위치 조정
    adjust_text(texts, only_move={'points': 'y', 'texts': 'y'}, arrowprops=dict(arrowstyle='->', color='gray'))

    plt.grid(True)
    
    # 그래프를 이미지로 저장
    plt.savefig(rf'C:\Users\User\Documents\업무\2023\DS\아모레퍼시픽\Incremental 성과 측정\windowsize 설명용\{df_name}_{column_name}_{window_size}_movig_av_{n_std_dev}_std_dev_moved_with_ad_spend.png', format='png', dpi=300, bbox_inches='tight')
    
    # 그래프 출력
    plt.show()
    plt.close()
