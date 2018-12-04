from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Create your views here.
if 'scheduler' not in locals():
    scheduler = AsyncIOScheduler()


def fetch_task():
    scheduler.add_job()


def init_task(request):
    if not scheduler.running:
        scheduler.start()

    scheduler.add_job(func=fetch_task, trigger='interval', hours=1)


def index(request):
    pass
