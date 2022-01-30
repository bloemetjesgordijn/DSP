document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector("#scrape-btn")
    btn.addEventListener('click', () => {
       $.ajax({
        url: '/test',
        method: 'GET'
    })
        .done(res => {
            const tid = res.task_id
            console.log(tid)
            const url2 = `/celery-progress/${tid}/`
            // var progressUrl = "{% url 'celery_progress:task_status' tid %}";
            // CeleryProgressBar.initProgressBar(progressUrl); 
            CeleryProgressBar.initProgressBar(url2); 
        })
    })
})