from process import Process

class Main:
    def __init__(self):
        self.processes = []

    def setup(self):
        # Create processes
        p1 = Process(1, "Process 1", "Task A")
        p2 = Process(2, "Process 2", "Task B")
        p3 = Process(3, "Process 3", "Task C")

        self.processes.extend([p1, p2, p3])

        # Create channels between processes
        p1.create_channel(p2)
        p1.create_channel(p3)
        p2.create_channel(p1)
        p2.create_channel(p3)
        p3.create_channel(p1)
        p3.create_channel(p2)

        Process.task_queue.extend(["Task B", "Task A", "Task C"])

    def run(self):
        for process in self.processes:
            process.start()


if __name__ == "__main__":
    main = Main()
    main.setup()
    main.run()

