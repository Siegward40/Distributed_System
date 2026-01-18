import tkinter as tk

class Visualizer:

    width = 1600
    height = 800

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chandy-Lamport Algorithm")
        self.root.geometry(f"{Visualizer.width}x{Visualizer.height}")
        self.graph_cnv = tk.Canvas(self.root, width=0.9*Visualizer.width, height=0.8*Visualizer.height, bg="white")
        self.graph_cnv.pack(padx=0.05*Visualizer.width, pady=0.1*Visualizer.height)

    def add_all_proccess(self, all_process:dict):
        """Parameter is a dictionary of all process with identifier of process as key and its name as value (label)"""
        nb_p = len(all_process)
        w = int(self.graph_cnv['width'])
        h = int(self.graph_cnv['height'])
        x_start = 0.1 * w
        x_end = 0.95 * w
        for i, (k, v) in enumerate(all_process.items()):
            y = (i+0.5)/nb_p * h
            self.graph_cnv.create_text(0.07 * w, y, text=v, fill ="black", font="Arial 20 bold")
            self.graph_cnv.create_line((x_start,y), (x_end,y), width=4, arrow='last')

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    visualizer = Visualizer()
    #visualizer.add_all_proccess({1:"P1", 2:"P2", 3:"P3"})
    visualizer.add_all_proccess({1:"P1", 2:"P2", 3:"P3", 4:"P4"})
    visualizer.run()