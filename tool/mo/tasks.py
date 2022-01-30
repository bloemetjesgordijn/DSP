import time
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .data_scraper import *

messages = {
    "init": '{INFO}: Initializing Scraper...',
    "init done": "{INFO}: Scraper initialized...",
    "existing files": "{INFO}: Finding existing files",
    "query": "{INFO}: Quering uitspraken.rechtspraak.nl API",
    "no res": "{INFO}: No results found... ",
    "res": "{INFO}: Response returned NR_HERE cases succesfully, going over them now...",
    "new cases": "{INFO}: NR_HERE new cases found...",
    "done scraping": "{INFO}: Done with scraping...",
    "word processing": "{INFO}: Starting word processing...",
    "finished up": "{INFO}: Done with word processing...",
    "push1": "{INFO}: Pushing to database 1/3...",
    "push2": "{INFO}: Pushing to database 2/3...",
    "push3": "{INFO}: Pushing to database 3/3...",
    "done": "{INFO}: All data pushed."
}


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
    total = 500
    time.sleep(1)
    recorder.set_progress(1, total, messages['init'])
    time.sleep(1)
    scraper = DataScraper()
    recorder.set_progress(2, total, messages['init done'])
    time.sleep(1)
    recorder.set_progress(3, total, messages['existing files'])
    time.sleep(1)
    scraper.set_existing_files() 
    recorder.set_progress(4, total, messages['query'])
    results = scraper.query_uitspraken()

    if not results:
        recorder.set_progress(5, total, messages['no res'])
        return "No results found"
    
    recorder.set_progress(5, total, messages['res'].replace('NR_HERE', f'{len(results)}'))
    new_case_results = [result for result in results if result['TitelEmphasis'].replace(':', '-') not in scraper.cases_already_scraped]
    recorder.set_progress(6, total, messages['new cases'].replace('NR_HERE', f'{len(new_case_results)}'))

    for i, case in enumerate(new_case_results):
        parsed_id = case['TitelEmphasis'].replace(':', '-') 
        scraper.handle_case(case, parsed_id)
        recorder.set_progress(i + 1 + 6, total, f"Handled case {parsed_id}")
    recorder.set_progress(6 + len(new_case_results), total, messages['done scraping'])
    recorder.set_progress(1 + 6 + len(new_case_results), total, messages['word processing'])
    scraper.process_search_words()
    recorder.set_progress(2 + 6 + len(new_case_results), total, messages['finished up'])
    recorder.set_progress(3 + 6 + len(new_case_results), total, messages['push1'])
    # scraper.push_verdicts_to_db_new()
    time.sleep(2)
    recorder.set_progress(4 + 6 + len(new_case_results), total, messages['push2'])
    time.sleep(2)
    # scraper.push_case_data_to_db_new()
    recorder.set_progress(5 + 6 + len(new_case_results), total, messages['push3'])
    time.sleep(2)
    # scraper.push_counts_to_db_new()
    recorder.set_progress(6 + 6 + len(new_case_results), total, messages['done'])
    return "<h2> Finished scraping, new data is stored in the database</h2>"