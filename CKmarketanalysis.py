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


def plot_backtest(date,flag, termflag, term,code, title):
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

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="CK Market Wizard")    
    st.header('🌍 CK Market Wizard')
    
    date = st.date_input("📅 조회 시작일을 선택해 주세요",max_value=datetime.today())
    class_data = Dataselect(date,st.secrets["server"],st.secrets["database"],st.secrets["username"],st.secrets["password"])
    db_connection = class_data.init_db()
    todate = str(date).replace('-','')
    date = get_maxdate(todate)
    # Using object notation
    with st.sidebar:
        add_selectbox = st.selectbox("🔍 찾고 싶은 정보를 선택하세요.", ("🌟대시보드","📈시장분석","🎭테마수익률","📊주식분석",'💹옵션분석','🔖트레이딩'))    
        st.header("🆕 Data Batch Status")
        
        # 데이터 처리 상태 가져오기
        dm_date_a1 = class_data.getDataProcess('a1')
        dm_date_b1 = class_data.getDataProcess('b1')
        
        # 데이터 처리 상태 출력
        st.write(f'🏠 국내데이터 {dm_date_a1} 완료')
        st.write(f'🌐 해외데이터 {dm_date_b1} 완료')
        
        # 최신 뉴스와 업데이트 입력 필드
        
        st.header("📰 업데이트 내역")
        st.markdown('''
        1. **시장분석** 
            - 투자자예탁금, 신용공여 데이터 업데이트
        2. **옵션분석**
            - 옵션지표 설명글 추가
        3. **트레이딩**
            - 트레이딩 설명글 추가
        4. **주식분석**
            - 뉴스 요약 추가
        ''')
                
        # 연락처 섹션
        st.header("📞 Contact")
        st.write("📧 For support, contact me via email: chansoookim@naver.com ")
    
    
    if date and add_selectbox=="🌟대시보드":
        st.header('🌟DASH BOARD')
        os_date = class_data.getmaxdate(todate,2)
        st.write('국내',date,'해외 : ',os_date)
        st.divider()
        with st.container():
            # cols = responsive_columns()
            cols = st.columns(8)
            idx = 0
            markets = [
                ('KOSPI',7, 'U001'), ('KOSDAQ',7, 'U201'), ('S&P500',8, 'SPX'), ('NASDAQ',8, 'COMP'),
                ('한국 원', 9,'FX@KRW'), ('금($/온스)', 9,'CM@NGLD'), ('미국채권,9,10-Year(CBT)',9, '99948'), ('WTI, 원유 뉴욕근월', 9,'CM@PWTI')
            ]
            for label,flag, code in markets:
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
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)
            with col12:
                df_price = class_data.getindexprice_sugup(date, 'u201','D',termflag,term)
                df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_price, x='logdate', y=df_price.columns, labels={'price': 'Price (Daily)'}, title="Daily KOSDAQ_수급추이")
                fig_d.update_layout(autosize=True)
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
                fig.update_layout(title_text='신용공여추이', autosize=True, height=600)
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
                fig.update_layout(title_text='증시자금추이', autosize=True, height=600)
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
            with st.expander('KOSPI누적장중수익률'):
                st.write('''
                **KOSPI 누적 장중 수익률 전략 설명:**
                - 코스피 지수의 (종가 - 시가) / 시가 를 누적하는 전략입니다.
                - 매일 장 시작 시의 시가와 장 마감 시의 종가를 비교하여 그 차이를 계산합니다.
                - 이를 시가로 나눈 후 백분율로 변환하여 일일 수익률을 구합니다.
                - 이렇게 구한 일일 수익률을 누적하여 전체 기간 동안의 수익률 변화를 추적합니다.
                ''')
            plot_backtest(date, 2, termflag, term, 'U001', 'KOSPI 누적 장중 수익률')

        with col2:

            with st.expander('KOSPI누적오버나잇수익률'):
                st.write('''
                **KOSPI 누적 오버나잇 수익률 전략 설명:**
                - 코스피 지수의 (시가 - 전일 종가) / 전일 종가 를 누적하는 전략입니다.
                - 매일 장 시작 시의 시가와 전일 장 마감 시의 종가를 비교하여 그 차이를 계산합니다.
                - 이를 전일 종가로 나눈 후 백분율로 변환하여 일일 수익률을 구합니다.
                - 이렇게 구한 일일 수익률을 누적하여 전체 기간 동안의 수익률 변화를 추적합니다.
                ''')
            plot_backtest(date, 1, termflag, term, 'U001', 'KOSPI 누적 오버나잇 수익률')

        col3, col4 = st.columns(2)
        with col3:

            with st.expander('KOSDAQ누적장중수익률'):
                st.write('''
                **KOSDAQ 누적 장중 수익률 전략 설명:**
                - 코스닥 지수의 (종가 - 시가) / 시가 를 누적하는 전략입니다.
                - 매일 장 시작 시의 시가와 장 마감 시의 종가를 비교하여 그 차이를 계산합니다.
                - 이를 시가로 나눈 후 백분율로 변환하여 일일 수익률을 구합니다.
                - 이렇게 구한 일일 수익률을 누적하여 전체 기간 동안의 수익률 변화를 추적합니다.
                ''')
            plot_backtest(date, 2, termflag, term, 'U201', 'KOSDAQ 누적 장중 수익률')
        with col4:

            with st.expander('KOSDAQ누적오버나잇수익률'):
                st.write('''
                **KOSDAQ 누적 오버나잇 수익률 전략 설명:**
                - 코스닥 지수의 (시가 - 전일 종가) / 전일 종가 를 누적하는 전략입니다.
                - 매일 장 시작 시의 시가와 전일 장 마감 시의 종가를 비교하여 그 차이를 계산합니다.
                - 이를 전일 종가로 나눈 후 백분율로 변환하여 일일 수익률을 구합니다.
                - 이렇게 구한 일일 수익률을 누적하여 전체 기간 동안의 수익률 변화를 추적합니다.
                ''')
            plot_backtest(date, 1, termflag, term, 'U201', 'KOSDAQ 누적 오버나잇 수익률')


        col5, col6 = st.columns(2)
        with col5:

            with st.expander('코스피 변동성돌파'):
                st.write('''
                **KOSPI Volatility Breakout 전략 설명:**
                - 코스피 지수의 변동성 돌파 전략입니다.
                - 당일 가격이 당일 시가 + (전일 고가 - 전일 저가) * 0.5 보다 높으면 매수 신호를 발생시킵니다.
                - 매수 후 당일 종가에 포지션을 청산합니다.
                ''')
            plot_backtest(date, 5, termflag, term, 'U001', 'KOSPI Volatility Breakout')
        with col6:

            with st.expander('코스닥 변동성돌파'):
                st.write('''
                **KOSDAQ Volatility Breakout 전략 설명:**
                - 코스닥 지수의 변동성 돌파 전략입니다.
                - 당일 가격이 당일 시가 + (전일 고가 - 전일 저가) * 0.5 보다 높으면 매수 신호를 발생시킵니다.
                - 매수 후 당일 종가에 포지션을 청산합니다.
                ''')
            plot_backtest(date, 5, termflag, term, 'U201', 'KOSDAQ Volatility Breakout')

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
            plot_backtest(date, 3, termflag, term, '0', 'K200옵션등가 양합')

        with col6:

            with st.expander('등가 Put-Call 거래량 비율'):
                st.write('''
                **등가 Put-Call 거래량 비율:** 
                - 풋콜 거래량 비율(Put-Call Volume Ratio)
                - 비율 > 1: 시장 참가자들이 주로 풋 옵션을 매수하고 있음을 의미하며, 이는 시장의 하락에 대한 대비가 더 많음을 나타낼 수 있습니다.
                - 비율 < 1: 시장 참가자들이 주로 콜 옵션을 매수하고 있음을 의미하며, 이는 시장의 상승에 대한 기대가 더 많음을 나타낼 수 있습니다.
                ''')
            plot_backtest(date, 4, termflag, term, '0', '등가 Put-Call 거래량 비율')

                    
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

