from datetime import datetime

import redis
import remoulade
from croniter import croniter
from remoulade.scheduler import ScheduledJob, Scheduler

from patronx.config import BackupConfig
from patronx.logger import get_logger

logger = get_logger(__name__)

def _interval_from_cron(expr: str) -> int:
    """Compute seconds between two consecutive cron occurrences."""

    now = datetime.utcnow()
    itr = croniter(expr, now)
    first = itr.get_next(datetime)
    second = itr.get_next(datetime)
    return int((second - first).total_seconds()) or 1


def init_scheduled_jobs(backup_cron: str, cleanup_cron: str) -> list[ScheduledJob]:
    return [
        ScheduledJob(
            actor_name="run_backup_job",
            interval=_interval_from_cron(backup_cron),
        ),
        ScheduledJob(
            actor_name="cleanup_old_backups",
            interval=_interval_from_cron(cleanup_cron),
        ),
    ]

def start_scheduler() -> None:
    """Start a scheduler with backup and cleanup jobs."""
    config = BackupConfig.from_env()
    scheduler = Scheduler(
        broker=remoulade.get_broker(),
        client=redis.from_url(config.redis_url),
        schedule=init_scheduled_jobs(config.backup_cron, config.cleanup_cron),
    )
    scheduler.logger = logger
    remoulade.set_scheduler(scheduler)
    logger.info("Starting scheduler")
    remoulade.get_scheduler().start()
    logger.info("Scheduler stopped")