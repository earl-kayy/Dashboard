from datetime import datetime

import streamlit as st
from streamlit_modal import Modal
from streamlit_option_menu import option_menu
from streamlit_extras.grid import grid

from log_manager import *
from data_manager import *
from visual_tool import *

st.set_page_config(
    page_title = 'Dashboard',
    page_icon = "📈",
    layout = 'wide',
    initial_sidebar_state= 'expanded'
)

st.logo(image='./data/logo.png')

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

    # nav_option = st.sidebar.radio('Select Navigating Option 🔍', ['Status', 'Distribution', 'Duration'])
    
    # 전체 화면 분할
    col0, col1 = st.columns((8, 2))
    with col0:
        vis_placeholder = st.empty()
        with vis_placeholder.container():
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

        nav_grid = grid([2, 3, 2, 2])
        nav_option = nav_grid.radio('Select Navigating Option 🔍', ['Status', 'Distribution'])
        nav_placeholder_1 = nav_grid.empty()
        nav_placeholder_2 = nav_grid.empty()
        nav_placeholder_3 = nav_grid.empty()
        st.markdown('---')
    with col1:
        # 변화랑/통계 정보 전달 위한 placeholder
        stats_upper_placeholder = st.empty()
        
        # 변화량/통계 정보 전달 위한 placeholder
        stats_lower_placeholder = st.empty()
    
    if nav_option == 'Status':

        with nav_placeholder_1.container():

        # with input_date:
            start_date = st.date_input('Start date', min_value=pd.to_datetime('2023-08-01'), value = pd.to_datetime('2023-08-01'), max_value=pd.to_datetime(today_date))
            end_date = st.date_input('End date', min_value=pd.to_datetime('2023-08-01'),value = 'today', max_value=pd.to_datetime(today_date))
                
            
        with nav_placeholder_2:
            selected_main = st.radio(
                "Select MAIN:",
                ['Total', 'Korean', 'English']
            )
            selected_main = selected_main.lower()
            if selected_main == 'total':
                selected_main = None

        if selected_main != None:
            with nav_placeholder_3.container():
                selected_category = st.selectbox(
                                        "Select CATEGORY",
                                        st.session_state['data_manager'].get_main_components(selected_main),
                                        index = None
                                    )
            with stats_upper_placeholder.container():
                VisualTool.plot_cat_partial(st.session_state['data_manager'].get_category_distribution(), st.session_state['data_manager'].get_main_components(selected_main))

        else:
            selected_category = None
            with stats_upper_placeholder.container():
                VisualTool.plot_main_dist(st.session_state['data_manager'].get_main_distribution())

        with vis_placeholder.container():
            VisualTool.plot_datewise_CDF(st.session_state['data_manager'].count_entries_datewise(min_date = start_date, max_date = end_date, main = selected_main, category = selected_category))
    
        with stats_lower_placeholder.container():
            # 이거 수치보면 필터링 잘못돼고 있음(시작 일자 기준으로 필터링 되고 있음)
            # 문제 : 누적 수치가 날짜 바꿀 때마다 계산 되고 있음
            # 해결 : data_manager 클래스 수정 (날짜에 대해 filter 하는 애 따로)
            st.table(st.session_state['data_manager'].count_entries_datewise(min_date = start_date, max_date = end_date, main = selected_main, category = selected_category))

            start_cumulative = st.session_state['data_manager'].count_entries_datewise(min_date = start_date, max_date = end_date, main = selected_main, category = selected_category)['cumulative'].iloc[0]
            end_cumulative = st.session_state['data_manager'].count_entries_datewise(min_date = start_date, max_date = end_date, main = selected_main, category = selected_category)['cumulative'].iloc[-1]
            cumulative_change = end_cumulative - start_cumulative

            if start_cumulative != 0:
                cumulative_change_rate = cumulative_change/start_cumulative*100
            else:
                cumulative_change_rate = 0

            st.metric(label = 'Change Rate', value = f"{end_cumulative/1000} K", delta = f"{cumulative_change_rate:.2f}%")

    elif nav_option == 'Distribution':

        with nav_placeholder_1:
            info_option = st.radio("Search for",
                                ['Classification_Info', 'Content_Info']
                                )
        
        with nav_placeholder_2:

            # 분류에 따른 분포 : 중/소분류 중심
            if info_option == 'Classification_Info':
                search_option = st.radio("Search for",
                                        ['CATEGORY', 'DETAIL']
                                        )
                # 각 category 에 대한 설명 : classification_info 일 때 필요한 정보들
                with stats_upper_placeholder.container():
                    st.markdown(
                        """
                        <style>
                        .spacer {
                            height: 90px;
                        }
                        </style>
                        <div class="spacer"></div>
                        """,
                        unsafe_allow_html=True
                    )
                    if q_prompt := st.chat_input("Category name: "):
                        st.chat_message('user').write(q_prompt)
                        
                        explanation = st.session_state['data_manager'].get_category_explanations(q_prompt.lower())
                        
                        if explanation == None:
                            st.chat_message("assistant").write("No match of category")
                        else:
                            st.chat_message('assistant').write(f"{explanation}")
                    

            # 내부 컨텐츠의 분포 : category 중심
            elif info_option == 'Content_Info':
                search_option = st.radio('Search for',
                                        ['SCRIPT', 'DURATION']
                                        )
                
        if search_option == 'CATEGORY':
            with nav_placeholder_3.container():
                search_queries = st.multiselect('Highlight Category', st.session_state['data_manager'].get_category_distribution()['label'])
            with vis_placeholder.container():    
                VisualTool.plot_cat_dist(st.session_state['data_manager'].get_category_distribution(), search_queries)
        
        elif search_option == 'DETAIL':
            with nav_placeholder_3.container():
                categories = st.session_state['data_manager'].get_categories()
                selected_categories = st.multiselect(
                    'Select Categories (max 2):',
                    categories,
                    help = 'You can select up to 2 options'
                )

            with vis_placeholder.container():
                # 초기 공간 보정 위한 마크업(ryoonki)
                if len(selected_categories) == 0:
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

        elif search_option == 'SCRIPT':
            # Script 의 평균 단어 개수, 중앙값
            with stats_upper_placeholder.container():
                pass
            # 여기 단어 개수에 대한 행 단위 평균값, 중앙값
            with stats_lower_placeholder.container():
                pass
        elif search_option == 'DURATION':

            # duration 관련 통계 정보
            with stats_upper_placeholder.container():
                st.header("Duration (s)")
                st.metric(label = 'Total', value = f"{st.session_state['data_manager'].count_entries_durationwise()['duration'].sum()/1000000:.1f}M")
                st.metric(label = 'Mean', value = f"{st.session_state['data_manager'].count_entries_durationwise()['duration'].mean():.2f}")
                st.metric(label = 'Median', value = st.session_state['data_manager'].count_entries_durationwise()['duration'].median())

            with nav_placeholder_3.container():

                preference = st.toggle('Watch Total', value=True)
                # 전체적인 duration 에 대한 histogram
                if preference:
                    with vis_placeholder.container():
                        VisualTool.plot_duration_hist(st.session_state['data_manager'].count_entries_durationwise())
                # 특정 category 별 duration 의 분포
                else:
                    category_selection = st.selectbox(
                        "Select specific Category",
                        st.session_state['data_manager'].get_category_distribution()['label'],
                        index = 0
                    )
                    with vis_placeholder.container():
                        VisualTool.plot_duration_line(st.session_state['data_manager'].count_entries_durationwise(category = category_selection))


            # c0, c1 = st.columns([3,7])
            # with c0:
            #     search_option = st.radio("Search for",
            #                     ['CATEGORY', 'DETAIL']
            #                     )
            # with c1:
            #     dynamic_nav = st.empty()
                
            #     if search_option == 'CATEGORY':
            #         with dynamic_nav.container():
            #             search_queries = st.multiselect('Highlight Category', st.session_state['data_manager'].get_category_distribution()['label'])
            #         with vis_placeholder.container():    
            #             VisualTool.plot_cat_dist(st.session_state['data_manager'].get_category_distribution(), search_queries)

                
            #     elif search_option == 'DETAIL':
            #         with dynamic_nav.container():
            #             categories = st.session_state['data_manager'].get_categories()
            #             selected_categories = st.multiselect(
            #                 'Select Categories (max 2):',
            #                 categories,
            #                 help = 'You can select up to 2 options'
            #             )
            #         with vis_placeholder.container():
            #             # 개수 제한
            #             if len(selected_categories) > 2:
            #                 st.error('You can select up to 2 categories')
            #                 selected_categories = selected_categories[:2]
                        
            #             # 하나라도 선택되면 그 이후부터는 출력
            #             if len(selected_categories) > 0:
            #                 columns = st.columns(len(selected_categories))

            #                 for col, category in zip(columns, selected_categories):
            #                     with col: # 여기서 만약 category 가 지도라면 => 지도로 시각화.(지도 뿐만 아니라 아이콘 추가)
            #                         st.markdown(f"### {category}")
            #                         if category == 'DialectSpeech' or category == 'KforeignSpeech':
            #                             VisualTool.plot_detail_dist(st.session_state['data_manager'].get_detail_distribution(category), category)
            #                         else:
            #                             VisualTool.plot_detail_dist(st.session_state['data_manager'].get_detail_distribution(category))

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