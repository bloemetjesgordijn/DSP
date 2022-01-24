import requests
import json
import urllib.request
import os
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

from .constants import *
load_dotenv()

class DataScraper():
    def __init__(self, query='drugs'):
        self.searchQuery = query
        self.baseUrl = 'https://uitspraken.rechtspraak.nl/api/zoek' 
        self.uitsprakenBaseUrl = 'https://uitspraken.rechtspraak.nl/inziendocument?id='
        self.case_count = 100000 
        # self.save_text_location = os.getcwd() + '/data/courtcases/' 
        # self.cases_df = pd.read_csv("data/cases3.csv", sep=',')
        # self.cases_already_scraped = os.listdir(self.save_text_location)
        self.host = os.getenv('HOST')
        self.user = os.getenv('DEFAULT_USER')
        self.pw = os.getenv('PASSWORD')
        self.port = os.getenv('PORT')
        self.db = os.getenv('DATABASE')
        self.sslmode = os.getenv("SSLMODE")
        self.connection_str = f"postgresql://{self.user}:{self.pw}@{self.host}:{self.port}/{self.db}?sslmode={self.sslmode}"
        self.case_verdict_df = pd.DataFrame(columns=['date', 'caseid', 'casetext'])
        # Tekstfragmenten ommitten for now
        self.cases_df = pd.DataFrame(columns=['Titel', 'Uitspraakdatum', 'UitspraakdatumType', 'GerechtelijkProductType', 'Proceduresoorten', 'Rechtsgebieden', 'caseid'])

    def set_existing_files(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        df = pd.read_sql('''SELECT caseid FROM public.court_verdicts''', con=conn)
        self.cases_already_scraped = list(df['caseid'])

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
            "date": case['Uitspraakdatum'],
            "caseid": parsed_id,
            "casetext": self.get_case_text(case['TitelEmphasis'])
        }
        data_row_2 = {key: val for key, val in case.items() if key in self.cases_df.columns}
        data_row_2['caseid'] = parsed_id
        self.case_verdict_df = self.case_verdict_df.append(data_row_1, ignore_index=True)
        self.cases_df = self.cases_df.append(data_row_2, ignore_index=True)

        # case_text = self.get_case_text(case['TitelEmphasis'])
        # with open(self.save_text_location + parsed_id + ".txt","w+", encoding='utf-8') as f:
            # f.write(case_text)

    def process_search_words(self):
        data = pd.DataFrame()
        for key, search_words in DRUGS_AND_PRECURSORS.items():
            print(key)
            print(search_words)
            df = self.count_mentions(search_words).rename(columns={"count": f"{key}_count"})
            try:
                data = pd.merge(data, df, on=['date', 'Case ID'], how='left')
            except:
                data = df
        data.sort_values(by='date', ascending=False, inplace=True)
        self.drug_word_count_df = data

    def count_mentions(self, word_arr):
        date_and_count = []
        for _, row in self.case_verdict_df.iterrows():
            date = row["date"]
            case_id = row['caseid']
            case_text = row['casetext']
            occurrences = 0
            for word in word_arr:
                occurrences += case_text.lower().count(word.lower())
            date_and_count.append([date, case_id, occurrences])

        results = pd.DataFrame(date_and_count, columns=['date', 'caseid', 'count'])
        return results

    def push_verdicts_to_db_new(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.case_verdict_df.to_sql('court_verdicts', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_case_data_to_db_new(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.cases_df.to_sql('case_data', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_counts_to_db_new(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        self.drug_word_count_df.to_sql('court_verdicts', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()
    
    def push_verdicts_to_db(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        df = pd.DataFrame()
        court_text_files = os.listdir(self.save_text_location)
        for case in court_text_files:
            data = {'caseid': case[:-4]}
            try:
                with open(f"{self.save_text_location}/{case}", 'r') as f:
                    data['casetext'] = f.read()
            except Exception as e:
                print(e)
            df.append(data, ignore_index=True)
        df.to_sql('court_verdicts', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_counts_to_db(self):
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        df = pd.read_csv("processed_data/drug_word_count.csv", sep=';')
        df.to_sql('drug_prevalence_count', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()

    def push_court_data(self):
        use_cols = ['Titel', 'Uitspraakdatum', 'UitspraakdatumType', 'GerechtelijkProductType', 'Proceduresoorten', 'Rechtsgebieden', 'Case ID']
        engine = create_engine(self.connection_str)
        conn = engine.connect()
        df = pd.read_csv("processed_data/courtdata.csv", sep=';', usecols=use_cols)
        df['Proceduresoorten'] = df['Proceduresoorten'].apply(lambda x: x.strip('[]').replace("'", '').split(','))
        df['Rechtsgebieden'] = df['Rechtsgebieden'].apply(lambda x: x.strip('[]').replace("'", '').split('; '))
        df = df.explode(column='Proceduresoorten')
        df = df.explode(column='Rechtsgebieden')
        new_cols = ['titel', 'court_datum', 'uitspraak_type', 'gerechtelijk_product_type', 'procedure_soorten', 'rechtsgebieden', 'case_id']
        mapper = {old: new for old, new in zip(use_cols, new_cols)}
        df.rename(columns=mapper, inplace=True)
        df.to_sql('case_data', con=conn, schema='public', if_exists='append', index=False, chunksize=500)
        conn.close()
    
# scraper = DataScraper()
# scraper.set_existing_files()
# print(scraper.cases_already_scraped)
# print('lets go')
# results = scraper.query_uitspraken()
# print('done')
# if not results:
#     exit()
# for case in results:
#     print(case)
#     exit()

if __name__ == '__main__':
    scraper = DataScraper()
    scraper.set_existing_files()
    results = scraper.query_uitspraken()

    results = results[:3]
    for case in results:
        parsed_id = case['TitelEmphasis'].replace(':', '-') 
        print(parsed_id)
        if parsed_id in scraper.cases_already_scraped:
            print('nah')
            continue
        else:
            print('yeh')
            scraper.handle_case(case, parsed_id)

    print(scraper.case_verdict_df.head())