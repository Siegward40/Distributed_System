import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb


class Terminal:
    """A simple Tkinter interface (terminal) for creating a set of processes and assigning tasks to them before viewing Global States and Distributed Snapshots."""

    def __init__(self):
        self.processes_list = []
        self.processes_trace = {}
        self.clock_type = ""

        self.root = tk.Tk()
        self.root.title("Terminal")
        self.root.geometry("1000x800")

        instructions = tk.Canvas(self.root, width=1000, height=250)
        instructions.create_text(500, 30, text="Define your system", fill ="black", font="Arial 18 bold", anchor="center")
        instructions.create_text(500, 70, text="On line 1, define the type of clocks used:  use [lamport OR vector]", font="Arial 10")
        instructions.create_text(500, 100, text="On line 2, define process names separated by commas", font="Arial 10")
        instructions.create_text(500, 130, text="On next lines define process tasks separated by commas:  [PROCESS]: [TASK 1], [TASK 2], ...", font="Arial 10")
        instructions.create_text(500, 155, text="• For a simple computation:  [TIME] compute", font="Arial 10")
        instructions.create_text(500, 180, text="• For sending a message :  [TIME] send [PROCESS] [MESSAGE]", font="Arial 10")
        instructions.create_text(500, 205, text="⚠ [TIME] must be an integer, it represents the moment and the order of events", font="Arial 10")
        instructions.create_text(500, 230, text="⚠ [PROCESS] must be declared on line 2", font="Arial 10")
        instructions.pack()

        self.terminal = tk.Text(self.root, font="Courier 10", bg="black", fg="white", insertbackground="white")
        self.terminal.pack()
        try: self.loadFile("default_terminal")
        except: pass

        buttons = tk.Frame()
        buttons.pack()
        tk.Button(buttons, text="Load", command=self.loadFile, padx=20).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(buttons, text="Export", command=self.exportFile, padx=20).grid(row=0, column=1, padx=10, pady=10)
        tk.Button(buttons, text="Execute", command=self.execute, padx=20).grid(row=0, column=2, padx=10, pady=10)

        self.root.mainloop()


    def execute(self):
        processes = {}
        processes_list = []
        clock_type = ""
        lines = self.terminal.get("1.0", "end").split("\n")[:-1]

        if len(lines) < 2:
            return mb.showerror("Error", "Minimum of 2 lines is required")

        # line 1: get type of clocks
        line1 = lines[0].split(" ")
        if len(line1)==2 and line1[0] == "use" and line1[1] in ["lamport","vector"]:
            clock_type = line1[1]
        else:
            return mb.showerror("Error", "Error on line 1")

        # line 2: get processes
        line2 = lines[1].replace(" ", "").split(",")
        if len(line2) > 0 and line2[0] != "":
            for p in line2:
                processes[p] = []
                processes_list.append(p)
        else:
            return mb.showerror("Error", "Error on line 2")

        # next lines : process tasks
        for i, line in enumerate(lines[2:]):
            try:
                separate = line.split(":")
                process = separate[0].replace(" ", "")
                if process in processes:
                    tasks = separate[1].split(",")
                    for task in tasks:
                        task = task[1:] if task[0] == " " else task
                        elements = task.split(" ")
                        t = int(elements[0])
                        action = elements[1]
                        if action == "compute":
                            processes[process].append( (t, ('compute',)) )
                        elif action == "send":
                            receiver = elements[2]
                            message = elements[3]
                            if receiver not in processes:
                                return mb.showerror("Error", f"Error on line {i+3}: undefined process '{receiver}'")
                            processes[process].append( (t, ('send', processes_list.index(receiver)+1, message)) )
                            # receiver transform to index+1 -> see declaration of processes in main module
                        else:
                            return mb.showerror("Error", f"Error on line {i+3}: unknown action '{action}'")
                else:
                    return mb.showerror("Error", f"Error on line {i+3}: undefined process '{process}'")
            except Exception as e:
                print(e)
                return mb.showerror("Error", f"Error on line {i+3}")

        self.processes_list = processes_list
        self.processes_trace = processes
        self.clock_type = clock_type

        self.root.destroy()


    def loadFile(self, filepath=None):
        if filepath is None:
            filepath = fd.askopenfilename()
        with open(filepath) as file:
            content = file.read()
            self.terminal.delete("1.0", tk.END)
            self.terminal.insert("1.0", content)


    def exportFile(self):
        filepath = fd.asksaveasfilename()
        with open(filepath, 'w') as file:
            content = self.terminal.get("1.0", "end")
            file.write(content)


# On line 1, define the type of clocks used: use [lamport OR vector]
# On line 2, define process names separated by commas
# On next lines (one per process in order), define process tasks with times and separated by commas
    # For a simple computation: [TIME] compute
    # For sending a message : [TIME] send [PROCESS] [MESSAGE]
    # [TIME] must be an integer and [PROCESS] must be declared on line 2

# Sample:
# use lamport
# P1,P2,P3,P4
# P1: 1 compute, 3 send P2 msg1, 5 compute, 7 send P3 msg1
# P2: 2 compute, 4 send P3 msg3, 6 compute, 8 send P4 msg4
# P3: 3 compute, 5 send P4 msg5
# P4: 4 compute, 6 send P1 msg6
