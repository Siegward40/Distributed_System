import tkinter as tk

class Visualizer:

    width = 1600
    height = 800
    max_events = 10 # max events per process line
    display_vector_tmstps = True # else Lamport's logical timestamps will be displayed

    events = [chr(i) for i in range(97,123)]    #letters a to z


    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chandy-Lamport Algorithm")
        self.root.geometry(f"{Visualizer.width}x{Visualizer.height}")
        self.graph_cnv = tk.Canvas(self.root, width=0.9*Visualizer.width, height=0.8*Visualizer.height, bg="white")
        self.graph_cnv.pack(padx=0.05*Visualizer.width, pady=0.1*Visualizer.height)
        self.cnv_width = int(self.graph_cnv['width'])
        self.cnv_height = int(self.graph_cnv['height'])
        self.process_line_width = 0
        self.nb_events = 0
        self.process_list = []
        self.lamport_tmstps = {}
        self.vector_tmstps = {}
        self.cursors = {}


    def add_all_proccess(self, all_process:dict):
        """Parameter is a dictionary of all process with identifier of process as key and its name as value (label)"""
        nb_p = len(all_process)
        w = self.cnv_width
        h = self.cnv_height
        x_start = 0.1 * w
        x_end = 0.95 * w
        self.process_line_width = (0.95-0.1) * w

        for i, (k, v) in enumerate(all_process.items()):

            self.process_list.append(k)
            self.lamport_tmstps[k] = 0
            self.vector_tmstps[k] = [0 for _ in range(nb_p)]

            y = (i+0.5)/nb_p * h
            self.graph_cnv.create_text(0.07 * w, y, text=v, fill ="black", font="Arial 20 bold")
            self.graph_cnv.create_line((x_start,y), (x_end,y), width=4, arrow='last')
            self.cursors[k] = [x_start+0.5*self.process_line_width/Visualizer.max_events, y]
            self.graph_cnv.create_text(x_start, y-20, text=self._getTimestamp(k), fill ="blue", font="Arial 14")


    def add_simple_event(self, process, event=None):  #event: str
        if process in self.cursors:

            if not event:
                event = Visualizer.events[self.nb_events]

            self._incrTimestamp(process)

            x = self.cursors[process][0]
            y = self.cursors[process][1]
            self._dot(self.graph_cnv, (x,y))
            self.graph_cnv.create_text(x, y+20, text=event, fill ="black", font="Arial 14")
            self.graph_cnv.create_text(x, y-20, text=self._getTimestamp(process), fill ="blue", font="Arial 14")
            self.cursors[process][0] += self.process_line_width/Visualizer.max_events
            self.nb_events += 1


    def add_message(self, sender, receiver, message:str, events=None):  #events: tuple of str
        if sender in self.cursors and receiver in self.cursors:

            if not events:
                events = (Visualizer.events[self.nb_events], Visualizer.events[self.nb_events+1])

            # sender event
            self._incrTimestamp(sender)
            x_s = self.cursors[sender][0]
            y_s = self.cursors[sender][1]
            self._dot(self.graph_cnv, (x_s,y_s))
            self.graph_cnv.create_text(x_s, y_s+20, text=events[0], fill ="black", font="Arial 14")
            self.graph_cnv.create_text(x_s, y_s-20, text=self._getTimestamp(sender), fill ="blue", font="Arial 14")
            self.cursors[sender][0] += self.process_line_width/Visualizer.max_events

            # receiver event
            self._incrTimestamp(receiver, sender)
            x_r = max(self.cursors[receiver][0], x_s+0.3*self.process_line_width/Visualizer.max_events)
            y_r = self.cursors[receiver][1]
            self._dot(self.graph_cnv, (x_r,y_r))
            self.graph_cnv.create_text(x_r, y_r+20, text=events[1], fill ="black", font="Arial 14")
            self.graph_cnv.create_text(x_r, y_r-20, text=self._getTimestamp(receiver), fill ="blue", font="Arial 14")
            self.cursors[receiver][0] = x_r + self.process_line_width/Visualizer.max_events

            # message
            self.graph_cnv.create_line((x_s,y_s), (x_r,y_r), width=3, arrow='last')
            self.graph_cnv.create_text((x_r+x_s)/2, (y_r+y_s)/2, text=message, fill ="red", font="Arial 14 bold")

            self.nb_events += 2


    def _dot(self, canvas, center:tuple, radius=6, color='black'):
        x,y = center
        A = (x-radius, y-radius)
        B = (x+radius, y+radius)
        return canvas.create_oval(A, B, fill=color, outline=color)


    def _incrTimestamp(self, process, other_process=None):
        # define other_process as sender when process RECEIVE message (NOT SEND)
        if Visualizer.display_vector_tmstps:
            if other_process:
                for i in range(len(self.process_list)):
                    self.vector_tmstps[process][i] = max(self.vector_tmstps[process][i], self.vector_tmstps[other_process][i])
            self.vector_tmstps[process][self.process_list.index(process)] += 1
        else:
            if other_process:
                self.lamport_tmstps[process] = max(self.lamport_tmstps[process], self.lamport_tmstps[other_process]) + 1
            else:
                self.lamport_tmstps[process] += 1


    def _getTimestamp(self, process):
        if Visualizer.display_vector_tmstps:
            return self.vector_tmstps[process]
        else:
            return self.lamport_tmstps[process]


    def run(self):
        self.root.mainloop()



if __name__ == "__main__":

    visualizer = Visualizer()

    #visualizer.add_all_proccess({1:"P1", 2:"P2", 3:"P3"})
    visualizer.add_all_proccess({1:"P1", 2:"P2", 3:"P3", 4:"P4"})

    visualizer.add_simple_event(1)
    visualizer.add_simple_event(1)
    visualizer.add_simple_event(2)
    visualizer.add_message(1,2,"m1")
    visualizer.add_message(1,3,"m2")
    visualizer.add_simple_event(3)
    visualizer.add_message(3,4,"m3")
    visualizer.add_simple_event(2)
    visualizer.add_message(2,1,"m4")
    visualizer.add_simple_event(4)
    visualizer.add_message(4,1,"m5")

    visualizer.run()