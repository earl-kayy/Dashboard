import os

import pandas as pd
import streamlit as st


# 모든 데이터 여기서 관리

class DataManager:
    def __init__(self):
        # 전체적인 데이터 불러오기
        self.__data_df = self.load_df()

        # main 카테고리로 분류된 데이터 프레임
        self.__main_distribution = self.__set_main_distribution()

        ### 추가하는 부분 (main component) 넣는 부분.
        self.__main_components = self.__set_main_components()
        
        # 각 category 에 대한 설명을 담고 있는 데이터 프레임
        self.__category_explanations = self.__set_category_explanations()

        # category 로 분류된 데이터 프레임
        self.__category_distribution = self.__set_category_distribution()

        # 하위 카테고리를 갖는 상위 카테고리명 관리 (수정 필요)
        self.__categories = self.__set_categories()

        # 하위 카테고리 : 해당 카테고리의 분포 df 관리하는 딕셔너리
        self.__detail_distributions = {}

        # 하위 카테고리의 분포를 관리하는 딕셔너리 구성
        for category in self.__categories:
            self.__detail_distributions[category] = self.__set_detail_distribution(category)

    #data 관련 csv 파일 불러오기
    @st.cache_data(persist = 'disk')
    def load_df(__self, route = './data/meta_data.csv'):
        if os.path.exists(route):
            df = pd.read_csv(route)
            print("데이터 로딩중...")
            return df
        else:
            return None
        
    # main 카테고리의 분포 업데이트
    @st.cache_data(persist = 'disk')
    def __set_main_distribution(__self):
        df = __self.__data_df['main'].value_counts().to_frame(name = 'count')
        df = df.reset_index().rename(columns = {'main' : 'label'})
        df['count'] = df['count'].astype(int)
        return df
    
    # kor/english 내부 sub 카테고리 정리 위한 setter
    @st.cache_data(persist = 'disk')
    def __set_main_components(__self):
        return __self.__data_df.groupby('main')['category'].apply(lambda x: x.unique())
    
    # category 별 설명을 담는 데이터 프레임
    def __set_category_explanations(self):
        return pd.read_csv('./data/cat_explanation.csv')
    
    # 주 카테고리의 분포 업데이트(새로운 데이터 들어왔을 때)
    @st.cache_data(persist = 'disk')
    def __set_category_distribution(__self):
        df = __self.__data_df['category'].value_counts().to_frame(name = 'count')
        df = df.reset_index().rename(columns = {'category' : 'label'})
        df['count'] = df['count'].astype(int)
        return df
    
    # detail 분류가 있는 카테고리 설정
    @st.cache_data(persist = 'disk')
    def __set_categories(__self):
        category_list = __self.__data_df[__self.__data_df['detail'] != '-']['category'].unique()
        return category_list
    
    # 하위 카테고리 중 하나의 분포 업데이트
    @st.cache_data(persist = 'disk')
    def __set_detail_distribution(__self, category):
        df = __self.__data_df[__self.__data_df['category']==category]['detail'].value_counts().to_frame(name = 'count')
        df = df.reset_index().rename(columns = {'detail' : 'label'})
        df['count'] = df['count'].astype(int)
        return df

    # 출력용(format 처리) - 상위 카테고리 용 (출력만을 위한 함수, 실제 객체 내부에 저장되는건 int 형, 이 함수를 통해 출력되는건 obj 형)
    def show_main_distribution(self):
        return self.__main_distribution.style.format(thousands = ',')

    # 일부 항목만 선택해서 출력 가능
    def show_category_distribution(self, selected_categories):
        # 기본적으로 전체 항목을 보여줌
        if selected_categories == None:
            return self.__category_distribution.style.format(thousands=',')
        else: # 선택한 항목들만 보여줌
            return self.__category_distribution.loc[self.__category_distribution['label'].isin(selected_categories)].style.format(thousands=',')
    
    def get_main_distribution(self):
        return self.__main_distribution
    
    # kor/english 의 내부 sub 카테고리들
    def get_main_components(self, main_category):
        return self.__main_components[main_category].tolist()
    
    # category 별 설명을 가진 데이터 프레임 가져옴
    def get_category_explanations(self, category):
        explanation = self.__category_explanations[self.__category_explanations['category'].str.lower() == category]['explanation']
        if explanation.empty:
            return None
        return explanation.iloc[0]
    
    def get_category_distribution(self):
        return self.__category_distribution
    
    # sub_categories 가져오기
    def get_categories(self):
        return self.__categories
    
    # sub_distributions 중에서 하나만 지정해서 가져오기
    def get_detail_distribution(self, category):
        return self.__detail_distributions[category]


    # 이 밑으로 나오는 함수들은 일반화 하는 과정 + 수정 필요 : 역할 별로 함수 나누고 재구성해야될수도 있음
    # 날짜 별 value_count (detail 부분은 일단 안쓰는중) => 추후에 함수 2개로 나눌 수도 있을듯(detail 부분 시각화 할때 위해서, 필터링하는 함수 + 그걸 가지고 value_count 하는 함수)
    # value_count 하는 함수는 어떤걸 기준으로 value_count() 할지 결정되면 그대로 처리함
    def count_entries_datewise(self, min_date = None, max_date = None, main = None, category = None, detail = None):
        if min_date != None and max_date != None:
            # 'time' 열을 datetime으로 변환하고, date만 추출하여 비교
            date_df = self.__data_df[(pd.to_datetime(self.__data_df['time']).dt.date >= min_date) & (pd.to_datetime(self.__data_df['time']).dt.date <= max_date)]

        else:
            date_df = self.__data_df

        if main == None:
            date_df = date_df['time'].value_counts().to_frame()
            date_df.index = pd.to_datetime(date_df.index).date
            date_df = date_df.sort_index()
            date_df.columns = ['count']
            date_df['cumulative'] = date_df['count'].cumsum()
            return date_df
        
        elif category == None:
            date_df = date_df[date_df['main'] == main]
            date_df = date_df['time'].value_counts().to_frame()
            date_df.index = pd.to_datetime(date_df.index).date
            date_df = date_df.sort_index()
            date_df.columns = ['count']
            date_df['cumulative'] = date_df['count'].cumsum()
            return date_df
        
        elif detail == None:
            date_df = date_df[date_df['category'] == category]
            date_df = date_df['time'].value_counts().to_frame()
            date_df.index = pd.to_datetime(date_df.index).date
            date_df = date_df.sort_index()
            date_df.columns = ['count']
            date_df['cumulative'] = date_df['count'].cumsum()
            return date_df
        
        else:
            date_df = date_df[date_df['detail'] == detail]
            date_df = date_df['time'].value_counts().to_frame()
            date_df.index = pd.to_datetime(date_df.index).date
            date_df = date_df.sort_index()
            date_df.columns = ['count']
            date_df['cumulative'] = date_df['count'].cumsum()
            return date_df
        
    # 전체에 대한 histogram 그릴때는 필요없음.
    def count_entries_durationwise(self, main=None, category=None):
        if main == None and category == None:
            temp = self.__data_df['duration'].to_frame()
            return temp
        elif category != None:
            temp = self.__data_df[self.__data_df['category'] == category]['duration'].to_frame()
            return temp
        else:
            pass
        