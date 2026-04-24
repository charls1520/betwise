from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.ingestion.tasks import run_daily_scraping
from src.utils.logger import get_logger
from src.ml.train import run_weekly_training

logger = get_logger()

scheduler = BackgroundScheduler()

def start_scheduler():
    # Run scraping every day at 02:00 AM
    scheduler.add_job(
        run_daily_scraping,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_scraping",
        replace_existing=True
    )
    
    # Run ML retraining every Monday at 04:00 AM
    scheduler.add_job(
        run_weekly_training,
        trigger=CronTrigger(day_of_week='mon', hour=4, minute=0),
        id="weekly_training",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler started with daily ingestion and weekly ML training.")