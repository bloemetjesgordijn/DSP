import os
import pandas as pd
from sqlalchemy import create_engine
from constants import DRUGS_AND_PRECURSORS_TABLEAU

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

    def propagate_count_changes(self):
        self.load_case_verdicts()
        data = pd.DataFrame()
        for drug, drug_ingredients in DRUGS_AND_PRECURSORS_TABLEAU.items():
            print(drug)
            df1 = self.count_mentions(drug_ingredients['altnames']).rename(columns={"count": f"{drug}_count".lower()})
            try:
                data = pd.merge(data, df1, on=['date', 'case_id'], how='left')
            except:
                data = df1
            for precursor, precursor_info in drug_ingredients['precursors'].items():
                print(precursor)
                df2 = self.count_mentions(precursor_info['altnames']).rename(columns={"count": f"{precursor}_count".lower()})
                data = pd.merge(data, df2, on=['date', 'case_id'], how='left')
                for ppc, lvals in precursor_info['preprecursors'].items():
                    df3 = self.count_mentions(lvals).rename(columns={"count": f"{ppc}_count".lower()})
                    data = pd.merge(data, df3, on=['date', 'case_id'], how='left')

        data.sort_values(by='date', ascending=False, inplace=True)
        self.drug_prevalence_count_tableau = data

    def count_mentions(self, word_arr: list) -> pd.DataFrame:
        date_and_count = []
        for _, row in self.case_verdict_df.iterrows():
            # date = row["date"]
            # case_id = row['case_id']
            # case_text = row['case_text']
            occurrences = 0
            for word in word_arr:
                occurrences += row['case_text'].lower().count(word.lower())
            date_and_count.append([row['date'], row['case_id'], occurrences])

        results = pd.DataFrame(date_and_count, columns=['date', 'case_id', 'count'])
        return results





