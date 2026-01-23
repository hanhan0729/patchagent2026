from asyncio import tasks
import time
import pika
import multiprocessing
from pika.exceptions import AMQPConnectionError
from pika.adapters.blocking_connection import BlockingChannel
from typing import List, Dict, Union
from nvwa.logger import log
from nvwa.frontend.aixcc import AIxCCTask


class Daemon:
    def __init__(
        self,
        qserver: str,
        qname: str,
        max_proc: int = 10,
    ) -> None:
        self.qserver: str = qserver
        self.qname: str = qname
        self.max_proc: int = max_proc

        self.task_map: Dict[str, List[AIxCCTask]] = {}

    def setup(self) -> None:
        log.info(f"Connecting to rabbitmq server: {self.qserver}")
        while True:
            try:
                rabbitmq_conn = pika.BlockingConnection(pika.URLParameters(self.qserver))
                break
            except AMQPConnectionError:
                log.info("waiting for rabbitmq server...")
                time.sleep(5)
                continue
        channel = rabbitmq_conn.channel()
        channel.queue_declare(queue=self.qname, durable=True)

        self.channel: BlockingChannel = channel
        self.thread_pool = multiprocessing.Pool(processes=self.max_proc)
        self.sched_lock = multiprocessing.Lock()

    def _receive_task(self) -> None:
        assert self.sched_lock.acquire(block=False) is False

        while True:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.qname, auto_ack=True)
            if method_frame is None:
                break

            task = AIxCCTask.parse(body)
            if task.tag not in self.task_map:
                self.task_map[task.tag] = []
            self.task_map[task.tag].append(task)

    def _priority(self, task: AIxCCTask) -> int:
        running_proc_num = 0
        for task in self.task_map[task.tag]:
            if task.running:
                running_proc_num += 1
        return -running_proc_num

    def _schedule(self) -> None:
        assert self.sched_lock.acquire(block=False) is False

        next_task = None
        for _, tasks in self.task_map.items():
            for task in tasks:
                if not task.running:
                    if next_task is None or self._priority(task) > self._priority(next_task):
                        next_task = task
        
        if next_task is not None:
            self.add_task(next_task)

    def add_task(self, task: AIxCCTask) -> None:
        assert self.sched_lock.acquire(block=False) is False

        def _task_wrapper():
            task.run()
            self.schedule(task)

        task.running = False
        self.thread_pool.apply(_task_wrapper)

    def schedule(self, task: Union[None, AIxCCTask] = None) -> None:
        self.sched_lock.acquire(block=True)

        if task is not None:
            task.count += 1
            task.running = False

        log.info(f"Receiving task from queue")
        self._receive_task()

        log.info(f"Entering schedule loop")
        self._schedule()

        self.sched_lock.release()

    def start(self) -> None:
        self.setup()
        for _ in range(self.max_proc):
            self.schedule()
