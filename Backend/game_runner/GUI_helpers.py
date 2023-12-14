from tkinter import *
from tkinter import ttk

# Takes in: root node. Attach a scrollable frame to it
# show_frame is where you put in elements to display
# using a grid system
class VSF:
    def __init__(self, master, rowid, cid):
        # Create A Main Frame
        self.frame = Frame(master)
        self.frame.grid(row=rowid, column=cid, padx=2, pady=2)
        # Create A Canvas
        self.canvas = Canvas(self.frame)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        # Add A Scrollbar To The Canvas
        self.scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        # Configure The Canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # Create ANOTHER Frame INSIDE the Canvas
        self.show_frame = Frame(self.canvas)
        # Add that New Frame To a Window In The Canvas
        self.canvas.create_window((0, 0), window=self.show_frame, anchor="nw")

class VSFL:
    def __init__(self, master, rowid, cid):
        # Create A Main Frame
        self.frame = Frame(master)
        self.frame.grid(row=rowid, column=cid, padx=2, pady=2)
        # Create A Canvas
        self.canvas = Canvas(self.frame)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        # Add A Scrollbar To The Canvas
        self.scrollbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=LEFT, fill=Y)
        # Configure The Canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # Create ANOTHER Frame INSIDE the Canvas
        self.show_frame = Frame(self.canvas)
        # Add that New Frame To a Window In The Canvas
        self.canvas.create_window((0, 0), window=self.show_frame, anchor="nw")

class HSF:
    def __init__(self, master, rowid, cid):
        # Create A Main Frame
        self.frame = Frame(master)
        self.frame.grid(row=rowid, column=cid, padx=2, pady=2)
        # Create A Canvas
        self.canvas = Canvas(self.frame)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
        # Add A Scrollbar To The Canvas
        self.scrollbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.canvas.xview)
        self.scrollbar.pack(side=LEFT, fill=X)
        # Configure The Canvas
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        # Create ANOTHER Frame INSIDE the Canvas
        self.show_frame = Frame(self.canvas)
        # Add that New Frame To a Window In The Canvas
        self.canvas.create_window((0, 0), window=self.show_frame, anchor="nw")