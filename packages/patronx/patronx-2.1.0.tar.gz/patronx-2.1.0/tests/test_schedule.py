import importlib


def test_interval_from_cron_is_positive():
    sched = importlib.import_module("patronx.schedule")
    assert sched._interval_from_cron("* * * * *") > 0

def test_start_scheduler_starts(monkeypatch):
    sched = importlib.import_module("patronx.schedule")
    importlib.reload(sched)

    DummyCfg = type(
        "Cfg",
        (),
        {
            "backup_cron": "* * * * *",
            "cleanup_cron": "* * * * *",
            "redis_url": "redis://r",
            "from_env": classmethod(lambda cls: cls()),
        },
    )
    monkeypatch.setattr(sched, "BackupConfig", DummyCfg, raising=False)

    monkeypatch.setattr(sched.redis, "from_url", lambda url: f"client:{url}")

    fake_broker = object()
    monkeypatch.setattr(sched.remoulade, "get_broker", lambda: fake_broker)

    jobs = [object()]
    monkeypatch.setattr(sched, "init_scheduled_jobs", lambda b, c: jobs)

    created = {}

    class DummyScheduler:
        def __init__(self, broker, client, schedule):
            created["args"] = (broker, client, schedule)
            self.logger = None

        def start(self):
            created["started"] = True

    monkeypatch.setattr(sched, "Scheduler", DummyScheduler)

    holder = {}
    monkeypatch.setattr(sched.remoulade, "set_scheduler", lambda s: holder.setdefault("sched", s))
    monkeypatch.setattr(sched.remoulade, "get_scheduler", lambda: holder["sched"])
    monkeypatch.setattr(sched.logger, "info", lambda *a, **k: None)

    sched.start_scheduler()

    assert created["args"] == (fake_broker, "client:redis://r", jobs)
    assert created.get("started") is True