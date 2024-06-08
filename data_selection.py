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
        
    
    # @st.cache_resource #연결에는 resource
    def init_db(_self):
        
        connection_string = f"mssql+pyodbc://{_self.user_id}:{_self.password}@{_self.server}/{_self.database}?driver=ODBC Driver 17 for SQL Server"
        engine = create_engine(connection_string, echo=False)
        try:
            _self.db_init = engine.connect()
            return _self.db_init
        except Exception as e:
            st.error(f"Failed to connect to database: {e}")
            return None

    @st.cache_data  #데이터 가져오는 것에는 data
    def getCalendar(_self, date, termflag, term):
        todate = int(str(date).replace('-', ''))
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = (todate,2, termflag, term,'')
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        frdate = int(df['frdate'][0])
        return frdate 

   
    @st.cache_data  #데이터 가져오는 것에는 data
    def getBacktest(_self, date,flag, termflag, term,etc):
        todate = int(str(date).replace('-', ''))
        sql = '''
            EXEC [SL_GetBacktest] ?,?,?,?,?
            '''
        params = (todate,flag, termflag, term,etc)
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        
        return df
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getstockprice(_self,date,code,frame):
        todate = int(str(date).replace('-',''))
        if frame=='D':
            frdate = _self.getCalendar(todate,'m','1')
            sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
            params = (frdate,'', code, int(5))
            df = pd.read_sql(sql, con=_self.db_init, params=params)
        else:
            sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
            params = ('',todate, code, int(6))
            df = pd.read_sql(sql, con=_self.db_init,params=params)
            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)

        return df
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getstockgongsi(_self,date,code):
        todate = int(str(date).replace('-',''))

        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = ('',todate, code, int(8))
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        df['logtime'] = df['logtime'].astype(str).str.zfill(4)
        df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
        df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
        df.drop(['logdate', 'logtime'], axis=1, inplace=True)
        return df

    @st.cache_data  #데이터 가져오는 것에는 data    
    def getoptionprice(_self,date,frame,otm,cpflag,termflag,term):
        todate = int(str(date).replace('-',''))
        if frame=='d':
            frdate = _self.getCalendar(todate,termflag,term)
            sql= '''
            EXEC [SL_GetOption] ?,?,?,?,?
            '''
            params=(frdate,todate,'D',otm,cpflag)            
            df = pd.read_sql(sql, con=_self.db_init,params=params)
            df['logdate'] =pd.to_datetime(df['logdate'])     

        else:
            sql ='''
            EXEC [SL_GetOption] ?,?,?,?,?
            '''
            params = (todate,todate,'m',otm,cpflag)
            df = pd.read_sql(sql, con=_self.db_init,params=params)

            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)

            df['datetime'] =pd.to_datetime(df['datetime'])
        return df
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getstockmater(_self,date):
        todate = int(str(date).replace('-',''))
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = (todate,1,'','','')
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        return df[['stockcode','stockname']]
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getDataProcess(_self,flag):
        
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = ('',12,'','',flag)
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        return df['logdate'][0]

    @st.cache_data  #데이터 가져오는 것에는 data    
    def getindexprice(_self,date,code,frame,termflag,term):
        todate = int(str(date).replace('-',''))

        
        if frame=='D':
            frdate = _self.getCalendar(todate,termflag,term)
            sql ="EXEC [SL_GetIndexreturn] ?,?,?,?"
            params = (frdate,todate, code, 1)
            df = pd.read_sql(sql, con=_self.db_init, params=params)
        else:
            sql ="EXEC [SL_GetIndexreturn] ?,?,?,?"
            params = ('',todate, code, 2)
            df = pd.read_sql(sql, con=_self.db_init,params=params)
            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime'], axis=1, inplace=True)
        return df
 

    @st.cache_data  #데이터 가져오는 것에는 data   
    def getindexprice_sugup(_self,date,code,frame,termflag,term):
               
        todate = str(date).replace('-','')
        if frame=='D':
            frdate = _self.getCalendar(todate,termflag,term)
            sql ="EXEC [SL_GetIndexreturn] ?,?,?,?"
            params = (frdate,todate, code, 3)
            df = pd.read_sql(sql, con=_self.db_init, params=params)
        else:
            sql ="EXEC [SL_GetIndexreturn] ?,?,?,?"
            params = ('',todate, code, 4)
            df = pd.read_sql(sql, con=_self.db_init, params=params)
            df['logtime'] = df['logtime'].astype(str).str.zfill(4)
            df['logtime'] = df['logtime'].str[:2] + ':' + df['logtime'].str[2:]
            df['datetime'] = df['logdate'].astype(str) + ' ' + df['logtime'] + ':00'
            df.drop(['logdate', 'logtime','stockcode'], axis=1, inplace=True)       
        return df
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getindex_fundmental(_self,date,code,termflag,term):      
        todate = str(date).replace('-','')
        frdate = _self.getCalendar(todate,termflag,term)
        sql ="EXEC [SL_GetIndexreturn] ?,?,?,?"
        params = (frdate,todate, code, 5)
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        return df


    @st.cache_data  #데이터 가져오는 것에는 data
    def getthemename(_self):
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = ('',4,'','','')
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        return df[['themecode','themename']]
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getCurrentPrice(_self,date,flag,code):
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = (date,flag,'','',code)
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        price = round(df['close'].iloc[-1],2)
        delta = round(df['change'].iloc[-1],2)
        return price,delta

    @st.cache_data  #데이터 가져오는 것에는 data
    def getthemereturn(_self,date,termflag,term,options):
        todate = str(date).replace('-','')
        frdate = _self.getCalendar(todate,termflag,term)
        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = (frdate,todate,options ,7)
        df = pd.read_sql(sql, con=_self.db_init,params=params)

        return df

    @st.cache_data  #데이터 가져오는 것에는 data
    def getdatediff(_self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
            SELECT [FN_DATESEARCH](?,?) as 'date'
            '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        if df['date'][0] ==0:
            date = todate
        else:
            date = df['date'][0]
        return  date


    @st.cache_data  #데이터 가져오는 것에는 data
    def getmaxdate(_self,date,flag):
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
        elif flag==3:
            sql = '''
                EXEC [SL_GetInformation] ?,?,?,?,?
                '''
            params = (todate,13, '', '','')

        
        df = pd.read_sql(sql, con=_self.db_init, params=
                         params)
        return str(df['date'][0]).replace('-','')
    

    @st.cache_data  #데이터 가져오는 것에는 data
    def gettradinginfo(_self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC [SL_GetTradinginfo] ?,?
        '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        return df

    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getAftermarketprice(_self,date,options,flag):
        todate = str(date).replace('-','')
        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = ('',todate,options ,flag)
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        df.columns=['시간외 표준편차','시간외 거래대금','시간외 수익률']
        return df
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getmarketinfo(_self,date,termflag,term,flag):
        todate = str(date).replace('-','')
        frdate = _self.getCalendar(todate,termflag,term)
        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = (frdate,todate,'',flag)
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        return df

    @st.cache_data  #데이터 가져오는 것에는 data
    def getthemestock(_self,date,options,flag):
        todate = int(str(date).replace('-',''))
        sql = '''
        EXEC [SL_Getstockreturn] ?,?,?,?
        '''
        params = ('',todate,options,flag)
        df = pd.read_sql(sql, con=_self.db_init,params=params)
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


    @st.cache_data  #데이터 가져오는 것에는 data
    def getThemetermreturn(_self,date,termflag,term,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC [SL_GetThemereturn] ?,?,?,?

        '''
        params = (todate,termflag,term,flag)
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        df['termret']=round(df['termret'].astype(float)*100,2)
        df['avgamount'] = df['avgamount'].map('{:,.0f}'.format)
        df['avgshortamount'] = df['avgshortamount'].fillna(0)
        df['avgshortamount'] = df['avgshortamount'].map('{:,.0f}'.format)
        # 컬럼명 변경
        df.columns = ['테마명', '수익률(%)', '평균 거래대금', '평균 공매도 거래대금']
        return df


    @st.cache_data  #데이터 가져오는 것에는 data
    def getLastnews(_self,code):
        # todate = int(str(date).replace('-',''))
        sql ="EXEC [SL_Getstockreturn] ?,?,?,?"
        params = ('','', code, int(9))
        df = pd.read_sql(sql, con=_self.db_init,params=params)
        return df
    

    @st.cache_data  #데이터 가져오는 것에는 data
    def getTradinglist(_self,date,flag):
        todate = str(date).replace('-','')
        sql = '''
        EXEC [SL_GetTradinginfo] ?,?
        '''
        params = (todate,flag)
        df = pd.read_sql(sql, con=_self.db_init, params=params)
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
                nticks=10,
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
                    nticks=10,  # x축에 표시할 레이블의 최대 수를 설정합니다.
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

    @st.cache_data  #데이터 가져오는 것에는 data
    def marketcondition(_self,date,flag):
        sql = f"exec [SL_GetMainDashBoard] ?, ?"
        params = (date,flag)
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        percent_columns = ['D1','W1', 'W3', 'M1', 'M3', 'M6', 'M12', 'M24', 'M36']
        for col in percent_columns:
            df[col]=round(df[col].astype(float)*100,2)
        return df

    @st.cache_data  #데이터 가져오는 것에는 data
    def getconditionlist(_self):
        sql = '''
            EXEC [SL_GetInformation] ?,?,?,?,?
            '''
        params = ('',10, '', '','')
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        return df
    
    @st.cache_data  #데이터 가져오는 것에는 data
    def getstocklistbycondition(_self,date,condition):
        sql = '''
            EXEC [SL_GetStocklistbyCondition] ?,?
            '''
        params = (date,condition)
        df = pd.read_sql(sql, con=_self.db_init, params=params)
        return df
