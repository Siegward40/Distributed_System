from collections import deque

class Channel:
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver
        self.queue = deque()
        self.recorded = False
        self.recorded_messages = []

    def send(self, message):
        self.queue.append(message)
        if self.recorded:
            self.recorded_messages.append(message)
    
    def send_marker(self):
        self.queue.append(('marker', self.sender.id))
        if not self.recorded:
            self.recorded = True
            self.recorded_messages = []
    
    def get_recorded_messages(self):
        return self.recorded_messages
    
    def reset_recording(self):
        self.recorded = False
        self.recorded_messages = []
