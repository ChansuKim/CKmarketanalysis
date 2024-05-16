import streamlit as st
from data_selection import Dataselect  # Assuming you have a separate module for data handling
import pandas as pd
import plotly.express as px
from datetime import datetime
# from sqlalchemy.util._collections import LRUCache


def generate_table(dataframe):
    # 테이블에 스타일 추가 (글자 크기를 12px로 설정)
    header = "<tr>" + "".join([f"<th style='font-size: 12px;'>{col}</th>" for col in dataframe.columns]) + "</tr>"
    rows = []
    for _, row in dataframe.iterrows():
        rows.append("<tr>" + "".join([
            f'<td style="font-size: 12px;"><a href="{row["URL"]}" target="_blank"><i class="fas fa-link"></i></a></td>' if col == 'URL' else f'<td style="font-size: 12px;">{value}</td>' 
            for col, value in row.items()]) + "</tr>")
    return "<table>" + header + "".join(rows) + "</table>"



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
    print(df_price)
    # x축의 날짜 개수를 더 많이 나오도록 설정
    fig_d.update_xaxes(
        tickformat="%Y-%m-%d",
        nticks=10  # 날짜 개수를 반 정도로 설정
    )
    st.plotly_chart(fig_d, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="CK Market wizard")    
    st.header('🌍 CK Market wizard')
    
    date = st.date_input("📅 조회 시작일을 선택해 주세요",max_value=datetime.today())
    class_data = Dataselect(date,st.secrets["server"],st.secrets["database"],st.secrets["username"],st.secrets["password"])
    db_connection = class_data.init_db()
    todate = str(date).replace('-','')
    date = get_maxdate(todate)
    # Using object notation
    add_selectbox = st.sidebar.selectbox("🔍 찾고 싶은 정보를 선택하세요.", ("🌟대시보드","📈시장지수","🎭테마수익률","📊주식분석",'💹옵션분석','🔖트레이딩'))


                
    if date and add_selectbox=="🌟대시보드":
        st.subheader('🌟DASH BOARD')
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
        st.subheader('📈테마수익률 현황')
        st.write('조회일 : ',date)
        term, termflag = class_data.select_term_and_flag(default_index=0)
        tab1,tab2 = st.tabs(['종합현황','테마수익률'])

        with tab1:
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
        with tab2:
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



    if date and add_selectbox=="📈시장지수":
        st.write('조회일 : ',date)
        st.subheader('📈 시장지수 분석')
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
                fig_d = px.line(df_price, x='logdate', y=df_price.columns, labels={'price': 'Price (Daily)'}, title="Daily KOSPI_sugup Trends")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)
            with col12:
                df_price = class_data.getindexprice_sugup(date, 'u201','D',termflag,term)
                df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
                fig_d = px.line(df_price, x='logdate', y=df_price.columns, labels={'price': 'Price (Daily)'}, title="Daily KOSDAQ_sugup Trends")
                fig_d.update_layout(autosize=True)
                st.plotly_chart(fig_d, use_container_width=True)

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
            
        
            with col2:
                stock_list = class_data.getstocklistbycondition(date,condition_choice)
                stock_options = {f"{row['stockcode']} - {row['stockname']}({round(row['ret']*100,2)}%)": (row['stockcode'], row['stockname']) for index, row in stock_list.iterrows()}
                stock_choice = st.selectbox("🔎 종목 선택", list(stock_options.keys())) 
            
            if stock_choice is not None:

                if condition_choice=='유상증자':
                    with st.expander('공시내용', expanded=False):
                            st.write('''
                            The chart above shows some numbers I picked for you.
                            I rolled actual dice for these, so they're *guaranteed* to
                            be random.
                        ''')


                searchdate=date
                selected_stock, stockname = stock_options[stock_choice]
                df = class_data.getthemestock(searchdate, selected_stock, 2)
                df_aftermarket = class_data.getAftermarketprice(searchdate, selected_stock, 4)
                df_all = pd.concat([df, df_aftermarket], axis=1)
                # df_gongsi = class_data.getstockgongsi(date, selected_stock)
                st.dataframe(df_all, use_container_width=True,hide_index=True)          
                
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
                col9,col10 = st.columns(2)
                with col9:
                    st.markdown("""
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
                    """, unsafe_allow_html=True)
                    html_table = generate_table(df_gongsi)
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                with col10:
                    st.markdown("""
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
                    """, unsafe_allow_html=True)
                    html_table = generate_table(df_lastnews)
                    st.markdown(html_table, unsafe_allow_html=True)

        except Exception as e:
            st.write('해당되는 종목이 없습니다.',e)

    if date and add_selectbox=="🔖트레이딩":
        st.subheader('📈트레이딩 지수')
        st.write('조회일 : ',date)
        term, termflag = class_data.select_term_and_flag(options=('1일','1주','1개월','2개월','3개월','6개월','1년'))
    
        col1, col2 = st.columns(2)

        with col1:
            plot_backtest(date,2,termflag, term, 'U001', 'KOSPI Intraday Return')
            with st.expander('전략상세'):
                st.write('코스피지수의 (종가-시가)/시가 를 누적한 전략')
        with col2:
            plot_backtest(date,1, termflag, term,'U001', 'KOSPI Overnight Return')
            with st.expander('전략상세'):
                st.write('코스피지수의 (시가-전일종가)/전일종가 를 누적한 전략')
        col3, col4 = st.columns(2)
        with col3:
            plot_backtest(date,2,termflag, term, 'U201', 'KOSDAQ Intraday Return')
            with st.expander('전략상세'):
                st.write('코스닥지수의(종가-시가)/시가 를 누적한 전략')
        with col4:
            plot_backtest(date,1,termflag, term, 'U201', 'KOSDAQ Overnight Return')
            with st.expander('전략상세'):
                st.write('코스피지수의 (시가-전일종가)/전일종가 를 누적한 전략')

        # col5, col6 = st.columns(2)
        # with col5:
        #     plot_backtest(date,3, termflag, term,'0', 'Option Daily straddle')

        col7, col8 = st.columns(2)
        with col7:
            plot_backtest(date,4, termflag, term,'U001', 'KOSPI Volatility Breakout')
            with st.expander('전략상세'):
                st.write('코스피지수의 변동성돌파, if price>priceopen + (prehigh-prelow)*0.5 then buy, exit on close')
        with col8:
            plot_backtest(date,4, termflag, term,'U201', 'KOSDAQ Volatility Breakout')
            with st.expander('전략상세'):
                st.write('코스닥지수의 변동성돌파, if price>priceopen + (prehigh-prelow)*0.5 then buy, exit on close')
    if date and add_selectbox=="💹옵션분석":
        st.write('조회일 : ',date)
        st.subheader('📈옵션 현황')
                    
        option_metrics = {
            'priceclose' : 'Price',
            'nonpaid' : 'Call OpenInterest',
            'iv': 'Implied Volatility',
            'delta': 'Delta',
            'gamma': 'Gamma',
            'theta': 'Theta',
            'vega': 'Vega'
        }

        tab1,tab2 = st.tabs(['Daily','Intraday'])

        with tab1:
            term, termflag = class_data.select_term_and_flag(default_index=2)

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

    #사이드바 추가 기능
    with st.sidebar:
        st.subheader("📰 Market Insights")
        st.text_area("🆕 최신 뉴스와 업데이트", height=100)
        st.subheader("Contact")
        st.write("For support, contact me via email: chansoookim@naver.com ")

