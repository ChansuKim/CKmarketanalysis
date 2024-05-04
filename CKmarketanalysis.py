import streamlit as st
import datetime
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

showErrorDetails = False


class Dataselect():
    def __init__(self, date,server, database, user_id, password):
        self.server = server
        self.database = database
        self.user_id = user_id
        self.password = password
        self.date = date
        
    
    # @st.cache_resource
    def init_db(self):
        connection_string = f"mssql+pyodbc://{self.user_id}:{self.password}@{self.server}/{self.database}?driver=SQL+Server"
        engine = create_engine(connection_string, echo=False)
        try:
            self.db_init = engine.connect()
            return self.db_init
        except Exception as e:
            st.error(f"Failed to connect to database: {e}")
            return None


    def getCalendar(self, date, termflag, term):
        todate = int(str(date).replace('-', ''))
        sql = '''
            EXEC stock.[dbo].[SL_GetInformation] ?,?,?,?
            '''
        params = (todate,2, termflag, term)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        frdate = int(df['frdate'][0])
        return frdate 

    def getstockprice(self,date,code,frame):
        todate = int(str(date).replace('-',''))
        if frame=='D':
            frdate = self.getCalendar(todate,'m','1')
            sql ="EXEC stock.[dbo].[SL_Getstockreturn] ?,?,?,?"
            params = (frdate,'', code, int(5))
            df = pd.read_sql(sql, con=self.db_init, params=params)
        else:
            sql ="EXEC stock.[dbo].[SL_Getstockreturn] ?,?,?,?"
            params = ('',todate, code, int(6))
            df = pd.read_sql(sql, con=self.db_init,params=params)
            df['logtime'] =df['logtime'].apply(lambda x: '0'+str(x) if len(str(x))==3 else x)
            df['logtime'] =df['logtime'].apply(lambda x: str(x)[:2]+':'+str(x)[-2:])
            cols = ['logdate', 'logtime']
            df['datetime'] =df[cols].apply(lambda row: ' '.join(row.values.astype(str))+':00', axis=1)
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)
        return df
    
    def getoptionprice(self,date,frame,otm,cpflag,termflag,term):
        todate = int(str(date).replace('-',''))
        if frame=='d':
            frdate = self.getCalendar(todate,termflag,term)
            sql= '''
            EXEC stock.[dbo].[SL_GetOption] {},{},{},{},{}
            '''.format(frdate,todate,'D',otm,cpflag)            
            df = pd.read_sql(sql, con=self.db_init)
            df['logdate'] =pd.to_datetime(df['logdate'])
            
        else:
            sql = '''
            EXEC stock.[dbo].[SL_GetOption] {},{},{},{},{}
            '''.format(todate,todate,'m',otm,cpflag)
            df = pd.read_sql(sql, con=self.db_init)
            df['logtime'] =df['logtime'].apply(lambda x: '0'+str(x) if len(str(x))==3 else x)
            df['logtime'] =df['logtime'].apply(lambda x: str(x)[:2]+':'+str(x)[-2:])
            cols = ['logdate', 'logtime']
            df['datetime'] =df[cols].apply(lambda row: ' '.join(row.values.astype(str))+':00', axis=1)
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)
            df['datetime'] =pd.to_datetime(df['datetime'])
        return df
    
    def getstockmater(self,date):
        todate = int(str(date).replace('-',''))
        sql = '''
            EXEC stock.[dbo].[SL_GetInformation] ?,?,?,?
            '''
        params = (todate,1,'','')
        df = pd.read_sql(sql, con=self.db_init,params=params)
        return df[['stockcode','stockname']]
    
    def getinterestedstocklist(self):
        sql = '''
            EXEC stock.[dbo].[SL_GetInformation] ?,?,?,?
            '''
        params = (todate,3,'','')
        df = pd.read_sql(sql, con=self.db_init,params=params)
        return df
    
    def insert_interested_stock(self,interestname,stock_code, stock_name):
        if self.db_init is None:
            st.error("Database connection is not established.")
            return
        try:
            # Create a SQL statement
            sql_statement = text("INSERT INTO stock.dbo.tc_InterestedStocks (stockcode, stockname,ipuser,ipdate) VALUES (:interestname ,:code, :name,:ipuser,:ipdate)")
            
            # Execute the SQL statement with parameters
            self.db_init.execute(sql_statement, {"interestname": interestname,"code": stock_code, "name": stock_name, "ipuser": 'stock_server', "ipdate": datetime.now()})
            # Since SQLAlchemy handles connection pooling, commit isn't usually required for each insert,
            # but we'll ensure it's committed in case of using raw connections.
            self.db_init.commit()
            st.success(f"{stock_name} added to interested stocks successfully!")
        except Exception as e:
            st.error(f"Error when inserting stock: {e}")

    def getindexprice(self,date,code,frame,termflag,term):
        todate = int(str(date).replace('-',''))
        if frame=='D':
            frdate = self.getCalendar(todate,termflag,term)
            sql ="EXEC stock.[dbo].[SL_GetIndexreturn] ?,?,?"
            params = (frdate, code, 1)
            df = pd.read_sql(sql, con=self.db_init, params=params)
        else:
            sql ="EXEC stock.[dbo].[SL_GetIndexreturn] ?,?,?"
            params = (todate, code, 2)
            df = pd.read_sql(sql, con=self.db_init,params=params)
            df['logtime'] =df['logtime'].apply(lambda x: '0'+str(x) if len(str(x))==3 else x)
            df['logtime'] =df['logtime'].apply(lambda x: str(x)[:2]+':'+str(x)[-2:])
            cols = ['logdate', 'logtime']
            df['datetime'] =df[cols].apply(lambda row: ' '.join(row.values.astype(str))+':00', axis=1)
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)
        return df
 
    def getindexprice_sugup(self,date,code,frame,termflag,term):
               
        todate = str(date).replace('-','')
        if frame=='D':
            frdate = self.getCalendar(todate,termflag,term)
            sql ="EXEC stock.[dbo].[SL_GetIndexreturn] ?,?,?"
            params = (frdate, code, 3)
            df = pd.read_sql(sql, con=self.db_init, params=params)
        else:
            sql ="EXEC stock.[dbo].[SL_GetIndexreturn] ?,?,?"
            params = (todate, code, 4)
            df = pd.read_sql(sql, con=self.db_init, params=params)
            df['logtime'] =df['logtime'].apply(lambda x: '0'+str(x) if len(str(x))==3 else x)
            df['logtime'] =df['logtime'].apply(lambda x: str(x)[:2]+':'+str(x)[-2:])
            cols = ['logdate', 'logtime']
            df['datetime'] =df[cols].apply(lambda row: ' '.join(row.values.astype(str))+':00', axis=1)
            df.drop(['logdate', 'logtime','stockcode'], axis=1, inplace=True)       
        return df

    def getindex_fundmental(self,date,code):      
        todate = str(date).replace('-','')
        frdate = self.getCalendar(todate,termflag,term)
        sql ="EXEC stock.[dbo].[SL_GetIndexreturn] ?,?,?"
        params = (frdate, code, 5)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df

    def getthemename(self):
        sql = '''
            EXEC stock.[dbo].[SL_GetInformation] ?,?,?,?
            '''
        params = ('',4,'','')
        df = pd.read_sql(sql, con=self.db_init,params=params)
        return df[['themecode','themename']]
    


    def getthemereturn(self,date,termflag,term,options):
        todate = str(date).replace('-','')
        frdate = self.getCalendar(todate,termflag,term)
        
        #multi일때 이거 쓰면 됨 
        # if len(option)>1:
        #     options_formatted = ','.join(f"'{x}'" for x in options)
        # else:
        # options_formatted= "{}".format(options)
        
        sql ="EXEC stock.[dbo].[SL_Getstockreturn] ?,?,?,?"
        params = (frdate,todate,options ,7)
        df = pd.read_sql(sql, con=self.db_init,params=params)

        return df



    def getmaxdate(self,date,flag):
        todate = str(date).replace('-','')
        if flag==1: 
            sql = '''
                EXEC stock.[dbo].[SL_GetInformation] ?,?,?,?
                '''
            params = (todate,5, '', '')
            
        elif flag==2:
            sql = '''
                EXEC stock.[dbo].[SL_GetInformation] ?,?,?,?
                '''
            params = (todate,6, '', '')
        
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return str(df['date'][0]).replace('-','')
    
    def gettradinginfo(self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC stock.[dbo].[SL_GetTradinginfo] ?,?
        '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df

    
    def getAftermarketprice(self,date,options,flag):
        todate = str(date).replace('-','')
        sql ="EXEC stock.[dbo].[SL_Getstockreturn] ?,?,?,?"
        params = ('',todate,options ,4)
        df = pd.read_sql(sql, con=self.db_init,params=params)
        df.columns=['시간외 표준편차','시간외 거래대금','시간외 수익률']
        return df


    def getthemestock(self,date,options,flag):
        todate = int(str(date).replace('-',''))
        sql = '''
        EXEC stock.[dbo].[SL_Getstockreturn] ?,?,?,?
        '''
        params = ('',todate,options,flag)
        df = pd.read_sql(sql, con=self.db_init,params=params)
        percent_columns = ['changeRate', '1w', '2w', '1m', '2m', '3m', '6m', '12m', '24m']
        for col in percent_columns:
            df[col]=round(df[col].astype(float)*100,2)
        columns_to_format = ['PRICECLOSE', 'foreigner', 'individual', 'institute', 'shortamt']
        for column in columns_to_format:
            try:
                df[column] = df[column].map('{:,.0f}'.format)
            except Exception:
                continue  # 형식 변환 중 오류가 발생하면 해당 열은 변경하지 않고 계속 진행
        # 컬럼명 변경
        df.columns = [
            '종목코드', '종목명', '종가', '시가총액(조)', 'PER', 'PBR', '변동률',
            '1주', '2주', '1개월', '2개월', '3개월', '6개월', '12개월', '24개월',
            '외국인', '개인', '기관', '공매도량']
        return df

    def getThemetermreturn(self,date,termflag,term,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC stock.[dbo].[SL_GetThemereturn] ?,?,?,?

        '''
        params = (todate,termflag,term,flag)
        df = pd.read_sql(sql, con=self.db_init,params=params)
        df['termret']=round(df['termret'].astype(float)*100,2)
        df['avgamount'] = df['avgamount'].map('{:,.0f}'.format)
        df['avgshortamount'] = df['avgshortamount'].map('{:,.0f}'.format)
        # 컬럼명 변경
        df.columns = ['테마명', '수익률(%)', '평균 거래대금', '평균 공매도 거래대금']
        return df

    
    def getTradinglist(self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC stock.[dbo].[SL_GetTradinginfo] ?,?
        '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df
    
    

st.set_page_config(layout="wide", page_title="CK System trading")

st.header('🌍 CK System trading')



date = st.date_input("📅 조회 시작일을 선택해 주세요")
class_data = Dataselect(date,st.secrets["server"],st.secrets["database"],st.secrets["username"],st.secrets["password"])

db_connection = class_data.init_db()
todate = str(date).replace('-','')




# Using object notation
add_selectbox = st.sidebar.selectbox("🔍 찾고 싶은 정보를 선택하세요.", ("시장지수","테마","주식",'관심종목','옵션'))


if date and add_selectbox=="테마":
    
    maxdate = class_data.getmaxdate(todate,1)

    if int(todate)>=int(maxdate):
        date = maxdate


    st.subheader('📈테마수익률 현황')

    termoption = st.selectbox(
    '기간선택',
    ('1일','1주','1개월','2개월','3개월','6개월'),5)
    if termoption.endswith('주'):
        term = int(termoption.split('주')[0])
        termflag = 'w'
    elif termoption.endswith('개월'):
        term = int(termoption.split('개월')[0])
        termflag = 'm'
    elif termoption.endswith('년'):
        term = int(termoption.split('년')[0])*12
        termflag = 'm'
    elif termoption.endswith('일'):
        term = int(termoption.split('일')[0])
        termflag = 'd'
    
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
            st.checkbox("📏 Use container width", value=False, key="use_container_width")
            df_theme_stocks = class_data.getthemestock(date, selected_themecode,1)
            st.dataframe(df_theme_stocks, use_container_width=st.session_state.use_container_width)



if date and add_selectbox=="시장지수":
    maxdate = class_data.getmaxdate(todate,1)

    if int(todate)>=int(maxdate):
        date = maxdate
    st.subheader('📈 시장지수 분석')

    
    tab1,tab2 = st.tabs(['Intraday','Daily'])
    # Display dataframe with better visibility
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            df_price = class_data.getindexprice(date, 'U001', 'M',None,None)
            df_price['datetime'] =pd.to_datetime(df_price['datetime'])

            # 캔들스틱 차트를 생성합니다.
            fig_m = go.Figure(data=[go.Candlestick(
                x=df_price['datetime'],
                open=df_price['open'],  # 여기서 'open'은 개장 가격을 의미합니다.
                high=df_price['high'],  # 'high'는 최고 가격을 의미합니다.
                low=df_price['low'],    # 'low'는 최저 가격을 의미합니다.
                close=df_price['close'],  # 'close'는 종가를 의미합니다.
                increasing_line_color='red', decreasing_line_color='green'
            )])

            # 차트 레이아웃을 업데이트합니다.
            fig_m.update_layout(
                title='Intraday KOSPI Candestick Chart',
                xaxis_title='date',
                yaxis_title='price',
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )

            # 차트를 Streamlit에 표시합니다.
            st.plotly_chart(fig_m, use_container_width=True)
        with col2:
            df_price = class_data.getindexprice(date, 'U201', 'M',None,None)
            df_price['datetime'] =pd.to_datetime(df_price['datetime'])

            # 캔들스틱 차트를 생성합니다.
            fig_m = go.Figure(data=[go.Candlestick(
                x=df_price['datetime'],
                open=df_price['open'],  # 여기서 'open'은 개장 가격을 의미합니다.
                high=df_price['high'],  # 'high'는 최고 가격을 의미합니다.
                low=df_price['low'],    # 'low'는 최저 가격을 의미합니다.
                close=df_price['close'],  # 'close'는 종가를 의미합니다.
                increasing_line_color='red', decreasing_line_color='green'
            )])

            # 차트 레이아웃을 업데이트합니다.
            fig_m.update_layout(
                title='Intraday KOSDAQ Candestick Chart',
                xaxis_title='date',
                yaxis_title='price',
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )

            # 차트를 Streamlit에 표시합니다.
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

    with tab2:
        termoption = st.selectbox(
        '기간선택',
        ('1일','1주','1개월','2개월','3개월','6개월','1년'),6)
        if termoption.endswith('주'):
            term = int(termoption.split('주')[0])
            termflag = 'w'
        elif termoption.endswith('개월'):
            term = int(termoption.split('개월')[0])
            termflag = 'm'
        elif termoption.endswith('년'):
            term = int(termoption.split('년')[0])*12
            termflag = 'm'
        elif termoption.endswith('일'):
            term = int(termoption.split('일')[0])
            termflag = 'd'
        
        col5, col6 = st.columns(2)

        with col5:
            df_price = class_data.getindexprice(date, 'u001', 'D',termflag,term)
            df_price['logdate'] =pd.to_datetime(df_price['logdate'])

            # 캔들스틱 차트를 생성합니다.
            fig_m = go.Figure(data=[go.Candlestick(
                x=df_price['logdate'],
                open=df_price['open'],  # 여기서 'open'은 개장 가격을 의미합니다.
                high=df_price['high'],  # 'high'는 최고 가격을 의미합니다.
                low=df_price['low'],    # 'low'는 최저 가격을 의미합니다.
                close=df_price['close'],  # 'close'는 종가를 의미합니다.
                increasing_line_color='red', decreasing_line_color='green'
            )])

            # 차트 레이아웃을 업데이트합니다.
            fig_m.update_layout(
                title='Daily KOSPI Candestick Chart',
                xaxis_title='date',
                yaxis_title='price',
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                    )
            )

            # 차트를 Streamlit에 표시합니다.
            st.plotly_chart(fig_m, use_container_width=True)


        with col6:
            df_price = class_data.getindexprice(date, 'u201', 'D',termflag,term)
            df_price['logdate'] =pd.to_datetime(df_price['logdate'])

            # 캔들스틱 차트를 생성합니다.
            fig_m = go.Figure(data=[go.Candlestick(
                x=df_price['logdate'],
                open=df_price['open'],  # 여기서 'open'은 개장 가격을 의미합니다.
                high=df_price['high'],  # 'high'는 최고 가격을 의미합니다.
                low=df_price['low'],    # 'low'는 최저 가격을 의미합니다.
                close=df_price['close'],  # 'close'는 종가를 의미합니다.
                increasing_line_color='red', decreasing_line_color='green'
            )])

            # 차트 레이아웃을 업데이트합니다.
            fig_m.update_layout(
                title='Daily KOSDAQ Candestick Chart',
                xaxis_title='date',
                yaxis_title='price',
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                    )
            )

            # 차트를 Streamlit에 표시합니다.
            st.plotly_chart(fig_m, use_container_width=True)


        col7, col8 = st.columns(2)
        with col7:
            df_kospi = class_data.getindex_fundmental(date,'KOSPI')
            df_kospi['logdate'] = pd.to_datetime(df_kospi['logdate'])  # Ensure datetime is in the correct format
            fig_d = px.line(df_kospi, x='logdate', y='per', labels={'price': 'Price (Daily)'}, title="KOSPI PER")
            fig_d.update_layout(autosize=True)
            st.plotly_chart(fig_d, use_container_width=True)
            fig_d = px.line(df_kospi, x='logdate', y='pbr', labels={'price': 'Price (Daily)'}, title="KOSPI PBR")
            fig_d.update_layout(autosize=True)
            st.plotly_chart(fig_d, use_container_width=True)
        with col8:
            df_kosdaq = class_data.getindex_fundmental(date,'KOSDAQ')
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

if date and add_selectbox=="주식":
    maxdate = class_data.getmaxdate(todate,1)

    if int(todate)>=int(maxdate):
        date = maxdate
    
    
    # selected_stock =st.text_input('🔎 종목 선택')
    stock_list = class_data.getstockmater(date)
    stock_options = {f"{row['stockcode']} - {row['stockname']}": (row['stockcode'], row['stockname']) for index, row in stock_list.iterrows()}
    stock_choice = st.selectbox("Choose a stock", list(stock_options.keys()))  

    selected_stock, stockname = stock_options[stock_choice]
    df = class_data.getthemestock(date, selected_stock, 2)
    df_aftermarket = class_data.getAftermarketprice(date, selected_stock, 4)
    st.dataframe(df, use_container_width=True)
    st.dataframe(df_aftermarket)


    col7, col8 = st.columns(2)
    
    with col7:
        df_price = class_data.getstockprice(date, selected_stock, 'M')
        
        df_price['datetime'] =pd.to_datetime(df_price['datetime'])

        # 캔들스틱 차트를 생성합니다.
        fig_m = go.Figure(data=[go.Candlestick(
            x=df_price['datetime'],
            open=df_price['open'],  # 여기서 'open'은 개장 가격을 의미합니다.
            high=df_price['high'],  # 'high'는 최고 가격을 의미합니다.
            low=df_price['low'],    # 'low'는 최저 가격을 의미합니다.
            close=df_price['close'],  # 'close'는 종가를 의미합니다.
            increasing_line_color='red', decreasing_line_color='green'
        )])

        # 차트 레이아웃을 업데이트합니다.
        fig_m.update_layout(
            title='Intraday Candestick Chart',
            xaxis_title='date',
            yaxis_title='price',
            autosize=True,
            xaxis=dict(
                    tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                    nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                    tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                )
        )

        # 차트를 Streamlit에 표시합니다.
        st.plotly_chart(fig_m, use_container_width=True)
    
    with col8:
        df_price = class_data.getstockprice(date, selected_stock, 'D')
        df_price['logdate'] = pd.to_datetime(df_price['logdate'])  # Ensure datetime is in the correct format
        fig_d = px.line(df_price, x='logdate', y='close', labels={'price': 'Price (Daily)'}, title="Daily Price Trends")
        fig_d.update_layout(autosize=True)
        st.plotly_chart(fig_d, use_container_width=True)




if date and add_selectbox=="관심종목":
    maxdate = class_data.getmaxdate(todate,1)

    if int(todate)>=int(maxdate):
        date = maxdate
    st.title('Stock Interest Tracker')
    
    interested_stock_list = class_data.getinterestedstocklist()
    interestname = st.selectbox('🔎 종목 선택', interested_stock_list['interestname'])
    # interestname= "'{}'".format(interestname)
    df_theme_stocks = class_data.getthemestock(date, interestname,3)
    st.dataframe(df_theme_stocks, use_container_width=True)

    
if date and add_selectbox=="옵션":
    
    maxdate = class_data.getmaxdate(todate,1)

    if int(todate)>=int(maxdate):
        date = maxdate

    st.subheader('📈옵션 현황')
    
    tab1,tab2 = st.tabs(['Intraday','Daily'])
    with tab1:
        col1,col2 = st.columns(2)


        with col1:
            df_option = class_data.getoptionprice(date,'m',0,'c',None,None)
            fig = px.line(df_option, x='datetime', y='priceclose', title='Call price')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='nonpaid', title='Call OpenInterest')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='iv', title='Call Implied Volatility')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='delta', title='Call delta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='gamma', title='Call gamma')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='theta', title='Call theta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='vega', title='Call vega')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            df_option = class_data.getoptionprice(date,'m',0,'p',None,None)
            # st.dataframe(df_option)

            fig = px.line(df_option, x='datetime', y='priceclose', title='Put')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)
           
            fig = px.line(df_option, x='datetime', y='nonpaid', title='Put OpenInterest')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='iv', title='Put Implied Volatility')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='delta', title='Put delta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='gamma', title='Put gamma')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='theta', title='Put theta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='datetime', y='vega', title='Put vega')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%H:%M'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        termoption = st.selectbox(
        '기간선택',
        ('1일','1주','1개월','2개월','3개월','6개월','1년'),6)
        if termoption.endswith('주'):
            term = int(termoption.split('주')[0])
            termflag = 'w'
        elif termoption.endswith('개월'):
            term = int(termoption.split('개월')[0])
            termflag = 'm'
        elif termoption.endswith('년'):
            term = int(termoption.split('년')[0])*12
            termflag = 'm'
        elif termoption.endswith('일'):
            term = int(termoption.split('일')[0])
            termflag = 'd'

        col3,col4 = st.columns(2)
        with col3:
            df_option = class_data.getoptionprice(date,'d',0,'c',termflag,term)
            fig = px.line(df_option, x='logdate', y='priceclose', title='Call price')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='nonpaid', title='Call OpenInterest')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='iv', title='Call Implied Volatility')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='delta', title='Call delta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='gamma', title='Call gamma')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='theta', title='Call theta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='vega', title='Call vega')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            df_option = class_data.getoptionprice(date,'d',0,'p',termflag,term)
            # st.dataframe(df_option)

            fig = px.line(df_option, x='logdate', y='priceclose', title='Put price')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)
           
            fig = px.line(df_option, x='logdate', y='nonpaid', title='Put OpenInterest')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='iv', title='Put Implied Volatility')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='delta', title='Put delta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='gamma', title='Put gamma')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='theta', title='Put theta')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)

            fig = px.line(df_option, x='logdate', y='vega', title='Put vega')
            fig.update_layout(
                autosize=True,
                xaxis=dict(
                        tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                        nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                        tickformat='%Y-%m-%d'  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                    )
            )    
            st.plotly_chart(fig, use_container_width=True)
# 사이드바 추가 기능
with st.sidebar:
    st.subheader("📰 Market Insights")
    st.text_area("🆕 최신 뉴스와 업데이트", height=100)
    # if st.checkbox("🔮 Show Predictive Analytics"):
        # st.subheader("🔮 Predictive Analytics")
        # st.write("예측 분석 내용이 여기에 포함됩니다.")