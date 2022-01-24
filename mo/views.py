from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import FileSystemStorage
from .models import *
from .data_scraper import *

# Create your views here.
def index(request):
    return render(request, 'index.html')

def start_scraping(request):
    scraper = DataScraper()
    scraper.set_existing_files()
    results = scraper.query_uitspraken()
    if not results:
        return HttpResponse("<h3>No results found</h3>")
    for case in results:
        parsed_id = case['TitelEmphasis'].replace(':', '-') 
        if f"{parsed_id}" in scraper.cases_already_scraped:
            continue
        else:
            scraper.handle_case(case, parsed_id)
    scraper.process_search_words()
    scraper.push_verdicts_to_db_new()
    scraper.push_case_data_to_db_new()
    scraper.push_counts_to_db_new()
    
    # scraper.cases_df.to_csv('..data/cases4.csv', sep=';')

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