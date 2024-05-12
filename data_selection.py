import datetime
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import streamlit as st
import plotly.express as px


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
        # connection_string = f"mssql+pyodbc://{self.user_id}:{self.password}@{self.server}/{self.database}?driver=ODBC Driver 17 for SQL Server"
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
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = (todate,2, termflag, term,'')
        df = pd.read_sql(sql, con=self.db_init, params=params)
        frdate = int(df['frdate'][0])
        return frdate 

    def getstockprice(self,date,code,frame):
        todate = int(str(date).replace('-',''))
        if frame=='D':
            frdate = self.getCalendar(todate,'m','1')
            sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
            params = (frdate,'', code, int(5))
            df = pd.read_sql(sql, con=self.db_init, params=params)
        else:
            sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
            params = ('',todate, code, int(6))
            df = pd.read_sql(sql, con=self.db_init,params=params)
            # df['logtime'] =df['logtime'].apply(lambda x: '0'+str(x) if len(str(x))==3 else x)
            # df['logtime'] =df['logtime'].apply(lambda x: str(x)[:2]+':'+str(x)[-2:])
            # cols = ['logdate', 'logtime']
            # df['datetime'] =df[cols].apply(lambda row: ' '.join(row.values.astype(str))+':00', axis=1)
            # df.drop(['logdate', 'logtime'], axis=1, inplace=True)
            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)

        return df
    
    def getstockgongsi(self,date,code):
        todate = int(str(date).replace('-',''))

        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = ('',todate, code, int(8))
        df = pd.read_sql(sql, con=self.db_init,params=params)
        df['logtime'] = df['logtime'].astype(str).str.zfill(4)
        df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
        df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
        df.drop(['logdate', 'logtime'], axis=1, inplace=True)
        return df

    def getoptionprice(self,date,frame,otm,cpflag,termflag,term):
        todate = int(str(date).replace('-',''))
        if frame=='d':
            frdate = self.getCalendar(todate,termflag,term)
            sql= '''
            EXEC [SL_GetOption] {},{},{},{},{}
            '''.format(frdate,todate,'D',otm,cpflag)            
            df = pd.read_sql(sql, con=self.db_init)
            df['logdate'] =pd.to_datetime(df['logdate'])
            
        else:
            sql = '''
            EXEC [SL_GetOption] {},{},{},{},{}
            '''.format(todate,todate,'m',otm,cpflag)
            df = pd.read_sql(sql, con=self.db_init)
            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)

            df['datetime'] =pd.to_datetime(df['datetime'])
        return df
    
    def getstockmater(self,date):
        todate = int(str(date).replace('-',''))
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = (todate,1,'','','')
        df = pd.read_sql(sql, con=self.db_init,params=params)
        return df[['stockcode','stockname']]
    
    def getinterestedstocklist(self,todate):
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = (todate,3,'','','')
        df = pd.read_sql(sql, con=self.db_init,params=params)
        return df
    
    def insert_interested_stock(self,interestname,stock_code, stock_name):
        if self.db_init is None:
            st.error("Database connection is not established.")
            return
        try:
            # Create a SQL statement
            sql_statement = text("INSERT INTO stock.dbo.tc_InterestedStocks (stockcode, stockname,ipuser,ipdate) VALUES (:interestname ,:code, :name,:ipuser,:ipdate)")
            self.db_init.execute(sql_statement, {"interestname": interestname,"code": stock_code, "name": stock_name, "ipuser": 'stock_server', "ipdate": datetime.now()})
            self.db_init.commit()
            st.success(f"{stock_name} added to interested stocks successfully!")
        except Exception as e:
            st.error(f"Error when inserting stock: {e}")

    def getindexprice(self,date,code,frame,termflag,term):
        todate = int(str(date).replace('-',''))
        if frame=='D':
            frdate = self.getCalendar(todate,termflag,term)
            sql ="EXEC [SL_GetIndexreturn] ?,?,?"
            params = (frdate, code, 1)
            df = pd.read_sql(sql, con=self.db_init, params=params)
        else:
            sql ="EXEC [SL_GetIndexreturn] ?,?,?"
            params = (todate, code, 2)
            df = pd.read_sql(sql, con=self.db_init,params=params)
            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)
        return df
 
    def getindexprice_sugup(self,date,code,frame,termflag,term):
               
        todate = str(date).replace('-','')
        if frame=='D':
            frdate = self.getCalendar(todate,termflag,term)
            sql ="EXEC [SL_GetIndexreturn] ?,?,?"
            params = (frdate, code, 3)
            df = pd.read_sql(sql, con=self.db_init, params=params)
        else:
            sql ="EXEC [SL_GetIndexreturn] ?,?,?"
            params = (todate, code, 4)
            df = pd.read_sql(sql, con=self.db_init, params=params)
            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime','stockcode'], axis=1, inplace=True)       
        return df

    def getindex_fundmental(self,date,code,termflag,term):      
        todate = str(date).replace('-','')
        frdate = self.getCalendar(todate,termflag,term)
        sql ="EXEC [SL_GetIndexreturn] ?,?,?"
        params = (frdate, code, 5)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df

    def getthemename(self):
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = ('',4,'','','')
        df = pd.read_sql(sql, con=self.db_init,params=params)
        return df[['themecode','themename']]
    
    def getCurrentPrice(self,date,flag,code):
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = (date,flag,'','',code)
        df = pd.read_sql(sql, con=self.db_init,params=params)
        price = round(df['close'].iloc[-1],2)
        delta = round(df['change'].iloc[-1],2)
        return price,delta

    def getthemereturn(self,date,termflag,term,options):
        todate = str(date).replace('-','')
        frdate = self.getCalendar(todate,termflag,term)
        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = (frdate,todate,options ,7)
        df = pd.read_sql(sql, con=self.db_init,params=params)

        return df

    def getdatediff(self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
            SELECT [FN_DATESEARCH](?,?) as 'date'
            '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        if df['date'][0] ==0:
            date = todate
        else:
            date = df['date'][0]
        return  date

    def getmaxdate(self,date,flag):
        todate = str(date).replace('-','')
        if flag==1: 
            sql = '''
                EXEC [SL_GetInformation] ?,?,?,?,?
                '''
            params = (todate,5, '', '','')
            
        elif flag==2:
            sql = '''
                EXEC [SL_GetInformation] ?,?,?,?,?
                '''
            params = (todate,6, '', '','')
        
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return str(df['date'][0]).replace('-','')
    
    def gettradinginfo(self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC [SL_GetTradinginfo] ?,?
        '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df

    
    def getAftermarketprice(self,date,options,flag):
        todate = str(date).replace('-','')
        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = ('',todate,options ,4)
        df = pd.read_sql(sql, con=self.db_init,params=params)
        df.columns=['시간외 표준편차','시간외 거래대금','시간외 수익률']
        return df


    def getthemestock(self,date,options,flag):
        todate = int(str(date).replace('-',''))
        sql = '''
        EXEC [SL_Getstockreturn] ?,?,?,?
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
        EXEC [SL_GetThemereturn] ?,?,?,?

        '''
        params = (todate,termflag,term,flag)
        df = pd.read_sql(sql, con=self.db_init,params=params)
        df['termret']=round(df['termret'].astype(float)*100,2)
        df['avgamount'] = df['avgamount'].map('{:,.0f}'.format)
        df['avgshortamount'] = df['avgshortamount'].fillna(0)
        df['avgshortamount'] = df['avgshortamount'].map('{:,.0f}'.format)
        # 컬럼명 변경
        df.columns = ['테마명', '수익률(%)', '평균 거래대금', '평균 공매도 거래대금']
        return df

    def getLastnews(self,code):
        # todate = int(str(date).replace('-',''))
        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = ('','', code, int(9))
        df = pd.read_sql(sql, con=self.db_init,params=params)
        return df
    
    def getTradinglist(self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC [SL_GetTradinginfo] ?,?
        '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df    
    
    def create_candlestick_chart(self, df, title, x_label, y_label):
        # x 축에 사용할 컬럼을 결정
        if 'datetime' in df.columns:
            x_values = df['datetime']
            tick_format = '%H:%M'  # 시간 데이터라고 가정
        elif 'logdate' in df.columns:
            x_values = df['logdate']
            tick_format = '%Y-%m-%d'  # 날짜 데이터라고 가정
        else:
            raise ValueError("DataFrame must have 'datetime' or 'logdate' columns")
        
        # 캔들스틱 차트 생성
        fig = go.Figure(data=[go.Candlestick(
            x=x_values,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='red', decreasing_line_color='green'
        )])
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            autosize=True,
            xaxis=dict(
                tickmode='auto',
                nticks=20,
                tickformat=tick_format
            )
        )
        return fig
    
    def create_line_chart(self, df, title, x_label, y_label):
        # x 축에 사용할 컬럼을 결정
        if 'datetime' in df.columns:
            tick_format = '%H:%M'  # 시간 데이터라고 가정
        elif 'logdate' in df.columns:
            tick_format = '%Y-%m-%d'  # 날짜 데이터라고 가정
        else:
            raise ValueError("DataFrame must have 'datetime' or 'logdate' columns")
        
        fig = px.line(df, x=x_label, y=y_label, title=title)
        
        fig.update_layout(
            autosize=True,
            xaxis=dict(
                    tickmode='auto',  # 자동 또는 사용자 지정 간격으로 레이블을 조정합니다.
                    nticks=20,  # x축에 표시할 레이블의 최대 수를 설정합니다.
                    tickformat=tick_format  # '01-Jan' 형식의 날짜 형식을 사용합니다.
                )
                 )   
    
        return fig


    def select_term_and_flag(self,options=('1일','1주','1개월','2개월','3개월','6개월'), default_index=5):
        term_option = st.selectbox('기간선택', options, default_index)
        
        # 기간과 플래그 추출
        if term_option.endswith('주'):
            term = int(term_option.rstrip('주'))
            term_flag = 'w'
        elif term_option.endswith('개월'):
            term = int(term_option.rstrip('개월'))
            term_flag = 'm'
        elif term_option.endswith('년'):
            term = int(term_option.rstrip('년')) * 12
            term_flag = 'm'
        elif term_option.endswith('일'):
            term = int(term_option.rstrip('일'))
            term_flag = 'd'
        else:
            raise ValueError("Invalid term option")

        return term, term_flag

    def marketcondition(self,date,flag):
        sql = f"exec [SL_GetMainDashBoard] ?, ?"
        params = (date,flag)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        percent_columns = ['D1','W1', 'W3', 'M1', 'M3', 'M6', 'M12', 'M24', 'M36']
        for col in percent_columns:
            df[col]=round(df[col].astype(float)*100,2)
        return df

    def getconditionlist(self):
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = ('',10, '', '','')
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df
    
    def getstocklistbycondition(self,date,condition):
        sql = '''
            EXEC [SL_GetStocklistbyCondition] ?,?
            '''
        params = (date,condition)
        df = pd.read_sql(sql, con=self.db_init, params=params)
        return df