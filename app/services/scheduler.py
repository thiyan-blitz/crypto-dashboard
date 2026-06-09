from apscheduler.schedulers.blocking import BlockingScheduler
from app.services.pipeline import run_pipeline

scheduler=BlockingScheduler()

@scheduler.scheduled_job('interval', minutes=1)
def scheduled_job():
    print("Scheduler started")
    run_pipeline()

if __name__=="__main__":
    print("Scheduler started! Fetching evry 5 minutes...")
    print("Press Ctrl+C to stop.")
    run_pipeline()
    scheduler.start()
    