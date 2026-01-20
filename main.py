from channel import Channel
from process import Process
from simulator import Simulator
from visualizer import Visualizer

def main():
    visualizer = Visualizer()
    sim = Simulator(visualizer)

    # create processes
    processes = {}
    for i in range(1, 5):
        p = Process(i, sim, visualizer)
        processes[i] = p
        sim.add_process(p)

    # create channels
    # bidirectional for snapshot
    channels = [
        (1,2), (2,1), (1,3), (3,1), (2,3), (3,2), (2,4), (4,2), (3,4), (4,3), (4,1), (1,4)
    ]
    for s, r in channels:
        ch = Channel(processes[s], processes[r])
        processes[s].add_channel_out(r, ch)
        processes[r].add_channel_in(s, ch)

    # define traces
    # example traces
    processes[1].trace = [
        (1, ('compute',)),
        (3, ('send', 2, 'msg1')),
        (5, ('compute',)),
        (7, ('send', 3, 'msg2')),
    ]
    processes[2].trace = [
        (2, ('compute',)),
        (4, ('send', 3, 'msg3')),
        (6, ('compute',)),
        (8, ('send', 4, 'msg4')),
    ]
    processes[3].trace = [
        (3, ('compute',)),
        (5, ('send', 4, 'msg5')),
    ]
    processes[4].trace = [
        (4, ('compute',)),
        (6, ('send', 1, 'msg6')),
    ]

    visualizer.add_all_proccess({1: "P1", 2: "P2", 3: "P3", 4: "P4"})
    sim.run()
    visualizer.run()

if __name__ == "__main__":
    main()
    