"""Background worker: runs scheduled jobs. Start with `python -m app.worker`.

For now only a placeholder loop; the Moodle sync is added with its own task.
"""

import logging
import time

from app.config import get_settings

log = logging.getLogger("app.worker")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    interval_minutes = get_settings().sync_interval_minutes
    log.info("Worker started, interval %d min (no jobs yet)", interval_minutes)
    while True:
        time.sleep(interval_minutes * 60)
        log.info("Tick (no jobs yet)")


if __name__ == "__main__":
    main()
