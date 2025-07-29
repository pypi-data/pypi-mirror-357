import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed

class Task:
    def __init__(self, name, func, retries=0, timeout=None, sleep_time=0):
        self.name = name
        self.func = func
        self.dependencies = []
        self.retries = retries
        self.timeout = timeout  # Em segundos
        self.sleep_time = sleep_time  # Tempo de espera antes de executar
        self.status = 'PENDING'

    def set_upstream(self, task):
        if task.name not in self.dependencies:
            self.dependencies.append(task.name)

    def __rshift__(self, other):
        other.set_upstream(self)
        return other

    def run_with_retries(self):
        attempts = 0
        while attempts <= self.retries:
            try:
                print(f"\n[▶] Running task: {self.name} (attempt {attempts + 1})")

                # Aguarda antes de executar a task
                if self.sleep_time > 0:
                    print(f"[...] Task {self.name} sleeping for {self.sleep_time} seconds before execution...")
                    time.sleep(self.sleep_time)

                if self.timeout:
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(self.func)
                        future.result(timeout=self.timeout)
                else:
                    self.func()

                self.status = 'SUCCESS'
                print(f"[✓] Task {self.name} completed successfully.")
                return
            except TimeoutError:
                print(f"[...] Task {self.name} timed out after {self.timeout} seconds.")
            except Exception as e:
                print(f"[X] Task {self.name} failed:\n{e}")
                traceback.print_exc()

            attempts += 1
            if attempts > self.retries:
                self.status = 'FAILED'
                print(f"[X] Task {self.name} failed after {self.retries + 1} attempts.")
                raise Exception(f"Task {self.name} failed after retries.")

class Pipeline:
    def __init__(self, tasks, max_workers=2):
        self.tasks = {task.name: task for task in tasks}
        self.max_workers = max_workers

    def run(self):
        executed = set()

        def execute_task(task):
            for dep in task.dependencies:
                if dep not in executed:
                    execute_task(self.tasks[dep])

            if task.name not in executed:
                task.run_with_retries()
                executed.add(task.name)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}

            for task in self.tasks.values():
                if not task.dependencies:
                    futures[executor.submit(execute_task, task)] = task.name

            while futures:
                done, _ = as_completed(futures), []
                for future in done:
                    task_name = futures.pop(future, None)
                    if task_name:
                        print(f"[O] Finished: {task_name}")
