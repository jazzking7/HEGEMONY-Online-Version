from tkinter import *
from PIL import Image, ImageTk

# CAUTION! Tkinter does not save image instances
# All images need to be saved explicitly otherwise it won't show!

root = Tk()
root.title("MAP VISUALIZE")
root.geometry('2550x1400')

# The content need to be physically stored.
physical_images = []
# Canvas will return an unique ID for each content. Removing the ID will remove the image
# Even more interesting: if you remove the ID, canvas will still continue to increment from where you left out.
# I'm scared of ID overflow, so I will delete the canvas and make a new one everytime I refresh
unique_IDs = []
texts = []

lock_physical_images = []
lock_IDs = []

Map = PhotoImage(file="visual_assets/MAP/mapc.png")
canvas = Canvas(root, width=2550, height=1400)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=Map, anchor='nw')

sn = Toplevel()
Label(sn, text="x").grid(row=0, column=0)
ex = Entry(sn)
ex.grid(row=1, column=0)
Label(sn, text="y").grid(row=2, column=0)
ey = Entry(sn)
ey.grid(row=3, column=0)

c1 = LabelFrame(sn, text="Insignia")
c1.grid(row=9, column=0)
c2 = LabelFrame(sn, text="Capital")
c2.grid(row=9, column=1)
c3 = LabelFrame(sn, text="City")
c3.grid(row=10, column=0)
c4 = LabelFrame(sn, text="Text")
c4.grid(row=10, column=1)

class locator:

    def __init__(self, filename):
        self.x = 0
        self.y = 0
        self.file_name = filename
        self.curr = None
        self.curr_id = None

    def show_coordinates(self):
        ex.delete(0, END)
        ex.insert(0, self.x)
        ey.delete(0, END)
        ey.insert(0, self.y)

class text_locator:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.curr = None
        self.curr_id = None

    def show_coordinates(self):
        ex.delete(0, END)
        ex.insert(0, self.x)
        ey.delete(0, END)
        ey.insert(0, self.y)

locator1 = locator("visual_assets/INSIGNIAS/insignia1.PNG")
locator2 = locator("visual_assets/CAPITALS/capital1.PNG")
locator3 = locator("visual_assets/LOGOS/city.png")
locator4 = text_locator()

def up(loca):
    loca.y -= 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(ix.get()), int(iy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    locator1.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=locator1.curr, anchor='nw')
    locator1.curr_id = new_img
    loca.show_coordinates()

def down(loca):
    loca.y += 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(ix.get()), int(iy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    locator1.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=locator1.curr, anchor='nw')
    locator1.curr_id = new_img
    loca.show_coordinates()

def left(loca):
    loca.x -= 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(ix.get()), int(iy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    locator1.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=locator1.curr, anchor='nw')
    locator1.curr_id = new_img
    loca.show_coordinates()

def right(loca):
    loca.x += 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(ix.get()), int(iy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.curr_insig_id = new_img
    loca.show_coordinates()

#

def upca(loca):
    loca.y -= 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cax.get()), int(cay.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.curr_insig_id = new_img
    loca.show_coordinates()

def downca(loca):
    loca.y += 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cax.get()), int(cay.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.curr_insig_id = new_img
    loca.show_coordinates()

def leftca(loca):
    loca.x -= 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cax.get()), int(cay.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.curr_insig_id = new_img
    loca.show_coordinates()

def rightca(loca):
    loca.x += 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cax.get()), int(cay.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.curr_insig_id = new_img
    loca.show_coordinates()

#

def upc(loca):
    loca.y -= 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cx.get()), int(cy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.show_coordinates()

def downc(loca):
    loca.y += 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cx.get()), int(cy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.show_coordinates()

def leftc(loca):
    loca.x -= 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cx.get()), int(cy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.show_coordinates()

def rightc(loca):
    loca.x += 1
    new_img = Image.open(loca.file_name)
    new_img = new_img.resize((int(cx.get()), int(cy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    loca.curr = new_img
    new_img = canvas.create_image(loca.x, loca.y, image=loca.curr, anchor='nw')
    loca.show_coordinates()

#

def upt(loca):
    loca.y -= 1
    canvas.delete(locator4.curr)
    canvas.delete(locator4.curr_id)
    text = canvas.create_text(loca.x, loca.y, text="999", font=("Helvetica", font.get()))
    locator4.curr = text
    locator4.curr_id = text
    loca.show_coordinates()

def downt(loca):
    loca.y += 1
    canvas.delete(locator4.curr)
    canvas.delete(locator4.curr_id)
    text = canvas.create_text(loca.x, loca.y, text="999", font=("Helvetica", font.get()))
    locator4.curr = text
    locator4.curr_id = text
    loca.show_coordinates()


def leftt(loca):
    loca.x -= 1
    canvas.delete(locator4.curr)
    canvas.delete(locator4.curr_id)
    text = canvas.create_text(loca.x, loca.y, text="999", font=("Helvetica", font.get()))
    locator4.curr = text
    locator4.curr_id = text
    loca.show_coordinates()


def rightt(loca):
    loca.x += 1
    canvas.delete(locator4.curr)
    canvas.delete(locator4.curr_id)
    text = canvas.create_text(loca.x, loca.y, text="999", font=("Helvetica", font.get()))
    locator4.curr = text
    locator4.curr_id = text
    loca.show_coordinates()

#

def add_locator1(locator1):
    x = int(ex.get())
    y = int(ey.get())
    new_img = Image.open(locator1.file_name)
    new_img = new_img.resize((int(ix.get()), int(iy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    locator1.x = x
    locator1.y = y
    locator1.curr = new_img
    new_img = canvas.create_image(x, y, image=locator1.curr, anchor='nw')
    locator1.curr_insig_id = new_img
    Button(c1, text="UP", command=lambda: up(locator1)).grid(row=0, column=1)
    Button(c1, text="DOWN", command=lambda: down(locator1)).grid(row=2, column=1)
    Button(c1, text="LEFT", command=lambda: left(locator1)).grid(row=1, column=0)
    Button(c1, text="RIGHT", command=lambda: right(locator1)).grid(row=1, column=2)

def add_locator2(locator2):
    x = int(ex.get())
    y = int(ey.get())
    new_img = Image.open(locator2.file_name)
    new_img = new_img.resize((int(cax.get()), int(cay.get())))
    new_img = ImageTk.PhotoImage(new_img)
    locator2.x = x
    locator2.y = y
    locator2.curr = new_img
    new_img = canvas.create_image(x, y, image=locator2.curr, anchor='nw')
    locator2.curr_insig_id = new_img
    Button(c2, text="UP", command=lambda: upca(locator2)).grid(row=0, column=1)
    Button(c2, text="DOWN", command=lambda: downca(locator2)).grid(row=2, column=1)
    Button(c2, text="LEFT", command=lambda: leftca(locator2)).grid(row=1, column=0)
    Button(c2, text="RIGHT", command=lambda: rightca(locator2)).grid(row=1, column=2)

def add_locator3(locator3):
    x = int(ex.get())
    y = int(ey.get())
    new_img = Image.open(locator3.file_name)
    new_img = new_img.resize((int(cx.get()), int(cy.get())))
    new_img = ImageTk.PhotoImage(new_img)
    locator3.x = x
    locator3.y = y
    locator3.curr = new_img
    new_img = canvas.create_image(x, y, image=locator3.curr, anchor='nw')
    locator2.curr_id = new_img
    Button(c3, text="UP", command=lambda: upc(locator3)).grid(row=0, column=1)
    Button(c3, text="DOWN", command=lambda: downc(locator3)).grid(row=2, column=1)
    Button(c3, text="LEFT", command=lambda: leftc(locator3)).grid(row=1, column=0)
    Button(c3, text="RIGHT", command=lambda: rightc(locator3)).grid(row=1, column=2)

def add_locator4(locator4):
    x = int(ex.get())
    y = int(ey.get())
    locator4.x = x
    locator4.y = y
    canvas.delete(locator4.curr)

    text = canvas.create_text(x, y, text="999", font=("Comic Sans MS", font.get()))
    locator4.curr = text
    Button(c4, text="UP", command=lambda: upt(locator4)).grid(row=0, column=1)
    Button(c4, text="DOWN", command=lambda: downt(locator4)).grid(row=2, column=1)
    Button(c4, text="LEFT", command=lambda: leftt(locator4)).grid(row=1, column=0)
    Button(c4, text="RIGHT", command=lambda: rightt(locator4)).grid(row=1, column=2)
    locator4.show_coordinates()

def lock():
    locas = [locator1, locator2, locator3, locator4]
    for loca in locas:
        if loca.curr_id not in lock_IDs:
            lock_IDs.append(loca.curr_id )
        if loca.curr not in lock_physical_images:
            lock_physical_images.append(loca.curr)
    return

Button(sn, text="Show Insignia", command=lambda: add_locator1(locator1)).grid(row=4, column=0)
Button(sn, text="Show Capital", command=lambda: add_locator2(locator2)).grid(row=5, column=0)
Button(sn, text="Show City", command=lambda: add_locator3(locator3)).grid(row=6, column=0)
Button(sn, text="Show Text", command=lambda: add_locator4(locator4)).grid(row=7, column=0)
Button(sn, text="Lock", command=lock).grid(row=8, column=0)

ix = Entry(sn)
ix.grid(row=4, column=1)
iy = Entry(sn)
iy.grid(row=4, column=2)

cax = Entry(sn)
cax.grid(row=5, column=1)
cay = Entry(sn)
cay.grid(row=5, column=2)

cx = Entry(sn)
cx.grid(row=6, column=1)
cy = Entry(sn)
cy.grid(row=6, column=2)

font = Entry(sn)
font.grid(row=7, column=1)

root.mainloop()

