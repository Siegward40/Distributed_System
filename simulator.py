import heapq

class Simulator:
    def __init__(self, visualizer=None, name="DefaultSimulator"):
        self.name = name
        self.visualizer = visualizer
        self.event_queue = []
        self.processes = {}
        self.current_time = 0

    def run(self):
        for p in self.processes.values():
            for ts, action in p.trace:
                heapq.heappush(self.event_queue, (ts, 'action', p.id, action))

        while self.event_queue:
            ts, event_type, *params = heapq.heappop(self.event_queue)
            self.current_time = ts
            if event_type == 'action':
                p_id, action = params
                p = self.processes[p_id]
                p.execute_action(action)
            elif event_type == 'receive':
                receiver_id, message, sender_id = params
                p = self.processes[receiver_id]
                p.receive_message(message, sender_id)
            elif event_type == 'marker_receive':
                receiver_id, sender_id = params
                p = self.processes[receiver_id]
                p.receive_marker(sender_id)

    def add_process(self, process):
        self.processes[process.id] = process

    def schedule_send(self, sender, receiver_id, message, delay):
        timestamp = self.current_time + delay
        heapq.heappush(self.event_queue, (timestamp, 'receive', receiver_id, message, sender.id))
        channel = sender.channels_out[receiver_id]
        channel.send(message)

    def schedule_marker(self, sender, receiver_id, delay):
        timestamp = self.current_time + delay
        heapq.heappush(self.event_queue, (timestamp, 'marker_receive', receiver_id, sender.id))
        channel = sender.channels_out[receiver_id]
        channel.send_marker()
    