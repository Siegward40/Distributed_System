class Process:
    def __init__(self, id, simulator, visualizer=None):
        self.id = id
        self.simulator = simulator
        self.visualizer = visualizer
        self.state = 0
        self.channels_in = {} 
        self.channels_out = {}  
        self.trace = [] 
        self.snapshot_initiated = False
        self.local_state_recorded = None
        self.recorded_channels = {}

    def add_channel_in(self, sender_id, channel):
        self.channels_in[sender_id] = channel
    
    def add_channel_out(self, receiver_id, channel):
        self.channels_out[receiver_id] = channel

    def execute_action(self, action):
        if action[0] == 'compute':
            self.state += 1
            if self.visualizer:
                self.visualizer.add_simple_event(self.id)
        elif action[0] == 'send':
            receiver_id, message = action[1], action[2]
            channel = self.channels_out[receiver_id]
            delay = 1
            self.simulator.schedule_send(self, receiver_id, message, delay)

    def initiate_snapshot(self):
        self.snapshot_initiated = True
        self.local_state_recorded = self.state
        for receiver_id, channel in self.channels_out.items():
            self.simulator.schedule_marker(self, receiver_id, 1)
        for channel in self.channels_in.values():
            self.recorded_channels[channel] = []

    def receive_marker(self, sender_id):
        ch = self.channels_in[sender_id]
        popped = ch.queue.popleft()
        assert popped == ('marker', sender_id)
        if not self.snapshot_initiated:
            self.snapshot_initiated = True
            self.local_state_recorded = self.state
            self.recorded_channels[ch] = []
            for rid, ch_out in self.channels_out.items():
                self.simulator.schedule_marker(self, rid, 1)
            for ch_in in self.channels_in.values():
                if ch_in != ch:
                    self.recorded_channels[ch_in] = []
        else:
            if ch not in self.recorded_channels:
                self.recorded_channels[ch] = []

    def receive_message(self, message, sender_id):
        ch = self.channels_in[sender_id]
        if self.snapshot_initiated and ch in self.recorded_channels:
            self.recorded_channels[ch].append(message)
        self.state += 1
        if self.visualizer:
            self.visualizer.add_message(sender_id, self.id, message)
        popped = ch.queue.popleft()
        assert popped == message