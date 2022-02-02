document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector("#scrape-btn")
    btn.addEventListener('click', () => {
        btn.innerText = 'Preparing task...'
        btn.disabled = true
       $.ajax({
        url: '/scrape',
        method: 'GET'
    })
        .done(res => {
            btn.innerText = 'Scraper running...'
            const tid = res.task_id
            console.log(tid)
            const progressURL = `/celery-progress/${tid}/`
            const colors = {
                success: '#198754',
                error: '#dc3545',
                progress: '#0d6efd',
                ignored: '#6c757d'
            }
            CeleryProgressBar.initProgressBar(progressURL, {
                barColors: colors,
                onSuccess: () => {
                    const btn = document.querySelector("#scrape-btn")
                    btn.innerText = 'Start scraping'
                    btn.disabled = false
                }
            }); 
        })
    })
})