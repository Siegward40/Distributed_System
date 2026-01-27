from channel import Channel
from process import Process
from simulator import Simulator
from visualizer import Visualizer
from terminal import Terminal


def main():

    terminal = Terminal()
    visualizer = Visualizer()
    sim = Simulator(visualizer)

    # Create processes with data of terminal
    try:
        print(terminal.processes_list)
        print(terminal.processes_trace)
        print(terminal.clock_type)

        # set clock type (lamport or vector)
        visualizer.display_vector_tmstps = (terminal.clock_type == "vector")

        # create processes
        processes = {}
        for i, process in enumerate(terminal.processes_list):
            p = Process(i+1, sim, visualizer)
            processes[i+1] = p
            sim.add_process(p)

        # create channels (bidirectional for snapshot)
        channels = []
        for i in range(len(terminal.processes_list)):
            for j in range(i, len(terminal.processes_list)):
                if i != j:
                    channels.append((i+1,j+1))
                    channels.append((j+1,i+1))
        for s, r in channels:
            ch = Channel(processes[s], processes[r])
            processes[s].add_channel_out(r, ch)
            processes[r].add_channel_in(s, ch)

        # define traces
        for i, process in enumerate(terminal.processes_list):
            if process in terminal.processes_trace:
                processes[i+1].trace = terminal.processes_trace[process]

        if len(terminal.processes_list) > 0:
            visualizer.set_all_proccess({processes[i+1]:p for i,p in enumerate(terminal.processes_list)})
            sim.run()
            visualizer.run()

    # Default example
    except Exception as e:
        print(e)

        visualizer.destroy()
        visualizer2 = Visualizer()
        sim = Simulator(visualizer2)

        # create processes
        processes = {}
        for i in range(1, 8):
            p = Process(i, sim, visualizer2)
            processes[i] = p
            sim.add_process(p)

        # create channels (bidirectional for snapshot)
        channels = [
            (1,2), (2,1), (1,3), (3,1), (2,3), (3,2), (2,4), (4,2), (3,4), (4,3), (4,1), (1,4)
        ]
        for s, r in channels:
            ch = Channel(processes[s], processes[r])
            processes[s].add_channel_out(r, ch)
            processes[r].add_channel_in(s, ch)

        # define traces
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

        visualizer2.set_all_proccess({1: "P1", 2: "P2", 3: "P3", 4: "P4"})
        sim.run()
        visualizer2.run()


if __name__ == "__main__":
    main()
