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

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
