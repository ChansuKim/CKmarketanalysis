import streamlit as st
from data_selection import Dataselect  # Assuming you have a separate module for data handling
import pandas as pd
import plotly.express as px
from datetime import datetime
import re

import plotly.graph_objects as go
from plotly.subplots import make_subplots
# from sqlalchemy.util._collections import LRUCache
def generate_table(dataframe, tablename):
    title = f"<h5>{tablename}</h5>"
    table_style = """
    <style>
        table, th, td { font-size: 12px; }
        .center { text-align: center; }
    </style>
    """
    header = "<tr>" + "".join([f"<th>{col}</th>" for col in dataframe.columns]) + "</tr>"
    rows = []
    
    # 이모지 매핑
    emoji_map = {
        0: '😡',
        1: '😟',
        2: '😐',
        3: '🙂',
        4: '😀',
        5: '😍'
    }
    
    for _, row in dataframe.iterrows():
        row_html = []
        for col, value in row.items():
            if col == 'URL':
                cell_html = f'<td><a href="{value}" target="_blank"><i class="fas fa-link"></i></a></td>'
            elif col == 'summary':
                formatted_value = re.sub(r'^-|(?!^)-', '<br>-', value).replace('<br>', '', 1)
                cell_html = f'<td title="{value}">{formatted_value}</td>'
            elif col == 'sentiment score':
                emoji = emoji_map.get(value, '')
                cell_html = f'<td class="center">{value} {emoji}</td>'
            else:
                cell_html = f'<td>{value}</td>'
            row_html.append(cell_html)
        rows.append("<tr>" + "".join(row_html) + "</tr>")
    
    return title + table_style + "<table>" + header + "".join(rows) + "</table>"





def get_maxdate(todate):
    maxdate = class_data.getmaxdate(todate,1)
    if int(todate)>=int(maxdate):
        date = maxdate


    return date


def plot_backtest_single(date,flag, termflag, term,code, title):
    df_price = class_data.getBacktest(date, flag, termflag, term, code)
    df_price['logdate'] = pd.to_datetime(df_price['logdate'], format='%Y%m%d')
    fig_d = px.line(df_price, x='logdate', y='ret', title=title)
    fig_d.update_layout(autosize=True)
    # x축의 날짜 개수를 더 많이 나오도록 설정
    fig_d.update_xaxes(
        tickformat="%Y-%m-%d",
        nticks=10  # 날짜 개수를 반 정도로 설정
    )
    st.plotly_chart(fig_d, use_container_width=True)

def plot_backtest_multiple(date, flag, termflag, term, codes):
    fig = go.Figure()
    
    for code, label in codes.items():
        df_price = class_data.getBacktest(date, flag, termflag, term, code)
        df_price['logdate'] = pd.to_datetime(df_price['logdate'], format='%Y%m%d')
        fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['ret'], mode='lines', name=label))
    
    fig.update_layout(autosize=True)
    fig.update_xaxes(tickformat="%Y-%m-%d", nticks=10)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="CK Market Wizard")    
    st.header('🌍 CK Market Wizard')
    
    add_selectbox = st.selectbox("🔍 찾고 싶은 정보를 선택하세요.", ("🌟대시보드","📈시장분석","🎭테마수익률","📊주식분석",'💹옵션분석','🔖트레이딩'))    
    date = st.date_input("📅 조회 시작일을 선택해 주세요",max_value=datetime.today())
    class_data = Dataselect(date,st.secrets["server"],st.secrets["database"],st.secrets["username"],st.secrets["password"])
    db_connection = class_data.init_db()
    todate = str(date).replace('-','')
    date = get_maxdate(todate)

    st.divider()
    # Using object notation
    with st.sidebar:
        st.header("🆕 Data Batch Status")
        
        # 데이터 처리 상태 가져오기
        dm_date_a1 = class_data.getDataProcess('a1')
        dm_date_b1 = class_data.getDataProcess('b1')
        
        # 데이터 처리 상태 출력
        st.success(f'🏠 국내데이터 {dm_date_a1} 완료')
        st.info(f'🌐 해외데이터 {dm_date_b1} 완료')
        
        # 최신 뉴스와 업데이트 입력 필드
        st.header("📰 Recently Update")
        st.markdown('''
            - 투자자예탁금, 신용공여 데이터 업데이트
            - 옵션지표 설명글 추가
            - 트레이딩 설명글 추가
            - 뉴스 요약 추가
        ''')
        
        # 연락처 섹션
        st.header("📞 Contact")
        st.write("📧 For support, contact me via email: [chansoookim@naver.com](mailto:chansoookim@naver.com)")

        # 추가적인 스타일링 요소
        st.markdown("---")
        st.write("Thank you for using our service!")
        st.markdown("""
            <style>
            .sidebar .sidebar-content {
                background-color: #f0f2f6;
                padding: 20px;
                border-radius: 10px;
            }
            .sidebar .sidebar-content h1, .sidebar .sidebar-content h2, .sidebar .sidebar-content h3 {
                color: #4CAF50;
            }
            .sidebar .sidebar-content p, .sidebar .sidebar-content li {
                font-size: 14px;
            }
            </style>
            """, unsafe_allow_html=True)
    
    
    if date and add_selectbox=="💸종베":
        st.header('📈 매수종목 분석')
        trading_list = class_data.getTradinglist(date,2)
        selected_stock = st.selectbox('🔎 종목 선택', trading_list['stockcode'])
        trading_df = class_data.gettradinginfo(date,1)
        st.dataframe(trading_df,hide_index=True)
        df = class_data.getthemestock(date, selected_stock, 2)
        df_aftermarket = class_data.getAftermarketprice(date, selected_stock, 4)

        df_all = pd.concat([df, df_aftermarket], axis=1)
        df_lastnews = class_data.getLastnews(selected_stock)
        df_gongsi = class_data.getstockgongsi(date, selected_stock)
        st.dataframe(df_all, use_container_width=True,hide_index=True)
        
        st.markdown("""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
        """, unsafe_allow_html=True)
        html_table = generate_table(df_gongsi,'종목공시')
        st.markdown(html_table, unsafe_allow_html=True)
        
    
        st.markdown("""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
        """, unsafe_allow_html=True)
        html_table = generate_table(df_lastnews,'종목뉴스')
        st.markdown(html_table, unsafe_allow_html=True)
            

        col1, col2 = st.columns(2)
        
        with col1:
            df_price = class_data.getstockprice(date, selected_stock, 'M')
            
            df_price['datetime'] =pd.to_datetime(df_price['datetime'])
            fig_m = class_data.create_candlestick_chart(df_price, 'Intraday Candestick Chart', 'date', 'price')
            # 차트를 Streamlit에 표시합니다.
            st.plotly_chart(fig_m, use_container_width=True)
        
        with col2:
            df_price = class_data.getstockprice(date, selected_stock, 'D')
            df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
            fig_d = px.line(df_price, x='logdate', y='close', labels={'price': 'Price (Daily)'}, title="Daily Price Trends")
            fig_d.update_layout(autosize=True)
            st.plotly_chart(fig_d, use_container_width=True)


        frdate = class_data.getCalendar(date,'m',6)
        col4, col5, col6 = st.columns(3) 
        df = class_data.gettradinginfo(frdate,3)
        df_st1 = df[df['strategy']=='jongbe_new'][['logdate','ret']]
        df_st1['cumret'] = (1 + df_st1['ret']).cumprod()
        df_st2 = df[df['strategy']=='jongbe_new2'][['logdate','ret']]
        df_st2['cumret'] = (1 + df_st2['ret']).cumprod()
        df_st3 = df[df['strategy']=='jongbe_new3'][['logdate','ret']]
        df_st3['cumret'] = (1 + df_st3['ret']).cumprod()
        with st.container():          
            with col4:
                # st.markdown('**strategy1**')
                df_st1['logdate'] = pd.to_datetime(df_st1['logdate'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
                fig = px.line(df_st1,x='logdate', y='cumret', labels={'cumret': 'Cumulative Return'}, title='Strategy 1 Cumulative Return')
                fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Return', xaxis=dict(tickmode='auto',nticks=10,tickformat = '%Y-%m-%d'))
                st.plotly_chart(fig, use_container_width=True)

            with col5:
                # st.markdown('**strategy2**')
                df_st2['logdate'] = pd.to_datetime(df_st2['logdate'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
                fig = px.line(df_st2,x='logdate', y='cumret', labels={'cumret': 'Cumulative Return'}, title='Strategy 2 Cumulative Return')
                fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Return', xaxis=dict(tickmode='auto',nticks=10,tickformat = '%Y-%m-%d'))
                st.plotly_chart(fig, use_container_width=True)
                
            with col6:
                # st.markdown('**strategy3**')
                df_st3['logdate'] = pd.to_datetime(df_st3['logdate'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
                fig = px.line(df_st3,x='logdate', y='cumret', labels={'cumret': 'Cumulative Return'}, title='Strategy 3 Cumulative Return')
                fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Return', xaxis=dict(tickmode='auto',nticks=10,tickformat = '%Y-%m-%d'))
                st.plotly_chart(fig, use_container_width=True)
                
    if date and add_selectbox=="🌟대시보드":
        st.header('🌟DASH BOARD')
        os_date = class_data.getmaxdate(todate,2)
        st.write('국내데이터 : ',date,' 해외 데이터 : ',os_date)
        st.divider()
        with st.container():
            # cols = responsive_columns()
            cols = st.columns(8)
            idx = 0
            markets = [
                ('KOSPI', 7, 'U001'), ('KOSDAQ', 7, 'U201'), ('S&P500', 8, 'SPX'), ('NASDAQ', 8, 'COMP'),
                ('한국 원', 9, 'FX@KRW'), ('금($/온스)', 9, 'CM@NGLD'), ('미국채권, 9, 10-Year(CBT)', 9, '99948'), ('WTI, 원유 뉴욕근월', 9, 'CM@PWTI')
            ]

            for label, flag, code in markets:
                if label in ['KOSPI', 'KOSDAQ']:
                    price, delta = class_data.getCurrentPrice(date, flag, code)
                else:
                    price, delta = class_data.getCurrentPrice(os_date, flag, code)
                
                with cols[idx % len(cols)]:
                    st.metric(label=label, value=price, delta=delta)
                idx += 1



        st.divider()
        col1, col2 = st.columns(2)
        with st.container():      
            with col1:
                st.markdown('**시장지수**')
                df = class_data.marketcondition(os_date,2)
                st.dataframe(df, use_container_width=True,hide_index=True)
            with col2:
                st.markdown('**상품**')
                df = class_data.marketcondition(os_date,3)
                st.dataframe(df , use_container_width=True,hide_index=True)
        col3, col4 = st.columns(2)
        with st.container():      
            with col3:
                st.markdown('**환율**')
                df = class_data.marketcondition(os_date,4)
                st.dataframe(df , use_container_width=True,hide_index=True)
            with col4:
                st.markdown('**채권**')
                df = class_data.marketcondition(os_date,5)
                st.dataframe(df , use_container_width=True,hide_index=True)
        col5, col6 = st.columns(2)
        with st.container():      
            with col5:
                st.markdown('**코스피 주간 Top 10**')
                df = class_data.marketcondition(date,6)
                st.dataframe(df , use_container_width=True,hide_index=True)

            with col6:
                st.markdown('**코스닥 주간 Top 10**')
                df = class_data.marketcondition(date,7)
                st.dataframe(df , use_container_width=True,hide_index=True)

        col7, col8 = st.columns(2)
        with st.container():      
            with col5:
                st.markdown('**코넥스 주간 Top 10**')
                df = class_data.marketcondition(date,9)
                st.dataframe(df , use_container_width=True,hide_index=True)

            with col6:
                st.markdown('**K-OTC 주간 Top 10**')
                df = class_data.marketcondition(date,10)
                st.dataframe(df , use_container_width=True,hide_index=True)

        col9, col10 = st.columns(2)
        with st.container():      
            with col9:
                st.markdown('**ETF 주간 Top 10**')
                df = class_data.marketcondition(date,8)
                st.dataframe(df , use_container_width=True,hide_index=True)

            with col10:
                st.markdown('**ETF 주간 Bottom 10**')
                df = class_data.marketcondition(date,13)
                st.dataframe(df , use_container_width=True,hide_index=True)


    if date and add_selectbox=="🎭테마수익률":
        st.header('📈테마수익률 현황')
        st.write('조회일 : ',date)
        term, termflag = class_data.select_term_and_flag(default_index=3)
        st.subheader('종합현황')
        col1, col2 = st.columns(2)
        with st.container():      
            with col1:
                st.markdown('**🔝 테마수익률 상위 5**')
                df_top_returns  = class_data.getThemetermreturn(date,termflag,term,'1')
                st.dataframe(df_top_returns , use_container_width=True,hide_index=True)
            with col2:
                st.markdown('**🔻 테마수익률 하위 5**')
                df_bottom_returns  = class_data.getThemetermreturn(date,termflag,term,'2')
                st.dataframe(df_bottom_returns, use_container_width=True,hide_index=True)
        col3, col4 = st.columns(2)
        with st.container():      
            with col3:
                st.markdown('**🔝 테마거래량 상위 5**')
                df_top_vol  = class_data.getThemetermreturn(date,termflag,term,'3')
                st.dataframe(df_top_vol , use_container_width=True,hide_index=True)
            with col4:
                st.markdown('**🔻 테마거래량 하위 5**')
                df_bottom_vol  = class_data.getThemetermreturn(date,termflag,term,'4')
                st.dataframe(df_bottom_vol, use_container_width=True,hide_index=True)
        col5, col6 = st.columns(2)
        with st.container():      
            with col5:
                st.markdown('**🔝 테마공매도 상위 5**')
                df_top_short  = class_data.getThemetermreturn(date,termflag,term,'5')
                st.dataframe(df_top_short , use_container_width=True,hide_index=True)
            with col6:
                st.markdown('**🔻 테마공매도 하위 5**')
                df_bottom_short  = class_data.getThemetermreturn(date,termflag,term,'6')
                st.dataframe(df_bottom_short, use_container_width=True,hide_index=True) 
        st.divider()
        st.subheader('테마수익률')
        theme_names = class_data.getthemename()
        theme_options = {f"{row['themecode']} - {row['themename']}": (row['themecode'], row['themename']) for index, row in theme_names.iterrows()}
        theme_choice = st.selectbox('🔎 테마 선택', list(theme_options.keys()))  
        selected_themecode, selected_theme = theme_options[theme_choice]
        
        if selected_themecode:
            df_theme_return = class_data.getthemereturn(date, termflag, term, selected_themecode)
            df_theme_return['logdate'] = pd.to_datetime(df_theme_return['logdate'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
            df_theme_return.set_index('logdate', inplace=True)
            st.line_chart(df_theme_return)
            df_theme_stocks = class_data.getthemestock(date, selected_themecode,1)
            st.dataframe(df_theme_stocks, use_container_width=True,hide_index=True)



    if date and add_selectbox=="📈시장분석":
        st.write('조회일 : ',date)
        st.header('📈 국내시장현황')
        tab1,tab2 = st.tabs(['Daily','Intraday'])
        # Display dataframe with better visibility

        with tab1:
            term, termflag = class_data.select_term_and_flag()
            
            col5, col6 = st.columns(2)

            with col5:
                df_price = class_data.getindexprice(date, 'u001', 'D',termflag,term)
                df_price['logdate'] =pd.to_datetime(df_price['logdate'])
                fig_m = class_data.create_candlestick_chart(df_price, 'Daily KOSPI Candestick Chart', 'date', 'price')
                st.plotly_chart(fig_m, use_container_width=True)
            with col6:
                df_price = class_data.getindexprice(date, 'u201', 'D',termflag,term)
                df_price['logdate'] =pd.to_datetime(df_price['logdate'])
                fig_m = class_data.create_candlestick_chart(df_price, 'Intraday KOSDAQ Candestick Chart', 'date', 'price')
                # 차트를 Streamlit에 표시합니다.
                st.plotly_chart(fig_m, use_container_width=True)


            col7, col8 = st.columns(2)
            with col7:
                df_kospi = class_data.getindex_fundmental(date,'KOSPI',termflag,term)
                df_kospi['logdate'] = pd.to_datetime(df_kospi['logdate'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_kospi, x='logdate', y='per', labels={'price': 'Price (Daily)'}, title="KOSPI PER")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)
                fig_d = px.line(df_kospi, x='logdate', y='pbr', labels={'price': 'Price (Daily)'}, title="KOSPI PBR")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)
            with col8:
                df_kosdaq = class_data.getindex_fundmental(date,'KOSDAQ',termflag,term)
                df_kosdaq['logdate'] = pd.to_datetime(df_kosdaq['logdate'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_kosdaq, x='logdate', y='per', labels={'price': 'Price (Daily)'}, title="KOSDAQ PER")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)  
                fig_d = px.line(df_kosdaq, x='logdate', y='pbr', labels={'price': 'Price (Daily)'}, title="KOSDAQ PBR")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True) 

            col11,col12 = st.columns(2)
            with col11:
                df_price = class_data.getindexprice_sugup(date, 'u001','D',termflag,term)
                df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_price, x='logdate', y=df_price.columns, labels={'price': 'Price (Daily)'}, title="Daily KOSPI_수급추이")
                fig_d.update_layout(autosize=True,legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
                st.plotly_chart(fig_d, use_container_width=True)
            with col12:
                df_price = class_data.getindexprice_sugup(date, 'u201','D',termflag,term)
                df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_price, x='logdate', y=df_price.columns, labels={'price': 'Price (Daily)'}, title="Daily KOSDAQ_수급추이")
                fig_d.update_layout(autosize=True,legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
                st.plotly_chart(fig_d, use_container_width=True)

            col13,col14 = st.columns(2)
            with col13:
                df_price = class_data.getmarketinfo(date,termflag,term,10)
                df_price['logdate'] = pd.to_datetime(df_price['logdate'], format='%Y%m%d')
                # 서브플롯 생성
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                                    subplot_titles=('신용거래 융자', '신용거래 대주'))
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['crdTrFingScrs'], mode='lines', name='신용거래융자 유가증권'),
                            row=1, col=1)
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['crdTrFingKosdaq'], mode='lines', name='신용거래융자 코스닥'),
                            row=1, col=1)
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['crdTrLndrScrs'], mode='lines', name='신용거래대주 유가증권'),
                            row=2, col=1)
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['crdTrLndrKosdaq'], mode='lines', name='신용거래대주 코스닥'),
                            row=2, col=1)
                fig.update_layout(title_text='신용공여잔고추이', autosize=True, height=600,legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)

                
            with col14:
                df_price = class_data.getmarketinfo(date,termflag,term,11)
                df_price['logdate'] = pd.to_datetime(df_price['logdate'], format='%Y%m%d')
                fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                                    subplot_titles=('투자자 예탁금', '미수금','반대매매','반대매매비중'))
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['invrDpsgAmt'], mode='lines', name='투자자 예탁금'),
                            row=1, col=1)
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['brkTrdUcolMny'], mode='lines', name='위탁매매 미수금'),
                            row=2, col=1)
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['brkTrdUcolMnyVsOppsTrdAmt'], mode='lines', name='미수금 대비 반대매매 금액'),
                            row=3, col=1)
                fig.add_trace(go.Scatter(x=df_price['logdate'], y=df_price['ucolMnyVsOppsTrdRlImpt'], mode='lines', name='반대매매/미수금'),
                            row=4, col=1)
                fig.update_layout(title_text='증시자금추이', autosize=True, height=600,legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                df_price = class_data.getindexprice(date, 'U001', 'M',None,None)
                df_price['datetime'] =pd.to_datetime(df_price['datetime'])
                fig_m = class_data.create_candlestick_chart(df_price, 'Intraday KOSPI Candestick Chart', 'date', 'price')
                st.plotly_chart(fig_m, use_container_width=True)
            with col2:
                df_price = class_data.getindexprice(date, 'U201', 'M',None,None)
                df_price['datetime'] =pd.to_datetime(df_price['datetime'])
                fig_m = class_data.create_candlestick_chart(df_price, 'Intraday KOSDAQ Candestick Chart', 'date', 'price')
                st.plotly_chart(fig_m, use_container_width=True)
            col3, col4 = st.columns(2)
            with col3:
                df_price = class_data.getindexprice_sugup(date, 'u001','M',None,None)
                
                df_price['datetime'] = pd.to_datetime(df_price['datetime'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_price, x='datetime', y=df_price.columns, labels={'price': 'Price (Daily)'}, title="Intraday KOSPI_sugup Trends")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)
            with col4:
                df_price = class_data.getindexprice_sugup(date, 'u201','M',None,None)
                
                df_price['datetime'] = pd.to_datetime(df_price['datetime'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_price, x='datetime', y=df_price.columns, labels={'price': 'Price (Daily)'}, title="Intraday KOSDAQ_sugup Trends")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)

    if date and add_selectbox=="📊주식분석":
        if 'chart_date' not in st.session_state:
            st.session_state['chart_date'] = date

        st.write("조건 조회일 ",date)
        col1,col2= st.columns(2)
        with col1:
            stock_conditions = class_data.getconditionlist()
            
            condition_options = {f"{row['name']}": (row['seq'], row['name']) for index, row in stock_conditions.iterrows()}
            condition_choice = st.selectbox("🔎조건 선택",list(condition_options.keys()))
        try:            
            
        
            # if stock_choice is not None:

            #     if condition_choice=='유상증자':
            #         with st.expander('공시내용', expanded=False):
            #                 st.write('''
            #                 The chart above shows some numbers I picked for you.
            #                 I rolled actual dice for these, so they're *guaranteed* to
            #                 be random.
            #             ''')
                stock_list = class_data.getstocklistbycondition(date,condition_choice)
                stockcodes = "".join([f"{code}|" for code in stock_list['stockcode']])
                stockcodes = stockcodes.rstrip('|')
                searchdate=date
                
                df = class_data.getthemestock(searchdate, stockcodes, 2)
                st.dataframe(df, use_container_width=True,hide_index=True)          
                    

                col3,col4= st.columns(2)
                with col3:
                    stock_options = {f"{row['stockcode']} - {row['stockname']}({round(row['ret']*100,2)}%)": (row['stockcode'], row['stockname']) for index, row in stock_list.iterrows()}
                    stock_choice = st.selectbox("🔎 종목 선택", list(stock_options.keys())) 
                    selected_stock, stockname = stock_options[stock_choice]
                    df_aftermarket = class_data.getAftermarketprice(searchdate, selected_stock, 4)
                with col4:
                    st.dataframe(df_aftermarket, use_container_width=True,hide_index=True)        
                    # # Create buttons for date navigation
                col111, col112,col13,col14 = st.columns(4)
                  
                try:
                    with col111:
                        if st.button('Previous Day'):
                            st.session_state['chart_date'] = class_data.getdatediff(st.session_state['chart_date'],-1)
                            
                    with col112:
                        if st.button('Next Day'):
                            st.session_state['chart_date'] =class_data.getdatediff(st.session_state['chart_date'],1)
                            
                except Exception as e:
                    st.session_state['chart_date'] = date
                    
                chartdate = st.session_state['chart_date']
                st.write('차트 조회일',chartdate)
                
                # chartdate=searchdate

                col7, col8 = st.columns(2)
                with col7:
                    df_price = class_data.getstockprice(chartdate, selected_stock, 'M')
                    
                    df_price['datetime'] =pd.to_datetime(df_price['datetime'])
                    fig_m = class_data.create_candlestick_chart(df_price, 'Intraday Candestick Chart('+str(chartdate)+')', 'date', 'price')
                    st.plotly_chart(fig_m, use_container_width=True)
                
                with col8:
                    df_price = class_data.getstockprice(chartdate, selected_stock, 'D')
                    df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
                    fig_d = px.line(df_price, x='logdate', y='close', labels={'price': 'Price (Daily)'}, title='Daily Price Trends(From a month ago to '+str(chartdate)+')')
                    fig_d.update_layout(autosize=True)
                    st.plotly_chart(fig_d, use_container_width=True)

                # st.dataframe(df_gongsi)

                df_lastnews = class_data.getLastnews(selected_stock)
                df_gongsi = class_data.getstockgongsi(date, selected_stock)
                # st.dataframe(df_all, use_container_width=True,hide_index=True)
                # col9,col10 = st.columns(2)
                # with col9:
                
                st.markdown("""
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
                """, unsafe_allow_html=True)
                html_table = generate_table(df_lastnews,'종목뉴스')
                st.markdown(html_table, unsafe_allow_html=True)
                
                st.markdown("""
                    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
                """, unsafe_allow_html=True)
                html_table = generate_table(df_gongsi,'종목공시')
                st.markdown(html_table, unsafe_allow_html=True)
                    
                # with col10:


        except Exception as e:
            st.write('해당되는 종목이 없습니다.',e)

    if date and add_selectbox=="🔖트레이딩":
        st.header('📈트레이딩 지수')
        st.write('조회일 : ',date)
        term, termflag = class_data.select_term_and_flag(options=('1일','1주','1개월','2개월','3개월','6개월','1년'))

        col1, col2 = st.columns(2)
        with col1:
            with st.expander('오버나잇 전략'):
                st.write('''
                **오버나잇 수익률 전략 설명:**
                - 코스피 및 코스닥 지수의 (시가 - 전일 종가) / 전일 종가 를 누적하는 전략입니다.
                - 오버나잇 수익률은 시장이 폐장된 후, 다음날 개장 시까지의 주가 변동을 포착하는데, 이는 장 마감 후 발생하는 뉴스나 글로벌 시장의 움직임 등에 의해 영향을 받습니다.
                - 이러한 전략은 단기적인 변동성을 이용하며, 장 마감 후 긍정적인 뉴스나 글로벌 호재에 반응하는 주가 상승을 노리는 것입니다.
                ''')

            plot_backtest_multiple(date, 1, termflag, term, {'U001': 'KOSPI 누적 오버나잇 수익률', 'U201': 'KOSDAQ 누적 오버나잇 수익률'})

        with col2:
            with st.expander('장중모멘텀'):
                st.write('''
                **장중 모멘텀 전략 설명:**
                - 장초반 30분 수익률이 상승하면 장종료 30분 전에 매수합니다.
                - 매수 후 당일 종가에 포지션을 청산합니다.
                - 이 전략은 장중 초기의 모멘텀이 하루 종가까지 지속될 가능성을 활용합니다.
                - 초기의 상승 모멘텀은 종종 지속적인 매수 압력으로 이어질 수 있습니다.
                ''')

            plot_backtest_multiple(date, 6, termflag, term, {'U001': 'KOSPI 장중 모멘텀', 'U201': 'KOSDAQ 장중 모멘텀'})
        col3, col4 = st.columns(2)
        with col3:
            with st.expander('변동성돌파'):
                st.write('''
                **Volatility Breakout 전략 설명:**
                - 당일 가격이 당일 시가 + (전일 고가 - 전일 저가) * 0.5 보다 높으면 매수 신호를 발생시킵니다.
                - 매수 후 당일 종가에 포지션을 청산합니다.
                - 이 전략은 시장의 단기적인 변동성을 이용하여 수익을 창출하는 것을 목표로 합니다.
                - 변동성이 높은 날에는 가격이 급격히 움직일 가능성이 크기 때문에 이러한 돌파 지점을 이용하여 수익을 얻을 수 있습니다.
                ''')

            plot_backtest_multiple(date, 5, termflag, term, {'U001': 'KOSPI 변동성돌파', 'U201': 'KOSDAQ 변동성돌파'})
        with col4:
            with st.expander('일중 주기성 모멘텀 전략'):
                st.write('''
                **Intraday Periodicity Momentum 전략 설명:**
                - 전일 장 마지막 20분이 상승했으면, 당일 마지막 20분에 진입, 종가 청산합니다.
                - 이 전략은 전일의 상승 모멘텀이 당일 장 마감 전에도 지속될 가능성을 이용합니다.
                - 전일 마지막 20분 동안의 상승이 다음날에도 긍정적인 심리를 유발할 수 있습니다.
                ''')

            plot_backtest_multiple(date, 7, termflag, term, {'U001': 'KOSPI 일중주기성 모멘텀', 'U201': 'KOSDAQ 일중주기성 모멘텀'})
        col5, col6 = st.columns(2)
        with col5:
            with st.expander('일중 주기성 리버설 전략'):
                st.write('''
                **Intraday Periodicity Reversal 전략 설명:**
                - 전일 장 초반 10분이 하락했으면, 당일 장시가 진입 10분에 청산합니다.
                - 이 전략은 전일 장 초반의 하락 모멘텀이 당일 장 초반의 반등으로 이어질 가능성을 이용합니다.
                - 전일 초반의 하락이 과매도로 인한 반등을 유발할 수 있습니다.
                ''')

            plot_backtest_multiple(date, 8, termflag, term, {'U001': 'KOSPI 일중주기성 리버설', 'U201': 'KOSDAQ 일중주기성 리버설'})

        with col6:
            with st.expander('월요 리버설 전략'):
                st.write('''
                **Monday Reversal 전략 설명:**
                - 월요일 오후 수익률이 0보다 작으면 매수하고, 다음 주 월요일 시가에 매도합니다.
                - 월요일 오전 손실로 인해 오후에 더 많은 위험을 감수하게 되어 주가가 하락할 수 있습니다.
                - 오전에는 주말 뉴스로 인해 과민반응이 발생하고, 오후에는 진정되어 주가가 하락할 수 있습니다.
                - 주중 나머지 기간 동안 시장이 안정화되면서 주가가 상승합니다.
                ''')

            plot_backtest_multiple(date, 9, termflag, term, {'U001': 'KOSPI 월요 리버설', 'U201': 'KOSDAQ 월요 리버설'})

    if date and add_selectbox=="💹옵션분석":
        st.write('조회일 : ',date)
        term, termflag = class_data.select_term_and_flag(default_index=2)
        st.header('📈옵션 현황')
        col5, col6 = st.columns(2)
        with col5:
            
            with st.expander('K200옵션 등가양합'):
                st.write('''
                **등가 양합 전략 설명:**
                - 양합은 행사가가 같은 콜옵션과 풋옵션의 합 중 가장 낮은 합을 말합니다.
                - 옵션 프리미엄이 높아지면 양합도 높아집니다.
                ''')
            plot_backtest_single(date, 3, termflag, term, '0', 'K200옵션등가 양합')

        with col6:

            with st.expander('등가 Put-Call 거래량 비율'):
                st.write('''
                **등가 Put-Call 거래량 비율:** 
                - 풋콜 거래량 비율(Put-Call Volume Ratio)
                - 비율 > 1: 시장 참가자들이 주로 풋 옵션을 매수하고 있음을 의미하며, 이는 시장의 하락에 대한 대비가 더 많음을 나타낼 수 있습니다.
                - 비율 < 1: 시장 참가자들이 주로 콜 옵션을 매수하고 있음을 의미하며, 이는 시장의 상승에 대한 기대가 더 많음을 나타낼 수 있습니다.
                ''')
            plot_backtest_single(date, 4, termflag, term, '0', '등가 Put-Call 거래량 비율')

                    
        option_metrics = {
            'priceclose' : 'Price',
            'nonpaid' : 'Call OpenInterest',
            'iv': 'Implied Volatility'
            # 'delta': 'Delta',
            # 'gamma': 'Gamma',
            # 'theta': 'Theta',
            # 'vega': 'Vega'
        }

        tab1,tab2 = st.tabs(['Daily','Intraday'])

        with tab1:
            

            col3,col4 = st.columns(2)
            with col3:
                df_option = class_data.getoptionprice(date,'d',0,'c',termflag,term)
                # Generate and display charts for Call options
                for metric, desc in option_metrics.items():
                    fig = class_data.create_line_chart(df_option, f'Call {desc}', 'logdate', metric)
                    st.plotly_chart(fig, use_container_width=True)

            with col4:
                df_option = class_data.getoptionprice(date,'d',0,'p',termflag,term)
                # Generate and display charts for Call options
                for metric, desc in option_metrics.items():
                    fig = class_data.create_line_chart(df_option, f'Put {desc}', 'logdate', metric)
                    st.plotly_chart(fig, use_container_width=True)

        with tab2:
            col1,col2 = st.columns(2)
            with col1:
                df_option = class_data.getoptionprice(date,'m',0,'c',None,None)
                # Generate and display charts for Call options
                for metric, desc in option_metrics.items():
                    fig = class_data.create_line_chart(df_option, f'Call {desc}', 'datetime', metric)
                    st.plotly_chart(fig, use_container_width=True)


            with col2:
                df_option = class_data.getoptionprice(date,'m',0,'p',None,None)
                # Generate and display charts for Call options
                for metric, desc in option_metrics.items():
                    fig = class_data.create_line_chart(df_option, f'Put {desc}', 'datetime', metric)
                    st.plotly_chart(fig, use_container_width=True)

