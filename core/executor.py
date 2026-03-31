from concurrent.futures import ProcessPoolExecutor
from typing import Optional
import time

_pool: Optional[ProcessPoolExecutor] = None
_max_tasks: int = 10
last_request_time: float = 0.0


def init(max_tasks_per_child: int = 10) -> None:
    global _pool, _max_tasks
    _max_tasks = max_tasks_per_child
    _pool = ProcessPoolExecutor(max_workers=1, max_tasks_per_child=max_tasks_per_child)


def restart() -> None:
    global _pool
    if _pool is not None:
        _pool.shutdown(wait=False)
    _pool = ProcessPoolExecutor(max_workers=1, max_tasks_per_child=_max_tasks)


def shutdown() -> None:
    global _pool
    if _pool is not None:
        _pool.shutdown(wait=False)
        _pool = None


def get() -> ProcessPoolExecutor:
    return _pool


def record_request() -> None:
    global last_request_time
    last_request_time = time.time()
