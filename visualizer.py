import tkinter as tk
from tkinter import messagebox as mb
import time

class Visualizer:
    """Tkinter interface for visualizing Global States and Distributed Snapshots of processes and their tasks."""

    events = [chr(i) for i in range(97,123)]        # letters a to z
    events.extend([chr(i) for i in range(945,970)]) # greek letters

    timer = 2


    def __init__(self, display_vector_tmstps=False, max_events=15):
        self.root = tk.Tk()
        self.root.title("Chandy-Lamport Algorithm")
        self.w_width = self.root.winfo_screenwidth()
        self.w_height = self.root.winfo_screenheight()
        self.root.state('zoomed')
        tk.Label(self.root, text="Chandy-Lamport Algorithm", font="Arial 20").pack()

        self.display_vector_tmstps = display_vector_tmstps # False for Lamport's clock, True for vector clock
        self.max_events = max_events

        self.graph_cnv = tk.Canvas(self.root, width=0.9*self.w_width, height=0.75*self.w_height, bg="white")
        self.graph_cnv.pack(padx=0.05*self.w_width)
        self.cnv_width = int(self.graph_cnv['width'])
        self.cnv_height = int(self.graph_cnv['height'])
        self.graph_cnv.create_text(0.2*self.cnv_width, 0.97*self.cnv_height, text="→ message in transit", fill ="orange", font="Arial 16")
        self.graph_cnv.create_text(0.4*self.cnv_width, 0.97*self.cnv_height, text="→ message received", fill ="brown", font="Arial 16")
        self.graph_cnv.create_text(0.6*self.cnv_width, 0.97*self.cnv_height, text="--- consistent cut", fill ="green", font="Arial 16")
        self.graph_cnv.create_text(0.8*self.cnv_width, 0.97*self.cnv_height, text="--- inconsistent cut", fill ="red", font="Arial 16")

        self.process_line_width = 0
        self.nb_events = 0
        self.process_list = []
        self.process_names = []
        self.lamport_tmstps = {}
        self.vector_tmstps = {}
        self.cursors = {}
        self.in_transit = {}
        self.timer = Visualizer.timer   # délai en mode auto (secondes)
        self.step_mode = True           # True = pas à pas
        self._step_var = tk.IntVar(value=0)

        step_controls = tk.Frame()
        step_controls.pack()
        self.next_btn = tk.Button(step_controls, text="Next", command=self.next_step)
        self.next_btn.grid(row=0, column=0, padx=20, pady=5)
        self.mode_btn = tk.Button(step_controls, text="Auto", command=self.toggle_mode)
        self.mode_btn.grid(row=0, column=1, padx=20, pady=5)

        cut_controls = tk.Frame()
        cut_controls.pack()
        self.desired_cut = tk.StringVar()
        self.desired_cut.set("P1:4,P2:1,P3:0,P4:0")
        tk.Label(cut_controls, text="Create cut: for each process, indicate the index of the event before the cut", font="Arial 12").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(cut_controls, textvariable=self.desired_cut, font="Arial 12").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(cut_controls, text="Display", command=self._draw_cut).grid(row=0, column=2, padx=5, pady=5)

        self.events_log = { }
        # structure:
        # process -> list of dicts
        # dict = {
        #   'x': float,
        #   'y': float,
        #   'type': 'local' | 'send' | 'receive',
        #   'msg': message or None,
        #   'peer': other process or None
        # }



    def set_all_proccess(self, all_process:dict):
        """Parameter is a dictionary of all process with identifier of process as key and its name as value (label)"""
        nb_p = len(all_process)
        w = self.cnv_width
        h = self.cnv_height
        x_start = 0.1 * w
        x_end = 0.95 * w
        self.process_line_width = (0.95-0.1) * w

        for i, (k, v) in enumerate(all_process.items()):

            self.process_list.append(k)
            self.process_names.append(v)
            self.lamport_tmstps[k] = 0
            self.vector_tmstps[k] = [0 for _ in range(nb_p)]

            y = (i+0.5)/nb_p * h
            self.graph_cnv.create_text(0.07 * w, y, text=v, fill ="black", font="Arial 20 bold")
            self.graph_cnv.create_line((x_start,y), (x_end,y), width=4, arrow='last')
            self.graph_cnv.create_text(x_start, y-20, text=self._getTimestamp(k), fill ="blue", font="Arial 14")
            self.cursors[k] = [x_start+0.5*self.process_line_width/self.max_events, y]

            self.events_log[k] = []
            self.events_log.setdefault(k, []).append({
                'x': x_start+0.25*self.process_line_width/self.max_events,
                'y': y,
                'type': 'local',
                'msg': None,
                'peer': None
            })


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
            self.events_log.setdefault(process, []).append({
                'x': x + 0.5*self.process_line_width/self.max_events,
                'y': y,
                'type': 'local',
                'msg': None,
                'peer': None
            })

            self.cursors[process][0] += self.process_line_width/self.max_events
            self.nb_events += 1
            self.root.update_idletasks()
            self.wait_step()


    def add_message(self, sender, receiver, message:str, event=None):  #events: tuple of str
        if sender in self.cursors and receiver in self.cursors:

            if not event:
                event = Visualizer.events[self.nb_events]

            # sender event
            self._incrTimestamp(sender)
            x_s = self.cursors[sender][0]
            y_s = self.cursors[sender][1]
            self._dot(self.graph_cnv, (x_s,y_s))
            self.graph_cnv.create_text(x_s, y_s+20, text=event, fill ="black", font="Arial 14")
            self.graph_cnv.create_text(x_s, y_s-20, text=self._getTimestamp(sender), fill ="blue", font="Arial 14")
            self.events_log.setdefault(sender, []).append({
                'x': x_s + 0.5*self.process_line_width/self.max_events,
                'y': y_s,
                'type': 'send',
                'msg': message,
                'peer': receiver
            })
            self.cursors[sender][0] += self.process_line_width/self.max_events

            # receiver event -> display after receiving in receiving_message
            x_r = max(self.cursors[receiver][0], x_s+0.3*self.process_line_width/self.max_events)
            y_r = self.cursors[receiver][1]

            # message
            x_r_temp = x_r-5
            y_r_temp = y_r-30 if y_r > y_s else y_r+30
            self.in_transit[(sender,receiver,message)] = (self.graph_cnv.create_line((x_s,y_s), (x_r_temp,y_r_temp), width=3, fill ="orange", arrow='last'), (x_s,y_s), (self.lamport_tmstps[sender], self.vector_tmstps[sender]))
            self.graph_cnv.create_text((x_r+x_s)/2, (y_r+y_s)/2, text=message, fill ="blue", font="Arial 14 bold")

            self.nb_events += 1

            self.root.update_idletasks()
            self.wait_step()


    def receiving_message(self, sender, receiver, message:str, event=None):
        if sender in self.cursors and receiver in self.cursors and (sender,receiver,message) in self.in_transit:

            if not event:
                event = Visualizer.events[self.nb_events]

            x_s,y_s = self.in_transit[(sender,receiver,message)][1]
            tmstps = self.in_transit[(sender,receiver,message)][2]

            # receiver event
            self._incrTimestamp(receiver, tmstps)
            x_r = max(self.cursors[receiver][0], x_s+0.3*self.process_line_width/self.max_events)
            y_r = self.cursors[receiver][1]
            self._dot(self.graph_cnv, (x_r,y_r))
            self.graph_cnv.create_text(x_r, y_r+20, text=event, fill ="black", font="Arial 14")
            self.graph_cnv.create_text(x_r, y_r-20, text=self._getTimestamp(receiver), fill ="blue", font="Arial 14")

            line = self.in_transit[(sender,receiver,message)][0]
            self.graph_cnv.itemconfig(line, fill="brown")
            self.graph_cnv.coords(line, x_s, y_s, x_r, y_r)
            self.in_transit.pop((sender,receiver,message))

            self.events_log.setdefault(receiver, []).append({
                'x': x_r + 0.5*self.process_line_width/self.max_events,
                'y': y_r,
                'type': 'receive',
                'msg': message,
                'peer': sender
            })

            self.cursors[receiver][0] = x_r + self.process_line_width/self.max_events

            self.nb_events += 1

            self.root.update_idletasks()
            self.wait_step()


    def is_consistent_cut(self, cut: dict):
        """
        cut : dict {process -> event_index}
        """
        for p, idx in cut.items():
            events = self.events_log.get(p, [])
            for i in range(idx + 1):
                e = events[i]
                if e['type'] == 'receive':
                    sender = e['peer']
                    msg = e['msg']

                    # chercher le send correspondant
                    send_events = self.events_log.get(sender, [])
                    send_idx = next(
                        (j for j, se in enumerate(send_events)
                        if se['type'] == 'send' and se['msg'] == msg),
                        None
                    )

                    if send_idx is None or send_idx > cut.get(sender, -1):
                        return False
        return True


    def _dot(self, canvas, center:tuple, radius=6, color='black'):
        x,y = center
        A = (x-radius, y-radius)
        B = (x+radius, y+radius)
        return canvas.create_oval(A, B, fill=color, outline=color)


    def _draw_cut(self, cut=None):
        """
        cut : {process -> event_index}
        """
        try:
            if cut is None:
                cut = {}
                cut_str = self.desired_cut.get().replace(" ", "")
                for point in cut_str.split(","):
                    cut[self.process_list[self.process_names.index(point.split(":")[0])]] = int(point.split(":")[1])


            points = []

            for p in self.process_list:
                idx = cut.get(p, None)
                if idx is None:
                    continue

                event = self.events_log[p][idx]
                points.extend([event['x'], event['y']])

            consistent = self.is_consistent_cut(cut)

            self.graph_cnv.create_line(
                points,
                fill="green" if consistent else "red",
                width=2,
                dash=(3,2)
            )
        except Exception as e:
            print(e)
            return mb.showerror("Error", f"Error creating the cut")


    def _incrTimestamp(self, process, sender_tmstps=None):
        # define sender_tmstps as sender's timestamps when process RECEIVE message (NOT SEND)
        # sender_tmstps = (lamport_timestamps, vector_timestamps)
        if self.display_vector_tmstps:
            if sender_tmstps:
                for i in range(len(self.process_list)):
                    self.vector_tmstps[process][i] = max(self.vector_tmstps[process][i], sender_tmstps[1][i])
            self.vector_tmstps[process][self.process_list.index(process)] += 1
        else:
            if sender_tmstps:
                self.lamport_tmstps[process] = max(self.lamport_tmstps[process], sender_tmstps[0]) + 1
            else:
                self.lamport_tmstps[process] += 1


    def _getTimestamp(self, process):
        if self.display_vector_tmstps:
            return self.vector_tmstps[process]
        else:
            return self.lamport_tmstps[process]


    def run(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()

    def next_step(self):
        self._step_var.set(self._step_var.get() + 1)

    def toggle_mode(self):
        self.step_mode = not self.step_mode
        self.mode_btn.config(text="Auto" if self.step_mode else "Step-by-step")
        # si on repasse en auto, on débloque tout de suite une éventuelle attente
        if not self.step_mode:
            self.next_step()

    def wait_step(self):
        """Attendre soit un clic Next (mode step), soit un délai (mode auto) sans bloquer l'UI."""
        if self.step_mode:
            self.root.wait_variable(self._step_var)  # bloque mais laisse l'UI active
        else:
            # mode auto: attendre self.timer secondes en gardant l'UI fluide
            done = tk.BooleanVar(value=False)
            self.root.after(int(self.timer * 1000), lambda: done.set(True))
            self.root.wait_variable(done)
