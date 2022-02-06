from django.db import ProgrammingError
import requests
import json
import urllib.request
import os
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
# from dotenv import load_dotenv

from constants import *
# load_dotenv()

class DataScraper():
    def __init__(self, query='drugs'):
        self.searchQuery = query
        self.baseUrl = 'https://uitspraken.rechtspraak.nl/api/zoek' 
        self.uitsprakenBaseUrl = 'https://uitspraken.rechtspraak.nl/inziendocument?id='
        self.case_count = 100000 
        self.host = os.getenv('HOST')
        self.user = os.getenv('DEFAULT_USER')
        self.pw = os.getenv('PASSWORD')
        self.port = os.getenv('PORT')
        self.db = os.getenv('DATABASE')
        self.sslmode = os.getenv("SSLMODE")
        self.connection_str = f"postgresql://{self.user}:{self.pw}@{self.host}:{self.port}/{self.db}?sslmode={self.sslmode}"

        self.col_mapper = {
            'Titel': 'titel',
            'Uitspraakdatum': 'court_datum', 
            'UitspraakdatumType': 'uitspraak_type', 
            'GerechtelijkProductType': 'gerechtelijk_product_type', 
            'Proceduresoorten': 'procedure_soorten', 
            'Rechtsgebieden': 'rechtsgebieden', 
            'Case ID': 'case_id' 
        }
        self.cases_df = pd.DataFrame(columns=['titel', 'court_datum', 'uitspraak_type', 'gerechtelijk_product_type', 'procedure_soorten', 'rechtsgebieden', 'case_id'])
        self.case_verdict_df = pd.DataFrame(columns=['date', 'case_id', 'case_text'])

    def set_existing_files(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        try:
            print('IN TRY')
            df = pd.read_sql('court_verdicts', con=conn)
            self.cases_already_scraped = list(df['case_id'])
        except Exception:
            print('IN EXCEPTION')
            print("No table with that name yet")
            self.cases_already_scraped = []

    def query_uitspraken(self):
        files = {
            "StartRow": 0,
            "PageSize": self.case_count,
            "ShouldReturnHighlights":'true',
            "ShouldCountFacets":'true',
            "SortOrder":"Relevance",
            "SearchTerms":[{"Term": self.searchQuery, "Field": "AlleVelden"}],
            "Contentsoorten": [],
            "Rechtsgebieden": [],
            "Instanties": [],
            "DatumPublicatie": [],
            "DatumUitspraak": [],
            "Advanced": {"PublicatieStatus":"AlleenGepubliceerd"},
            "CorrelationId": "9abc658b0ce64f8786992af6965aabc4",
            "Proceduresoorten": []
        }
        try:
            response = requests.post(self.baseUrl, json=files)
            responseJSON = json.loads(response.text)
            results = responseJSON['Results']
            return results
        except urllib.error.HTTPError as err:
            with open("error_log.txt", 'w') as f:
                f.write(str(err))
            return None

    def get_case_text(self, caseId):
        response = requests.get(self.uitsprakenBaseUrl + caseId)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup_content = soup.find("div", {"id": 'content'})
        uitspraak_html = soup_content.find('div', {'class': 'uitspraak'})
        if soup_content.find('div', {'class': 'uitspraak'}) is not None:
            uitspraak_html = soup_content.find('div', {'class': 'uitspraak'})
        elif soup_content.find('div', {'class': 'conclusie'}) is not None:
            uitspraak_html =  soup_content.find('div', {'class': 'conclusie'})
        uitspraak = uitspraak_html.get_text().replace(',', '')
        return uitspraak

    def handle_case(self, case, parsed_id):
        data_row_1 = {
            "date": [case['Uitspraakdatum']],
            "case_id": [parsed_id],
            "case_text": [self.get_case_text(case['TitelEmphasis'])]
        }
        df_row_1 = pd.DataFrame.from_dict(data_row_1)

        data_row_2 = {self.col_mapper[key]: [val] for key, val in case.items() if key in self.col_mapper}
        data_row_2['case_id'] = [parsed_id]
        df_row_2 = pd.DataFrame.from_dict(data_row_2)
        
        self.case_verdict_df = pd.concat([self.case_verdict_df, df_row_1]) 
        self.cases_df = pd.concat([self.cases_df, df_row_2])


    def preprocess_case_data(self):
        self.cases_df.to_csv('t.csv', index=False, sep=';')
        self.cases_df['gerechtscode'] = pd.DataFrame(self.cases_df['case_id'].str.split('-').tolist(), columns=['a', 'b', 'code', 'd', 'e'])['code']
        self.cases_df['locatie'] = self.cases_df['gerechtscode'].map(GERECHTSCODE_LOCATIE_MAPPING)

        self.cases_df['procedure_soorten'] = self.cases_df['procedure_soorten'].str.replace("Peek,", "")
        self.cases_df['procedure_soorten'] = self.cases_df['procedure_soorten'].apply(lambda x: str(x)[1:-1].replace('"', "").split(','))
        self.cases_df['rechtsgebieden'] = self.cases_df['rechtsgebieden'].apply(lambda x: str(x)[1:-1].replace('"', "").split(','))

        self.cases_df = self.cases_df.explode('procedure_soorten').reset_index(drop=True)
        self.cases_df = self.cases_df.explode('rechtsgebieden').reset_index(drop=True)


    def process_search_words_tableau(self):
        data = pd.DataFrame()
        for drug, drug_ingredients in DRUGS_AND_PRECURSORS_TABLEAU.items():
            print(drug)
            df1 = self.count_mentions_tableau(drug_ingredients['altnames']).rename(columns={"count": f"{drug}_count".lower()})
            try:
                data = pd.merge(data, df1, on=['date', 'case_id'], how='left')
            except:
                data = df1
            for precursor, precursor_info in drug_ingredients['precursors'].items():
                print(precursor)
                df2 = self.count_mentions_tableau(precursor_info['altnames']).rename(columns={"count": f"{precursor}_count".lower()})
                data = pd.merge(data, df2, on=['date', 'case_id'], how='left')
                for ppc, lvals in precursor_info['preprecursors'].items():
                    df3 = self.count_mentions_tableau(lvals).rename(columns={"count": f"{ppc}_count".lower()})
                    data = pd.merge(data, df3, on=['date', 'case_id'], how='left')

        data.sort_values(by='date', ascending=False, inplace=True)
        self.drug_prevalence_count_tableau = data

        cols_to_drop = [col for col in self.drug_prevalence_count_tableau.columns if '_y' in col]
        cols_rename = {col: col[:-2] for col in self.drug_prevalence_count_tableau.columns if '_x' in col}
        self.drug_prevalence_count_tableau.drop(columns=cols_to_drop, inplace=True)
        self.drug_prevalence_count_tableau.rename(columns=cols_rename, inplace=True)

        df = self.drug_prevalence_count_tableau.sum(axis=0).reset_index()
        df.rename(columns={'index': 'col', 0: 'sum'}, inplace=True)

        cols_to_drop = df[df['sum'] == 0]['col'].tolist()
        self.drug_prevalence_count_tableau.drop(columns=cols_to_drop, inplace=True)


    def count_mentions_tableau(self, word_arr: list) -> pd.DataFrame:
        date_and_count = []
        for _, row in self.case_verdict_df.iterrows():
            occurrences = 0
            for word in word_arr:
                occurrences += row['case_text'].lower().count(word.lower())
            date_and_count.append([row['date'], row['case_id'], occurrences])

        results = pd.DataFrame(date_and_count, columns=['date', 'case_id', 'count'])
        return results

    def push_verdicts_to_db_tableau(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.case_verdict_df.to_sql('court_verdicts', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_case_data_to_db_tableau(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        print(self.cases_df.head())
        self.cases_df.to_sql('case_data_tableau', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_counts_to_db_tableau(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.drug_prevalence_count_tableau.to_sql('drug_prevalence_count_tableau', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()
    
 
## --------------- NOT FOR TABLEAU ------------------- ##

    def process_search_words(self):
        data = pd.DataFrame()
        for key, search_words in DRUGS_AND_PRECURSORS.items():
            print(key)
            print(search_words)
            df = self.count_mentions(search_words).rename(columns={"count": f"{key}_count"})
            try:
                data = pd.merge(data, df, on=['date', 'case_id'], how='left')
            except:
                data = df
        data.sort_values(by='date', ascending=False, inplace=True)
        self.drug_word_count_df = data

    def count_mentions(self, word_arr):
        date_and_count = []
        for _, row in self.case_verdict_df.iterrows():
            date = row["date"]
            case_id = row['case_id']
            case_text = row['case_text']
            occurrences = 0
            for word in word_arr:
                occurrences += case_text.lower().count(word.lower())
            date_and_count.append([date, case_id, occurrences])

        results = pd.DataFrame(date_and_count, columns=['date', 'case_id', 'count'])
        return results

    def push_verdicts_to_db_new(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.case_verdict_df.to_sql('court_verdicts', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_case_data_to_db_new(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        print(self.cases_df.head())
        self.cases_df.to_sql('case_data', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_counts_to_db_new(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.drug_word_count_df.to_sql('drug_prevalence_count', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()
    
## --------------- NOT FOR TABLEAU ------------------- ##
    

# if __name__ == '__main__':
    # scraper = DataScraper()
    # scraper.set_existing_files()
    # results = scraper.query_uitspraken()
    # print(type(scraper.cases_already_scraped))

    # results = results[:3]
    # for case in results:
    #     parsed_id = case['TitelEmphasis'].replace(':', '-') 
    #     print(parsed_id)
    #     if parsed_id in scraper.cases_already_scraped:
    #         print('nah')
    #         continue
    #     else:
    #         print('yeh')
    #         scraper.handle_case(case, parsed_id)

    # print(scraper.case_verdict_df.head())