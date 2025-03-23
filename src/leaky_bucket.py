### asyncio is used because it's the easiest way to simulate a running system without threads
# also vanilla asyncion cannot be run from Jupyter

from asyncio import Lock, sleep, create_task, run
from collections import deque
from time import time
from random import random, randint


class LeakyBucket:
    """With queue (there is 'pure' implementation without queue, but this will allow to handle traffic bursts)"""

    def __init__(self, rate: int, capacity: int) -> None:
        """
        params:
            - rate - tasks/second that will be executed by the processor (in our case it's bucket itself for simplicity)
            - capacity - how many objects can bucket hold until it rejects a request for the next task
        """
        self._wait_time: float = 1 / rate
        self._capacity = capacity
        self._queue: deque[str] = deque()
        self._lock = Lock()  # for the safety of a queue
    
    async def add_task(self, task: str) -> bool:
        async with self._lock:
            if len(self._queue) < self._capacity:
                self._queue.append(task)
                print(f"task {task} added [capacity {len(self._queue)} / {self._capacity}]")
                return True
            print(f"task {task} cannot be created - bucket is too full")
            return False
    
    async def process_task(self) -> None:  # a.k.a `leak`
        while True:
            await sleep(self._wait_time)  # this is the moment when tasks can be added to the bucket
            async with self._lock:
                if self._queue:
                    task = self._queue.popleft()
                    print(f"Task {task} processed; timestamp={time()}; [capacity {len(self._queue)} / {self._capacity}]")

async def main():
    lb = LeakyBucket(2, 20)
    create_task(lb.process_task())
    while True:
        await sleep(random())  # make random smaller to increse rate of adding elements per second
        await lb.add_task(randint(0, 10 ** 6))

if __name__ == "__main__":
    run(main())
