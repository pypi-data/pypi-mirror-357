import threading

import remoulade
from remoulade import Worker

import patronx.tasks  # noqa: F401  # ensure actors are declared
from patronx.logger import get_logger
from patronx.schedule import start_scheduler

logger = get_logger(__name__)

def run_scheduler() -> None:
    logger.info("Starting scheduler")
    start_scheduler()

def run_worker() -> None:
    logger.info("Starting worker")
    worker = Worker(remoulade.get_broker())
    worker.start()
    worker.logger = logger


def run_worker_and_scheduler() -> None:
    sched_thread = threading.Thread(target=run_scheduler, name="scheduler", daemon=True)
    sched_thread.start()
    run_worker()
