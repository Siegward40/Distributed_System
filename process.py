from datetime import datetime
from channel import Channel



class Process:

    process_list = []
    task_queue = []

    def __init__(self, id_process, name_process):
        self.id_process = id_process
        self.name_process = name_process
        self.state = {'status': 'stopped', 'events': 0}
        self.channels = {}
        self.events = {self: 0}
        Process.process_list.append(self)


    def create_channel(self, process_receiver):
         for id_process in Process.process_list:
            if id_process.id_process != self.id_process:
                channel = Channel(self, process_receiver)
                self.channels[process_receiver.id_process] = channel


    def start(self):
        self.state = {'status': 'running', 'events': 0}
        self.send_message(list(self.channels.keys()))
        print(self.state)

    def stop(self):
        self.state = None

    def send_message(self, id_process_receivers):
        
        for id_process_receiver in id_process_receivers:
            if id_process_receiver in self.channels:
                    self.events[self] += 1
                    self.channels[id_process_receiver].send_message()

    def get_message(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Message from {self.name_process} at {timestamp}"
        return message
    
    def receive_message(self, message):
        print(f"Process {self.name_process} a reçu le message: {message}")
        self.state['events'] += 1
