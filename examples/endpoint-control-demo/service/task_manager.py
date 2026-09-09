# Copyright 2026 InsightOS
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
import threading
from datetime import datetime
from typing import Dict, List, Optional
from .interface import TaskInterface

TIMEFORMAT = "%Y-%m-%d %H:%M:%S.%f"


def get_current_time_str() -> str:
    return datetime.now().strftime(TIMEFORMAT)[:-3]


class TaskStatus:
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, dict] = {}
        self.task_registry: Dict[int, TaskInterface] = {}
        self.task_threads: Dict[str, threading.Thread] = {}
        self.task_cancellation: Dict[str, threading.Event] = {}
        self.lock = threading.Lock()

    def register_tasks(self, tasks: Dict[int, TaskInterface]):
        with self.lock:
            self.task_registry.update(tasks)

    def start_task(self, index: int, input_data: dict) -> dict:
        if index not in self.task_registry:
            raise ValueError(f"Unknown task index: {index}")

        task_id = f"task-{uuid.uuid4().hex[:8]}"
        now = get_current_time_str()
        cancel_event = threading.Event()

        task_info = {
            "task_id": task_id,
            "index": index,
            "status": TaskStatus.RUNNING,
            "created_at": now,
            "updated_at": now,
        }

        with self.lock:
            self.tasks[task_id] = task_info
            self.task_cancellation[task_id] = cancel_event

        thread = threading.Thread(
            target=self._execute_task, args=(task_id, index, input_data, cancel_event)
        )
        thread.daemon = True
        thread.start()

        with self.lock:
            self.task_threads[task_id] = thread

        return {"task_id": task_id}

    def _execute_task(self, task_id, index, input_data, cancel_event):
        try:
            if cancel_event.is_set():
                with self.lock:
                    self.tasks[task_id].update(
                        {"status": TaskStatus.CANCELLED, "updated_at": get_current_time_str()}
                    )
                return

            task_handler = self.task_registry[index]
            result = task_handler.execute(input_data)

            if cancel_event.is_set():
                with self.lock:
                    self.tasks[task_id].update(
                        {"status": TaskStatus.CANCELLED, "updated_at": get_current_time_str()}
                    )
                return

            with self.lock:
                self.tasks[task_id].update(
                    {
                        "status": TaskStatus.COMPLETED,
                        "updated_at": get_current_time_str(),
                        "payload": result,
                    }
                )
        except Exception as e:
            with self.lock:
                self.tasks[task_id].update(
                    {
                        "status": TaskStatus.FAILED,
                        "updated_at": get_current_time_str(),
                        "message": str(e),
                    }
                )
        finally:
            with self.lock:
                self.task_threads.pop(task_id, None)
                self.task_cancellation.pop(task_id, None)

    def get_task_info(self, task_id: str) -> Optional[dict]:
        with self.lock:
            return self.tasks.get(task_id)

    def list_tasks(self) -> List[dict]:
        with self.lock:
            return list(self.tasks.values())

    def list_task_registry(self) -> List[dict]:
        with self.lock:
            return [
                {"index": index, "task_name": type(handler).__name__}
                for index, handler in self.task_registry.items()
            ]

    def cancel_task(self, task_id: str) -> bool:
        with self.lock:
            task_info = self.tasks.get(task_id)
            if not task_info:
                return False
            if task_info["status"] in [
                TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED
            ]:
                return True
            cancel_event = self.task_cancellation.get(task_id)
            if cancel_event:
                cancel_event.set()
            task_info.update(
                {"status": TaskStatus.CANCELLED, "updated_at": get_current_time_str()}
            )
            return True


task_manager = TaskManager()
