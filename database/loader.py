import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

class Loader():
    def __init__(self):
        self.host = os.getenv('HOST')
        self.user = os.getenv('DEFAULT_USER')
        self.pw = os.getenv('PASSWORD')
        self.port = os.getenv('PORT')
        self.db = os.getenv('DATABASE')
        self.sslmode = os.getenv("SSLMODE")
        self.connection_str = f"postgresql://{self.user}:{self.pw}@{self.host}:{self.port}/{self.db}?sslmode={self.sslmode}"

    def load_case_data(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.cases_df = pd.read_sql('case_data', con=conn)
        conn.close()

    def load_case_verdicts(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.case_verdict_df = pd.read_sql('court_verdicts', con=conn)
        conn.close()

    def load_drug_count_data(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.drug_count_df = pd.read_sql('drug_prevalence_count', con=conn)
        conn.close()

    def load_sewage_data(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.sewege_df = pd.read_sql('sewage', con=conn)
        conn.close()

l = Loader()
l.load_case_data()
print(l.cases_df)