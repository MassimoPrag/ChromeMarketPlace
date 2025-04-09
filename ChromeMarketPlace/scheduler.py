from apscheduler.schedulers.blocking import BlockingScheduler
from SCRAPERS.makeOneCsv import makeOneDF

scheduler = BlockingScheduler()

@scheduler.scheduled_job("cron", hour=0)  # Runs every night at midnight
def scheduled_task():
    makeOneDF()

if __name__ == "__main__":
    scheduler.start()
