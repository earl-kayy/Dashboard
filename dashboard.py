from datetime import datetime

import streamlit as st
from streamlit_modal import Modal
from streamlit_option_menu import option_menu

from log_manager import *
from data_manager import *
from visual_tool import *

st.set_page_config(
    page_title = 'Dashboard',
    page_icon = "📈",
    layout = 'wide',
    initial_sidebar_state= 'expanded'
)


# 금일 날짜 표시
today_date = datetime.now().strftime("%Y-%m-%d")
st.sidebar.markdown(f"### {today_date}")

# 사이드 바에 Data/Log 중 무엇을 볼지 정의
with st.sidebar:
    option = option_menu("Menu", ['Data Navigator','Log Information'],
                         icons = ['compass', 'clock-history'],
                         menu_icon = 'window-stack',
                         styles={
                        "container": {"padding": "0!important", "background-color": "#fafafa"},
                        "icon": {"color": "black", "font-size": "17px"},
                        "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#b5ffff"},
                        "nav-link-selected": {"background-color": "#00ffff"},
                        })
# 세션 별 데이터 관리하는 객체 생성 (세션이 새로 고침되면 객체 다시 생성)
if 'data_manager' not in st.session_state:
    st.session_state['data_manager'] = DataManager()

# 세션 별 로그 관리하는 객체 생성 (세션 새로 고침되면 객체 다시 생성)
if 'log_manager' not in st.session_state:
    st.session_state['log_manager'] = LogManager()

if option == 'Data Navigator':
    st.sidebar.markdown("<br><br><br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown('---')

    nav_option = st.sidebar.radio('Select Navigating Option 🔍', ['Status', 'Distribution', 'Duration'])

    col1, col0 = st.columns((8, 2))
    with col0:
        VisualTool.plot_main_dist(st.session_state['data_manager'].get_main_distribution())
    with col1:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(
                    """
                    <style>
                    .spacer {
                        height: 466px;
                    }
                    </style>
                    <div class="spacer"></div>
                    """,
                    unsafe_allow_html=True
                )
            st.markdown('---')
    if nav_option == 'Status':
        with col1:

            # placeholder = st.empty()
            # with placeholder.container():
            #     st.markdown(
            #         """
            #         <style>
            #         .spacer {
            #             height: 466px;
            #         }
            #         </style>
            #         <div class="spacer"></div>
            #         """,
            #         unsafe_allow_html=True
            #     )
            # st.markdown("---")

            input_date, input_main, input_category = st.columns([6, 4, 4])

            with input_date:
                start_date = st.date_input('Start date', min_value=pd.to_datetime('2023-08-01'), value = pd.to_datetime('2023-08-01'), max_value=pd.to_datetime(today_date))
                end_date = st.date_input('End date', min_value=pd.to_datetime('2023-08-01'),value = 'today', max_value=pd.to_datetime(today_date))
                
            
            with input_main:
                selected_main = st.radio(
                    "Select MAIN:",
                    ['Total', 'Korean', 'English']
                )
                selected_main = selected_main.lower()
                if selected_main == 'total':
                    selected_main = None

            with input_category:
                dynamic_option = st.empty()
                if selected_main != None:
                    with dynamic_option.container():
                        selected_category = st.selectbox(
                                                "Select CATEGORY",
                                                st.session_state['data_manager'].get_main_components(selected_main),
                                                index = None
                                            )
                else:
                    selected_category = None

            st.markdown("---")
            col0, col1 = st.columns([9.2,0.8])
            with col1:
                st.markdown(
                    """
                    <style>
                    .spacer {
                        height: 30px;
                    }
                    </style>
                    <div class="spacer"></div>
                    """,
                    unsafe_allow_html=True
                )
                filter = st.button("FILTER")
            with placeholder.container():
                VisualTool.plot_datewise_CDF(st.session_state['data_manager'].count_entries_datewise(min_date = start_date, max_date = end_date, main = selected_main, category = selected_category))
            if filter: # 날짜 반영이 안됨 (날짜로 필터링 하는 함수 필요)
                with placeholder.container():
                    VisualTool.plot_datewise_CDF(st.session_state['data_manager'].count_entries_datewise(min_date = start_date, max_date = end_date, main = selected_main, category = selected_category))

    
    elif nav_option == 'Distribution':
        with col1:
            # placeholder = st.empty()
            # with placeholder.container():
            #     st.markdown(
            #         """
            #         <style>
            #         .spacer {
            #             height: 466px;
            #         }
            #         </style>
            #         <div class="spacer"></div>
            #         """,
            #         unsafe_allow_html=True
            #     )
            # st.markdown("---")
            c0, c1 = st.columns([3,7])
            with c0:
                search_option = st.radio("Search for",
                                ['CATEGORY', 'DETAIL']
                                )
            with c1:
                dynamic_nav = st.empty()
                
                if search_option == 'CATEGORY':
                    with dynamic_nav.container():
                        search_queries = st.multiselect('Highlight Category', st.session_state['data_manager'].get_category_distribution()['label'])
                    with placeholder.container():    
                        VisualTool.plot_cat_dist(st.session_state['data_manager'].get_category_distribution(), search_queries)

                
                elif search_option == 'DETAIL':
                    with dynamic_nav.container():
                        categories = st.session_state['data_manager'].get_categories()
                        selected_categories = st.multiselect(
                            'Select Categories (max 2):',
                            categories,
                            help = 'You can select up to 2 options'
                        )
                    with placeholder.container():
                        # 개수 제한
                        if len(selected_categories) > 2:
                            st.error('You can select up to 2 categories')
                            selected_categories = selected_categories[:2]
                        
                        # 하나라도 선택되면 그 이후부터는 출력
                        if len(selected_categories) > 0:
                            columns = st.columns(len(selected_categories))

                            for col, category in zip(columns, selected_categories):
                                with col: # 여기서 만약 category 가 지도라면 => 지도로 시각화.(지도 뿐만 아니라 아이콘 추가)
                                    st.markdown(f"### {category}")
                                    if category == 'DialectSpeech' or category == 'KforeignSpeech':
                                        VisualTool.plot_detail_dist(st.session_state['data_manager'].get_detail_distribution(category), category)
                                    else:
                                        VisualTool.plot_detail_dist(st.session_state['data_manager'].get_detail_distribution(category))


    
    elif nav_option == 'Duration':
        with placeholder.container():# 이것도 navigating 하는 식으로/interactive 하게 추가할 사항 있으면 추가
            VisualTool.plot_duration_hist(st.session_state['data_manager'].count_entries_durationwise())

    # st.markdown(
    #         """
    #         <style>
    #         .st-emotion-cache-l6wp7i {
    #             min-width: 700px !important;
    #             width: 700px;
    #             max-width: 800px !important;
    #             position: fixed !important;
    #             top: 50% !important;
    #             left: 50% !important;
    #             transform: translate(-50%, -50%);
    #             display: flex;
    #             flex: 1 1 0%;
    #             flex-direction: column;
    #             min-height: 400px !important;
    #             height: 500px;
    #             max-height: 600px !important; 
    #             overflow-y: auto;
    #         }
    #         </style>
    #         """,
    #         unsafe_allow_html=True
    #     )

    # modal = Modal(key = 'table_data', title = 'Table')
    # col0, col1, col2, col3 = st.columns([5, 5, 2, 2])
    # with col3:
    #     if st.button('Table'):
    #         modal.open()

    #     if modal.is_open():
    #         with modal.container():
    #             st.dataframe(st.session_state['data_manager'].count_entries_datewise())


        # 위치 조정정
        # st.markdown(
        #     """
        #     <style>
        #     .st-emotion-cache-l6wp7i {
        #         min-width: 700px !important;
        #         width: 700px;
        #         max-width: 800px !important;
        #         position: fixed !important;
        #         top: 50% !important;
        #         left: 50% !important;
        #         transform: translate(-50%, -50%);
        #         display: flex;
        #         flex: 1 1 0%;
        #         flex-direction: column;
        #         min-height: 400px !important;
        #         height: 500px;
        #         max-height: 600px !important; 
        #         overflow-y: auto;
        #     }
        #     </style>
        #     """,
        #     unsafe_allow_html=True
        # )

        # modal = Modal(key = 'table_data', title = 'Table')
        # col0, col1, col2, col3 = st.columns([5, 5, 2, 2])
        # with col3:
        #     if st.button('Table'):
        #         modal.open()

        #     if modal.is_open():
        #         with modal.container():
        #             main, kor, eng = st.tabs(['MAIN', 'KOR', 'ENG'])
        #             with main:
        #                 st.table(st.session_state['data_manager'].show_main_distribution())
        #             with kor:
        #                 st.table(st.session_state['data_manager'].show_category_distribution(st.session_state['data_manager'].get_main_components('korean')))
        #             with eng:
        #                 st.table(st.session_state['data_manager'].show_category_distribution(st.session_state['data_manager'].get_main_components('english')))

# 사이드 바에서 Log Information 선택했을 경우
elif option == 'Log Information':
    if 'success_message' not in st.session_state:
        st.session_state['success_message'] = False

    st.header('Log 기록')

    # 입력
    st.session_state['log_manager'].log_input()

    st.session_state['log_manager'].show_logs()
    # 성공적으로 저장되면 알림
    st.session_state['log_manager'].notify()

    # # 전체 선택 버튼/삭제 버튼 추가
    col0, col1 = st.columns(2)
    with col0:
        delete_button = st.button('Delete')
        if delete_button:
            st.session_state['log_manager'].delete_logs()

    st.session_state['log_manager'].save_log()