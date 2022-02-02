import time
from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .data_scraper import *

messages = {
    "step1": 'Initializing Scraper...',
    "step2": "Scraper initialized",
    "step3": "Finding existing cases...",
    "step4": "Found NR_HERE existing cases already",
    "step5": "Quering uitspraken.rechtspraak.nl API...",
    "step6": ["No results found... ", "Response returned NR_HERE cases succesfully, checking for new cases..."],
    "step7": "NR_HERE new cases found...",
    "step8": "Handled case ECLI_HERE - (STATUS_HERE)",
    "step9": "Done scraping",
    "step10": "Starting word processing...",
    "step11": "Done with word processing...",
    "step12": "Pushing to database 1/3...",
    "step13": "Pushing to database 2/3...",
    "step14": "Pushing to database 3/3...",
    "step15": "All data pushed."
}

@shared_task(bind=True)
def scrape_task(self):
    recorder = ProgressRecorder(self)
    total = len(messages)
    time.sleep(1)
    recorder.set_progress(1, total, messages['step1'])
    time.sleep(1)
    scraper = DataScraper()
    recorder.set_progress(2, total, messages['step2'])
    time.sleep(1)
    recorder.set_progress(3, total, messages['step3'])
    time.sleep(1)
    scraper.set_existing_files() 
    recorder.set_progress(4, total, messages['step4'].replace('NR_HERE', f"{len(scraper.cases_already_scraped)}"))
    time.sleep(1)
    recorder.set_progress(5, total, messages['step5'])
    results = scraper.query_uitspraken()

    if not results:
        recorder.set_progress(total, total, messages['step6'][0])
        return "No results found"
    
    recorder.set_progress(6, total, messages['step6'][1].replace('NR_HERE', f'{len(results)}'))
    new_case_results = [result for result in results if result['TitelEmphasis'].replace(':', '-') not in scraper.cases_already_scraped]
    nr_new_cases = len(new_case_results)
    recorder.set_progress(7, total, messages['step7'].replace('NR_HERE', f'{nr_new_cases}'))

    for i, case in enumerate(new_case_results):
        parsed_id = case['TitelEmphasis'].replace(':', '-') 
        scraper.handle_case(case, parsed_id)
        recorder.set_progress(8, total, messages['step8']\
                                            .replace('ECLI_HERE', f"{parsed_id}")\
                                            .replace('STATUS_HERE', f"{i+1}/{nr_new_cases}"))
    recorder.set_progress(9, total, messages['step9'])
    recorder.set_progress(10, total, messages['step10'])
    scraper.process_search_words()
    recorder.set_progress(11, total, messages['step11'])
    recorder.set_progress(12, total, messages['step12'])
    time.sleep(2)
    # scraper.push_verdicts_to_db_new()
    recorder.set_progress(13, total, messages['step13'])
    time.sleep(2)
    # scraper.push_case_data_to_db_new()
    recorder.set_progress(14, total, messages['step14'])
    time.sleep(2)
    # scraper.push_counts_to_db_new()
    recorder.set_progress(15, total, messages['step15'])
    return "Finished scraping, new data is stored in the database"