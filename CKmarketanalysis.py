import streamlit as st
from data_selection import Dataselect  # Assuming you have a separate module for data handling
import pandas as pd
import plotly.express as px
from datetime import datetime


def generate_table(dataframe):
    header = "<tr>" + "".join([f"<th>{col}</th>" for col in dataframe.columns]) + "</tr>"
    rows = []
    for _, row in dataframe.iterrows():
        rows.append("<tr>" + "".join([
            f'<td><a href="{row["URL"]}" target="_blank"><i class="fas fa-link"></i></a></td>' if col == 'URL' else f"<td>{value}</td>" 
            for col, value in row.items()]) + "</tr>")
    return "<table>" + header + "".join(rows) + "</table>"

def get_maxdate(todate):
    maxdate = class_data.getmaxdate(todate,1)
    if int(todate)>=int(maxdate):
        date = maxdate
    return date

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="CK Market wizard")    
    st.header('🌍 CK Market wizard')
    
    date = st.date_input("📅 조회 시작일을 선택해 주세요",max_value=datetime.today())
    # @st.cache_resource
    class_data = Dataselect(date,st.secrets["server"],st.secrets["database"],st.secrets["username"],st.secrets["password"])
    db_connection = class_data.init_db()
    todate = str(date).replace('-','')
    date = get_maxdate(todate)
    # Using object notation
    add_selectbox = st.sidebar.selectbox("🔍 찾고 싶은 정보를 선택하세요.", ("🌟대시보드","📈시장지수","🎭테마수익률","📊주식분석",'🔖관심종목','💹옵션분석'))


    if date and add_selectbox=="🌟대시보드":
        st.subheader('🌟DASH BOARD')
        st.write('조회일 : ',date)
        
        with st.container():
            col11, col12, col13, col14 = st.columns(4)
            with col11:
                price,delta = class_data.getCurrentPrice(date,7,'U001')
                st.metric(label="KOSPI", value=price, delta=delta)
            with col12:
                price,delta = class_data.getCurrentPrice(date,7,'U201')
                st.metric(label="KOSDAQ", value=price, delta=delta)
            with col13:
                price,delta = class_data.getCurrentPrice(date,8,'SPX')
                st.metric(label="S&P500", value=price, delta=delta)
            with col14:
                price,delta = class_data.getCurrentPrice(date,8,'COMP')
                st.metric(label="NASDAQ", value=price, delta=delta)
            col15, col16, col17, col18 = st.columns(4)
            with col15:
                price,delta = class_data.getCurrentPrice(date,9,'FX@KRW')
                st.metric(label="한국 원", value=price, delta=delta)
            with col16:
                price,delta = class_data.getCurrentPrice(date,9,'CM@NGLD')
                st.metric(label="금($/온스)", value=price, delta=delta)
            with col17:
                price,delta = class_data.getCurrentPrice(date,9,'99948')
                st.metric(label="미국채권,10-Year(CBT)", value=price, delta=delta)
            with col18:
                price,delta = class_data.getCurrentPrice(date,9,'CM@PWTI')
                st.metric(label="WTI, 원유 뉴욕근월", value=price, delta=delta)


        st.write('')
        col1, col2 = st.columns(2)
        with st.container():      
            with col1:
                st.markdown('**시장지수**')
                df = class_data.marketcondition(date,2)
                st.dataframe(df, use_container_width=True)
            with col2:
                st.markdown('**상품**')
                df = class_data.marketcondition(date,3)
                st.dataframe(df , use_container_width=True)
        col3, col4 = st.columns(2)
        with st.container():      
            with col3:
                st.markdown('**환율**')
                df = class_data.marketcondition(date,4)
                st.dataframe(df , use_container_width=True)
            with col4:
                st.markdown('**채권**')
                df = class_data.marketcondition(date,5)
                st.dataframe(df , use_container_width=True)
        col5, col6 = st.columns(2)
        with st.container():      
            with col5:
                st.markdown('**코스피 주간 Top 10**')
                df = class_data.marketcondition(date,6)
                st.dataframe(df , use_container_width=True)

            with col6:
                st.markdown('**코스닥 주간 top 10**')
                df = class_data.marketcondition(date,7)
                st.dataframe(df , use_container_width=True)

        col7, col8 = st.columns(2)
        with st.container():      
            with col5:
                st.markdown('**코넥스 주간 Top 10**')
                df = class_data.marketcondition(date,9)
                st.dataframe(df , use_container_width=True)

            with col6:
                st.markdown('**K-OTC 주간 Top 10**')
                df = class_data.marketcondition(date,10)
                st.dataframe(df , use_container_width=True)

        col9, col10 = st.columns(2)
        with st.container():      
            with col9:
                st.markdown('**ETF 주간 Top 10**')
                df = class_data.marketcondition(date,8)
                st.dataframe(df , use_container_width=True)

            with col10:
                st.markdown('**ETF 주간 Bottom 10**')
                df = class_data.marketcondition(date,13)
                st.dataframe(df , use_container_width=True)


    if date and add_selectbox=="🎭테마수익률":
        st.subheader('📈테마수익률 현황')
        st.write('조회일 : ',date)
        term, termflag = class_data.select_term_and_flag()
        tab1,tab2 = st.tabs(['종합현황','테마수익률'])

        with tab1:
            col1, col2 = st.columns(2)
            with st.container():      
                with col1:
                    st.markdown('**🔝 테마수익률 상위 5**')
                    df_top_returns  = class_data.getThemetermreturn(date,termflag,term,'1')
                    st.dataframe(df_top_returns , use_container_width=True)
                with col2:
                    st.markdown('**🔻 테마수익률 하위 5**')
                    df_bottom_returns  = class_data.getThemetermreturn(date,termflag,term,'2')
                    st.dataframe(df_bottom_returns, use_container_width=True)
            col3, col4 = st.columns(2)
            with st.container():      
                with col3:
                    st.markdown('**🔝 테마거래량 상위 5**')
                    df_top_vol  = class_data.getThemetermreturn(date,termflag,term,'3')
                    st.dataframe(df_top_vol , use_container_width=True)
                with col4:
                    st.markdown('**🔻 테마거래량 하위 5**')
                    df_bottom_vol  = class_data.getThemetermreturn(date,termflag,term,'4')
                    st.dataframe(df_bottom_vol, use_container_width=True)
            col5, col6 = st.columns(2)
            with st.container():      
                with col5:
                    st.markdown('**🔝 테마공매도 상위 5**')
                    df_top_short  = class_data.getThemetermreturn(date,termflag,term,'5')
                    st.dataframe(df_top_short , use_container_width=True)
                with col6:
                    st.markdown('**🔻 테마공매도 하위 5**')
                    df_bottom_short  = class_data.getThemetermreturn(date,termflag,term,'6')
                    st.dataframe(df_bottom_short, use_container_width=True) 
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
                st.dataframe(df_theme_stocks, use_container_width=True)



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
        st.write('조회일 : ',date)
        stock_list = class_data.getstockmater(date)
        stock_options = {f"{row['stockcode']} - {row['stockname']}": (row['stockcode'], row['stockname']) for index, row in stock_list.iterrows()}
        stock_choice = st.selectbox("🔎 종목 선택", list(stock_options.keys()))  

        selected_stock, stockname = stock_options[stock_choice]
        df = class_data.getthemestock(date, selected_stock, 2)
        df_aftermarket = class_data.getAftermarketprice(date, selected_stock, 4)

        df_gongsi = class_data.getstockgongsi(date, selected_stock)
        st.dataframe(df, use_container_width=True)
        st.dataframe(df_aftermarket)

        col7, col8 = st.columns(2)
        
        with col7:
            df_price = class_data.getstockprice(date, selected_stock, 'M')
            
            df_price['datetime'] =pd.to_datetime(df_price['datetime'])
            fig_m = class_data.create_candlestick_chart(df_price, 'Intraday Candestick Chart', 'date', 'price')
            st.plotly_chart(fig_m, use_container_width=True)
        
        with col8:
            df_price = class_data.getstockprice(date, selected_stock, 'D')
            df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
            fig_d = px.line(df_price, x='logdate', y='close', labels={'price': 'Price (Daily)'}, title="Daily Price Trends")
            fig_d.update_layout(autosize=True)
            st.plotly_chart(fig_d, use_container_width=True)

        # st.dataframe(df_gongsi)

        st.markdown("""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
        """, unsafe_allow_html=True)
        html_table = generate_table(df_gongsi)
        st.markdown(html_table, unsafe_allow_html=True)

    if date and add_selectbox=="🔖관심종목":
        st.write('조회일 : ',date)
        st.title('관심종목 Tracker')
        
        interested_stock_list = class_data.getinterestedstocklist(date)
        interestname = st.selectbox('🔎 종목 선택', interested_stock_list['interestname'])
        df_theme_stocks = class_data.getthemestock(date, interestname,3)
        # st.dataframe(df_theme_stocks.style.applymap(lambda x: 'background-color : yellow' if x > 0 else ''), use_container_width=True)
        st.dataframe(df_theme_stocks, use_container_width=True)

        
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
        st.write("For support, contact us via email: ")

        # my_bar = st.progress(0)
        # for percent_complete in range(100):
        #     time.sleep(0.1)
        #     my_bar.progress(percent_complete + 1)

        
    # with st.sidebar:
    #     st.subheader("Navigation")
    #     page = st.radio("Go to", ["Home", "Market Analysis", "Stock Insights", "Options", "About"])

    #     st.subheader("Settings")
    #     st.checkbox("Enable Advanced Features")

    #     st.subheader("Contact")
    #     st.write("For support, contact us via email: support@ckmarketwizard.com.")
