from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import FileSystemStorage
from .models import *
from .data_scraper import *
import time
from django_celery_results.models import TaskResult


from mo.tasks import scrape, scrape2


# Create your views here.
def index(request):
    return render(request, 'index.html')

def test_scrape(request):
    x = TaskResult.objects.filter(status=['-'])
    print(x)
    scrape_task = scrape2.delay()
    return JsonResponse({"task_id": scrape_task.task_id})
    # return render(request, 'test.html', {"task_id": scrape_task.task_id})

def start_scraping(request):
    print('{INFO}: Initializing Scraper...')
    scraper = DataScraper()
    print("{INFO}: Scraper initialized...")
    scraper.set_existing_files()
    results = scraper.query_uitspraken()
    print("{INFO}: No results found... ")
    if not results:
        return HttpResponse("<h3>No results found</h3>")
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
    return HttpResponse("<h2> Finished scraping, new data is stored in the database</h2>")

    

def upload(request):
    if request.method == "POST" and request.FILES['file']:
        # get form data
        file = request.FILES['file']
        title = request.POST['title']
        case_nr = request.POST['case_nr']
        description = request.POST['description']
        crime_type = request.POST['crime_type']
        uploaded_file = Upload.objects.create(
            file=file,
            title=title,
            case_nr=case_nr,
            description=description,
            crime_type=crime_type
        )
        return render(request, 'index.html', {
            'uploaded_file_url': uploaded_file.file.url,
            "uploaded_file": uploaded_file
        })
    return redirect(index)