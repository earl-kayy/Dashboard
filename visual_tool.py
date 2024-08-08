import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import json
import altair as alt
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

class VisualTool:

    @staticmethod
    def plot_main_dist(main_distribution):
        base = alt.Chart(main_distribution).encode(
            theta = alt.Theta("count:Q", stack=True),
            radius = alt.Radius("count", scale = alt.Scale(type='sqrt', zero = True, rangeMin=20)),
            color = alt.Color('label:N', scale = alt.Scale(domain=['korean', 'english'], range=['#29b5e8', '#155F7A']), legend=None)
        )
        c1 = base.mark_arc(innerRadius=30, stroke='#0000')
        c2 = base.mark_text(radiusOffset=20).encode(text = 'label')

        chart = c1 + c2
        st.altair_chart(chart, theme = 'streamlit', use_container_width=True)

    # 선택한 항목 하이라이트하기 위해
    @staticmethod
    def plot_cat_dist(category_distribution, search_queries):
        
        if not search_queries:
            colors = ['#1f77b4'] * len(category_distribution)
        else:
            colors = [
                '#ff0000' if any(query.lower() == idx.lower() for query in search_queries) else '#1f77b4'
                for idx in category_distribution['label']
            ]

        fig = px.bar(
            category_distribution,
            x = 'count',
            y = 'label',
            text = (category_distribution['count']/category_distribution['count'].sum()*100).round(2).astype(str) + '%',
            width = 800,
            height = 800,
            orientation = 'h',
            title = 'Category Distribution'
        ).update_yaxes(categoryorder = 'total ascending')
        fig.update_traces(marker_color = colors)
        st.plotly_chart(fig)
    
    # 선택한 항목만 볼 수 시각화
    @staticmethod
    def plot_cat_partial(category_distribution, categories):
        temp_df = category_distribution.loc[category_distribution['label'].isin(categories)]

        temp_df['percentage'] = (temp_df['count']/(temp_df['count'].sum()))*100
        fig = px.bar(
            temp_df,
            x = 'label',
            y = 'percentage',
            width = 450,
            height = 400,
            orientation = 'v'
        ).update_xaxes(categoryorder = 'total descending')
        st.plotly_chart(fig)

    @staticmethod
    def plot_detail_dist(detail_distribution, category = None):
        if category == None:
            labels = detail_distribution['label']
            values = detail_distribution['count']
            
            colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880']
            
            # 파이 차트 생성
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.4,  # 도넛 차트 모양
                hoverinfo="label+percent+value",
                textinfo='label+percent',  # 내부에 레이블 표시
                textfont=dict(size=12, color='#FFFFFF', family='Arial Black'),  # 글자 크기 줄임
                marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
                pull=[0.1 if i == values.idxmax() else 0 for i in range(len(values))]
            )])

            # 레이아웃 설정
            fig.update_layout(
                showlegend=False,  # 범례를 사용하지 않음
                paper_bgcolor='#FFFFFF',  # 밝은 배경색
                plot_bgcolor='#FFFFFF',  # 밝은 배경색
                font=dict(color='#000000'),
                margin=dict(t=0, b=0, l=0, r=0)
            )

            # 애니메이션 효과 추가
            fig.update_traces(
                hoverinfo="label+percent+value",
                textinfo="label+percent",
                marker=dict(line=dict(color='#FFFFFF', width=1))
            )

        else:
            geojson_file_path = './data/kor_geomap.json'
            with open(geojson_file_path, 'r', encoding = 'utf-8') as f:
                geojson_data = json.load(f)
            
            featureidkey = 'properties.CTP_KOR_NM' if category == 'KforeignSpeech' else 'properties.CTP_ENG_NM'

            fig = px.choropleth(
                detail_distribution,
                geojson=geojson_data,
                locations='label',
                color = 'count',
                color_continuous_scale='greens',
                range_color = (0, max(detail_distribution['count'])),
                featureidkey=featureidkey,  # GeoJSON 파일의 속성 이름과 일치해야 함
                labels={'count': 'Count'}
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(
                margin={"r":0, "t":0, "l":0, "b":0},
                height = 500
                )
            
        # 차트 렌더링
        st.plotly_chart(fig)


    # 이 밑으로는 수정 필요(위에 것과 겹치거나, 일반화 및 최적화) + 함수 순서도 조금씩 바꿔주면 좋지 (main, cat, detail 순서대로)
    # 날짜별 누적 분포를 그려내는 함수
    @staticmethod
    def plot_datewise_CDF(datewise_CDF):
        # 라인 차트 생성
        fig = go.Figure()
        
        # 누적 라인 차트
        fig.add_trace(go.Scatter(
            x=datewise_CDF.index,
            y=datewise_CDF['cumulative'],
            mode='lines',
            line=dict(color='royalblue', width=4),
            name='Cumulative Data'
        ))
        
        # 점 추가
        fig.add_trace(go.Scatter(
            x=datewise_CDF.index,
            y=datewise_CDF['cumulative'],
            mode='markers',
            marker=dict(
                color='red',
                size=12,
                symbol='circle',
                line=dict(color='black', width=2)
            ),
            name='Data Points'
        ))

        # 레이아웃 수정
        fig.update_layout(
            title={
                'text': 'Cumulative Data Over Time',
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title='Date',
            yaxis_title='Cumulative Count',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(showgrid=True, gridcolor='gray'),
            xaxis=dict(showgrid=True, gridcolor='gray'),
            font=dict(size=14)
        )

        # 애니메이션 효과 추가
        fig.update_traces(marker=dict(size=8),
                        selector=dict(mode='markers'))

        st.plotly_chart(fig)

    # duration 에 대한 histogram
    @staticmethod
    def plot_duration_hist(duration_df):
        # Plotly 히스토그램 생성
        fig = px.histogram(
            duration_df, 
            x='duration', 
            nbins=100, 
            title="Distribution of Duration",
            color_discrete_sequence=['#636EFA']  # 기본 색상 팔레트 변경
        )
        
        # 그래프 레이아웃 수정 (단순화)
        fig.update_layout(
            title=dict(
                text="Distribution of Duration",
                font=dict(size=20, color='DarkSlateGrey'),
                x=0.5  # 중앙 정렬
            ),
            xaxis=dict(
                title=dict(text='Duration', font=dict(size=16, color='DarkSlateGrey')),
                tickfont=dict(size=12, color='DarkSlateGrey')
            ),
            yaxis=dict(
                title=dict(text='Frequency', font=dict(size=16, color='DarkSlateGrey')),
                tickfont=dict(size=12, color='DarkSlateGrey')
            ),
            plot_bgcolor='rgba(0,0,0,0)',  # 배경 투명하게 설정
            paper_bgcolor='rgba(0,0,0,0)',  # 배경 투명하게 설정
            margin=dict(l=10, r=10, t=30, b=0)  # 마진 조정
        )

        # 마커 라인 스타일 수정
        fig.update_traces(
            hoverinfo="x+y",
            marker=dict(line=dict(width=0.5, color='DarkSlateGrey'))
        )
        
        st.plotly_chart(fig)

    @staticmethod
    def plot_duration_line(duration_df):
        fig = go.Figure()

        # 히스토그램
        fig.add_trace(go.Histogram(
            x=duration_df['duration'],
            nbinsx=100,
            name='Histogram',
            marker=dict(color='blue', line=dict(color='black', width=1)),
            opacity=0.7
        ))

        # 라인 플롯
        line_data = duration_df['duration'].value_counts().sort_index()
        fig.add_trace(go.Scatter(
            x=line_data.index,
            y=line_data.values,
            mode='lines+markers',
            name='Line Plot',
            line=dict(color='red')
        ))

        # 레이아웃 설정
        fig.update_layout(
            title='Histogram and Line Plot of Duration',
            xaxis_title='Duration',
            yaxis_title='Frequency',
            yaxis2=dict(
                title='Duration',
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.1, y=0.9)
        )

        st.plotly_chart(fig)