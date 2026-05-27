from apscheduler.schedulers.asyncio import AsyncIOScheduler
from agents.Cost_Estimator.services.cost_services.market_updater import update_market_rates


def start_scheduler(db):
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        lambda: update_market_rates(db, "Hyderabad"),
        "interval",
        hours=24
    )

    scheduler.start()