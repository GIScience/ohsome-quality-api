"""Helper functions for `asyncio`."""
import asyncio
from typing import Coroutine


async def gather_with_semaphore(tasks: list) -> Coroutine:
    """Limit the number of tasks executed at a time."""
    # Semaphore needs to initiated inside of the event loop
    semaphore = asyncio.Semaphore(4)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))
