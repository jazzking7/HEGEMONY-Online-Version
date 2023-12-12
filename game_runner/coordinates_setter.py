from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.title("MAP VISUALIZE")
root.geometry('2550x1400')

panel = Toplevel()
panel.geometry("500x500")

# coordinates
coords = LabelFrame(panel, text="Coordinates")
coords.grid(row=0, column=0, padx=2, pady=2)
coord = Label(coords, text="")
coord.pack(pady=20)
x_e = Entry(coords)
x_e.pack()
y_e = Entry(coords)
y_e.pack()

# image choices:
imgs = LabelFrame(panel, text="Type of image")
imgs.grid(row=0, column=1, padx=2, pady=2)
img_type = StringVar(value=" ")
Radiobutton(imgs, variable=img_type, value="visual_assets/RADIOACTIVE/radioactive.PNG", text="insignia").pack()
Radiobutton(imgs, variable=img_type, value="visual_assets/CAPITALS/capital8.PNG", text="capital").pack()
Radiobutton(imgs, variable=img_type, value="visual_assets/LOGOS/city.png", text="city").pack()

# dimension of the images
dims = LabelFrame(panel, text="Dimension")
dims.grid(row=1, column=0, padx=2, pady=2)
dimx = Entry(dims)
dimx.pack()
dimy = Entry(dims)
dimy.pack()

def show_text():
    t_locator.x = int(tx.get())
    t_locator.y = int(ty.get())
    text = canvas.create_text(t_locator.x, t_locator.y, text="999", font=("Helvetica", font.get()))
    t_locator.curr_id = text
    t_locator.show_coordinates()

def copy_coor():
    tx.delete(0, END)
    tx.insert(0, x_e.get())
    ty.delete(0, END)
    ty.insert(0, y_e.get())

# set text
texts = LabelFrame(panel, text="Troop amount")
texts.grid(row=2, column=0, padx=2, pady=2)
tx = Entry(texts)
tx.pack()
ty = Entry(texts)
ty.pack()
font = Entry(texts)
font.pack()
Button(texts, text="Copy Coordinates", command=copy_coor).pack()
Button(texts, text="Show", command=show_text).pack()

class Text_locator:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.curr_id = None

    def show_coordinates(self):
        tx.delete(0, END)
        tx.insert(0, self.x)
        ty.delete(0, END)
        ty.insert(0, self.y)

t_locator = Text_locator()

# display map
Map = PhotoImage(file="visual_assets/MAP/mapc.png")
canvas = Canvas(root, width=2550, height=1400)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=Map, anchor='nw')

temp_storage = []

def lock():
    lock_images.append(temp_storage[0])

def write_data():
    file = open("trty_radio_active_site.txt", "a")
    file.write(f"{x_e.get()},{y_e.get()},{dimx.get()}x{dimy.get()}\n")
    file.close()

def write_text():
    file = open("trty_radio_active_site.txt", "a")
    file.write(f"{tx.get()},{ty.get()},{font.get()}\n")
    file.close()

def write_name():
    file = open("trty_radio_active_site.txt", "a")
    file.write(f"{name.get()}\n")
    file.close()

def move(e):
    temp_storage.clear()
    insig = Image.open(img_type.get())
    insig = insig.resize((int(dimx.get()), int(dimy.get())))
    insig = ImageTk.PhotoImage(insig)
    temp_storage.append(insig)
    canvas.create_image(e.x, e.y, image=insig, anchor='nw')
    coord.config(text=f"x: {str(e.x)}  y: {str(e.y)}")
    x_e.delete(0, END)
    x_e.insert(0, e.x)
    y_e.delete(0, END)
    y_e.insert(0, e.y)
    return

canvas.bind('<B1-Motion>', move)

lock_images = []

# info_saver
infos = LabelFrame(panel, text="Save data")
infos.grid(row=1, column=1, padx=2, pady=2)
Label(infos, text="Name").pack()
name = Entry(infos)
name.pack()
Button(infos, text="Lock Image", command=lock).pack()
Button(infos, text="Write data", command=write_data).pack()
Button(infos, text="Write text data", command=write_text).pack()
Button(infos, text="Write name", command=write_name).pack()

def left(e):
    t_locator.x -= 1
    canvas.delete(t_locator.curr_id)
    text = canvas.create_text(t_locator.x, t_locator.y, text="999", font=("Helvetica", font.get()))
    t_locator.curr_id = text
    t_locator.show_coordinates()

def right(e):
    t_locator.x += 1
    canvas.delete(t_locator.curr_id)
    text = canvas.create_text(t_locator.x, t_locator.y, text="999", font=("Helvetica", font.get()))
    t_locator.curr_id = text
    t_locator.show_coordinates()

def up(e):
    t_locator.y -= 1
    canvas.delete(t_locator.curr_id)
    text = canvas.create_text(t_locator.x, t_locator.y, text="999", font=("Helvetica", font.get()))
    t_locator.curr_id = text
    t_locator.show_coordinates()

def down(e):
    t_locator.y += 1
    canvas.delete(t_locator.curr_id)
    text = canvas.create_text(t_locator.x, t_locator.y, text="999", font=("Helvetica", font.get()))
    t_locator.curr_id = text
    t_locator.show_coordinates()

root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<Up>", up)
root.bind("<Down>", down)

root.mainloop()