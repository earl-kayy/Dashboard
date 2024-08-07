import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

class LogManager:

    # 생성자 정의(객체 생성 시, 현재 시점의 로그 기록 읽어오기)
    # 세션 바뀔 때마다 객체 생성
    def __init__(self):
        self.__log_df = self.__load_log()
        self.__refresh_logs() # 세션 바뀔 때마다, delete 열을 false 로
    
    # 로그를 로드해오거나 없으면 새롭게 생성
    def __load_log(self):
        if os.path.exists('./data/log_data.csv'):
            return pd.read_csv('./data/log_data.csv')
        else: # 가장 초기일 경우, 데이터 프레임 생성
            return pd.DataFrame(columns = ['delete', 'time', 'log'])

    # 추가된 로그를 행으로 생성
    def __log_row_create(self, mod):
        now = datetime.now()
        df = pd.DataFrame({'delete': False, 'time': [now.strftime('%Y-%m-%d %H:%M:%S')], 'log':[mod]})
        return df

    # 입력(엔터) 후, 입력 버퍼를 비우는 역할 (만일 log_input 함수를 수정본으로 하면 얘도 수정해야 됨)
    def __flush_buf(self):
        mod = st.session_state['log_input']
        if mod:
            mod_df = self.__log_row_create(mod)
            self.__log_df = pd.concat([mod_df, self.__log_df], ignore_index = True)
            self.save_log()
            # st.session_state['log_input'] = "" # 입력 버퍼 비우기

            self.__signal_session_state() # 메시지 성공적으로 입력했다고 신호 보냄

    # 새로 고침할 경우(세션 바뀌면), delete 열 refresh
    # 같은 세션 내에선 체크된 정보 유지됨
    def __refresh_logs(self):
        self.__log_df.loc[:, ['delete']] = False  

    # 메시지 입력 시 성공적으로 입력했다고 session_state(전역변수)에 신호 보냄
    def __signal_session_state(self):
        st.session_state['success_message'] = True

    # 로그를 csv 로 저장
    def save_log(self):
        self.__log_df.to_csv('./data/log_data.csv', index = False)
        
    # 로그를 입력하는 함수(수정본)
    def log_input(self):
        with st.container():
            st.chat_input("수정 사항을 입력하세요", key="log_input", on_submit=self.__flush_buf)
    
    # 체크된 행 삭제
    def delete_logs(self):
        self.__log_df = self.__log_df.drop(self.__log_df[self.__log_df['delete'] == True].index, axis = 0)
    
    # 로그 데이터 출력 (수정 했을 때, 반영되게끔 구현)
    # 데이터 에디터에 수정사항이 생기면, __signal_session_state() 함수 호출
    def show_logs(self):
        self.__log_df = st.data_editor(self.__log_df, width = 800, hide_index = True) 

    def notify(self):
        if st.session_state['success_message'] == True:
            with st.empty():
                st.success("로그가 성공적으로 저장되었습니다.")
                time.sleep(0.7)
                st.write("")
        st.session_state['success_message'] = False