from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django.core.files.storage import FileSystemStorage
from .models import *
from .data_scraper import *
import time
from django_celery_results.models import TaskResult


from .tasks import scrape_task


# Create your views here.
def index(request):
    return render(request, 'mo/index.html')

def start_scrape_task(request):
    # x = TaskResult.objects.filter(status=['-'])
    # print(x)
    task = scrape_task.delay()
    return JsonResponse({"task_id": task.task_id})
    # return render(request, 'test.html', {"task_id": scrape_task.task_id})

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
        return render(request, 'mo/index.html', {
            'uploaded_file_url': uploaded_file.file.url,
            "uploaded_file": uploaded_file
        })
    return redirect(index)