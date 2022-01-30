import time
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .data_scraper import *

@shared_task
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True

@shared_task(bind=True)
def scrape(self):
    recorder = ProgressRecorder(self)
    for i in range(5):
        time.sleep(5)
        recorder.set_progress(i, 5, f"Totally chilling at {i + 1}")
    return "All is scraped" 



@shared_task(bind=True)
def scrape2(self):
    recorder = ProgressRecorder(self)

    print('{INFO}: Initializing Scraper...')
    scraper = DataScraper()
    print("{INFO}: Scraper initialized...")
    scraper.set_existing_files()
    results = scraper.query_uitspraken()
    print("{INFO}: No results found... ")
    if not results:
        return "<h3>No results found</h3>"
    print(f"[INFO]: Response returned {len(results)}succesfully, going over them now...")
    new_case_results = [result for result in results if result['TitelEmphasis'].replace(':', '-') not in scraper.cases_already_scraped]
    print(f"[INFO]: {len(new_case_results)} new cases found...")
    for case in new_case_results[:10]:
        parsed_id = case['TitelEmphasis'].replace(':', '-') 
        scraper.handle_case(case, parsed_id)
    print("{INFO}: Done with scraping...")
    time.sleep(2)
    print("{INFO}: Starting word processing...")
    scraper.process_search_words()
    print("{INFO}: Done with word processing...")
    scraper.push_verdicts_to_db_new()
    scraper.push_case_data_to_db_new()
    scraper.push_counts_to_db_new()
    return "<h2> Finished scraping, new data is stored in the database</h2>"

        
    recorder = ProgressRecorder(self)
    for i in range(5):
        time.sleep(5)
        recorder.set_progress(i, 5, f"Totally chilling at {i + 1}")
    return "All is scraped" 


