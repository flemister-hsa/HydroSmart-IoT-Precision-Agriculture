import tkinter as tk  # PEP 8 recommends avoiding `import *`.
from tkinter import font
import tkinter.messagebox
from time import gmtime, strftime
import random, pickle, os

class Fullscreen_Window:

    def __init__(self):
        self.tk = tk.Tk()
        self.tk.attributes('-zoomed', True)
        self.frame = tk.Frame(self.tk)
        self.frame.pack()
        self.state = False
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.state = not self.state
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", self.state)
        return "break"

class PopupWindow(tk.Toplevel):

    def __init__(self, parent):
        self.parent = parent
        tk.Toplevel.__init__(self, parent)
        self.withdraw()
        width = 620
        height = 190
        x = self.parent.winfo_rootx() + self.parent.winfo_width()/2 - width/2
        y = self.parent.winfo_rooty() + self.parent.winfo_height()/2 - height/2
        self.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.update_idletasks()
        self.overrideredirect(True)
        self.bind("<FocusOut>", self.close)
        self.bind("<Escape>", self.close)
        self.protocol("WM_DELETE_WINDOW", self.close)

        content = tk.Frame(self)
        content.pack(padx=10, pady=20)
        question = tk.Label(content, text="Would you like to Abort, Pause or Go Back?", font="TkHeadingFont")
        abort = tk.Label(content, text="Abort", font="TkHeadingFont")
        pause = tk.Label(content, text="Pause", font="TkHeadingFont")
        go_back = tk.Label(content, text="Go Back", font="TkHeadingFont")
        abort_text = tk.Label(content, text="stops the program and clears all data")
        pause_text = tk.Label(content, text="stops the program but can be resumed by pressing 'Run'")
        go_back_text = tk.Label(content, text="keeps the program running and cancels the action")

        question.grid(column=0, row=0, columnspan=3, sticky='w')
        abort.grid(column=1, row=1, sticky='e')
        pause.grid(column=1, row=2, sticky='e')
        go_back.grid(column=1, row=3, sticky='e')
        abort_text.grid(column=2, row=1, columnspan=2, sticky='w')
        pause_text.grid(column=2, row=2, columnspan=2, sticky='w')
        go_back_text.grid(column=2, row=3, columnspan=2, sticky='w')

        button_go_back = tk.Button(content, text="Go Back", command=self.close)
        button_go_back.grid(column=0, row=4, pady=20)
        button_pause = tk.Button(content, text="Pause", command=lambda:[pause_program(), self.close()])
        button_pause.grid(column=3, row=4, sticky='e', pady=20)
        button_abort = tk.Button(content, text="Abort", command=lambda:[abort_program(), self.close()])
        button_abort.grid(column=4, row=4, sticky='e', pady=20)
        self.deiconify()

    def close(self, event=None):
        for nav_btn in nav_btns:
            nav_btn.set_state(tk.NORMAL)
        self.parent.focus_set()
        self.destroy()


class CanvasButton:

    def __init__(self, canvas, x, y, display, command, anchor='nw', btn_num=None):
        self.canvas = canvas
        try:
            self.display = tk.PhotoImage(file=display)
        except tk.TclError:
            self.display = display
        # print(type(self.display))
        if isinstance(self.display, str):
            self.button = tk.Button(self.canvas, 
                                    text=self.display) 
        elif isinstance(self.display, tk.PhotoImage):
            self.button = tk.Button(self.canvas, 
                                    image=self.display)
        if btn_num is not None:
            self.button.configure(command=lambda:(command(btn_num)))
        else:
            self.button.configure(command=command)
        self.canvas_btn_obj = canvas.create_window(x, y, anchor=anchor, window=self.button)

    def set_state(self, state):
        self.canvas.itemconfigure(self.canvas_btn_obj, state=state)

class CanvasImageButton:
    """ Create leftmost mouse button clickable canvas image object.

    The x, y coordinates are relative to the top-left corner of the canvas.
    """
    flash_delay = 100  # Milliseconds.

    def __init__(self, canvas, x, y, image_path, command, anchor='nw', btn_num=None, state=tk.NORMAL):
        self.canvas = canvas
        self.btn_image = tk.PhotoImage(file=image_path)
        self.canvas_btn_img_obj = canvas.create_image(x, y, anchor=anchor, state=state,
                                                      image=self.btn_image)
        if btn_num is not None:
            canvas.tag_bind(self.canvas_btn_img_obj, "<ButtonRelease-1>",
                            lambda event: (command(btn_num)))
        else:
            # canvas.tag_bind(self.canvas_btn_img_obj, "<ButtonRelease-1>",
            #                 lambda event: (self.flash(), command()))
            canvas.tag_bind(self.canvas_btn_img_obj, "<ButtonRelease-1>",
                            lambda event: (command()))
    def flash(self):
        self.set_state(tk.HIDDEN)
        self.canvas.after(self.flash_delay, self.set_state, tk.NORMAL)

    def set_state(self, state):
        """ Change canvas button image's state.

        Normally, image objects are created in state tk.NORMAL. Use value
        tk.DISABLED to make it unresponsive to the mouse, or use tk.HIDDEN to
        make it invisible.
        """
        self.canvas.itemconfigure(self.canvas_btn_img_obj, state=state)

class CanvasImage:
    def __init__(self, canvas, x, y, image_path, anchor='nw', state=tk.NORMAL):
        self.canvas = canvas
        self.img = tk.PhotoImage(file=image_path)
        self.canvas_img_obj = canvas.create_image(x, y, anchor=anchor, state=state,
                                                  image=self.img)
    def set_state(self, state):
        self.canvas.itemconfigure(self.canvas_img_obj, state=state)

class CanvasText:
    def __init__(self, canvas, x, y, font, align='nw', text='', state=tk.NORMAL):
        self.canvas = canvas
        self.canvas_txt_obj = canvas.create_text(x, y, anchor=align, font=font, text=text)
        self.bbox = self.canvas.bbox(self.canvas_txt_obj)

    def update_text(self, text):
        self.canvas.itemconfigure(self.canvas_txt_obj, text=text)
        self.bbox = self.canvas.bbox(self.canvas_txt_obj)
        #self.canvas.create_rectangle(self.bbox, outline="blue")

    def move_text_lr(self, x):
        self.canvas.moveto(self.canvas_txt_obj, x, self.bbox[1])

    def update_width(self, width):
        self.canvas.itemconfigure(self.canvas_txt_obj, width=width)
        # self.bbox = self.canvas.bbox(self.canvas_txt_obj)
        # self.canvas.create_rectangle(self.bbox, outline="blue")
        

class CanvasFrame:
    def __init__(self, canvas, x, y, state=tk.NORMAL):
        self.root_canvas = canvas
        self.frame_height = bgr_height-y
        self.frame_width = bgr_width-x
        self.F = tk.Frame(canvas, bg='', height=self.frame_height, width=self.frame_width)
        self.canvas_frame_obj = canvas.create_window(x, y, anchor='nw', state=state, window=self.F)
        self.canvas = tk.Canvas(self.F, bg="white", height=self.frame_height, width=self.frame_width, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0,y=0)
        self.canvas.create_image(self.frame_width, self.frame_height, anchor='se', image=background_img)
    def set_state(self, state):
        self.root_canvas.itemconfigure(self.canvas_frame_obj, state=state)
    def clear(self):
        self.canvas.delete("all")
        self.canvas.create_image(self.frame_width, self.frame_height, anchor='se', image=background_img)

class ActivePlant:
    plants = ["Lettuce", "Basil", "Strawberries"]
    def __init__(self):
        self.name = "None"
        self.start_date = ""
        self.harvest_date = "--/--/----"
        self.running = False
    def set_running(self, value):
        self.running = value
    def load_plant(self, index):
        self.name = self.plants[index]
    def reset(self):
        self.name = "None"
        self.start_date = ""
        self.harvest_date = "--/--/----"
        self.running = False
        

BGR_IMG_PATH = "assets/bg.png"
NAV_BTN_PATHS = ("assets/button-home.png", "assets/button-plant.png", 
                 "assets/button-stats.png", "assets/button-people.png")
HSA_ICON_PATH = "assets/hsa-ico.png"
LED_PATHS = ("assets/led-white.png", "assets/led-green.png", "assets/led-red.png")
CTL_BTN_PATHS = ("assets/button-start.png", "assets/button-abort.png")
PLANT_BTN_PATHS = ('assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png")
# PLANT_BTN_PATHS = ('assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png")

def btn_clicked():
    """ Prints to console a message every time the button is clicked """
    print("Button Clicked")

def nav_clicked(btn):
    nav_btns[btn].flash()
    for display in displays:
        display.set_state(tk.HIDDEN)
    displays[btn].set_state(tk.NORMAL)
    if btn == 3:
        displays[3].clear()
        generate_credits()

def update_status(index, msg):
    for control in controls:
        control.set_state(tk.HIDDEN)
    for led in leds:
        led.set_state(tk.HIDDEN)
    controls[index].set_state(tk.NORMAL)
    leds[index].set_state(tk.NORMAL)
    status_msg.update_text(msg)

def launch_popup():
    for nav_btn in nav_btns:
        nav_btn.set_state(tk.DISABLED)
    popupWindow = PopupWindow(root.tk)
    popupWindow.focus_set()
    
def abort_program():
    os.remove(fname)
    activePlant.reset()
    plant_name.update_text(activePlant.name)
    update_status(0,"No Program Running")

def pause_program():
    activePlant.set_running(False)
    update_status(0,"Program Paused")

def start_program():
    if activePlant.name == "None":
        tk.messagebox.showerror(title="No Plant Selected",
                                message="You must select a plant from the Plants tab")
    else:
        activePlant.set_running(True)
        update_status(1,"All Systems Normal")

def update_time():
    string_time = strftime('%H:%M ')
    digital_clock.update_text(string_time)
    str_weekday = strftime('%A')
    padded = str_weekday.center(8)
    weekday.update_text(padded)
    str_month = strftime('%m/ ')
    month.update_text(str_month)
    month.move_text_lr(weekday.bbox[0])
    str_day = strftime('%d')
    day.update_text(str_day)
    str_year = strftime('/%y')
    year.update_text(str_year)
    year.move_text_lr(weekday.bbox[2]-year.bbox[2]+year.bbox[0]-5)
 
def update_home():
    update_time()
    if activePlant.running:
        controls[1].set_state(tk.NORMAL)
    else:
        controls[0].set_state(tk.NORMAL)

    displays[0].canvas.after(1000, update_home)

def generate_credits():
    random.shuffle(students)
    CanvasText(displays[3].canvas, 350, 0, h[3], 'n', "HSA Engineering 2026 Graduating Class")
    num_col = 3
    while len(students) % num_col != 0:
        students.append("")
    for i in range(num_col):
        num_row = int(len(students)/num_col)
        for j in range(num_row):
            txt = students[j+i*num_row]
            if txt != "":
                txt = "\u2022 " + txt
            CanvasText(displays[3].canvas, 30+i*200, 35*j+40, h[3], 'nw', txt)
    txt = gen_str("Instructor", instructors)
    CanvasText(displays[3].canvas, 30, 35*int(len(students)/num_col+1)+20, h[3], 'nw', txt)
    txt = gen_str("Advisor", advisors)
    CanvasText(displays[3].canvas, 30, 35*int(len(students)/num_col+2)+20, h[3], 'nw', txt)
    txt = gen_str("Special Thank", sponsors)
    thanks = CanvasText(displays[3].canvas, 30, 35*int(len(students)/num_col+3)+40, h[4], 'nw', txt)
    thanks.update_width(600)

def gen_str(start, elements):
    txt = start
    num_elements = len(elements)
    if num_elements > 1:
        txt = txt + "s: "
    else:
        txt = txt + ": "
    for i in range(num_elements):
        txt = txt + elements[i]
        if i < num_elements - 1:
            txt = txt + ", "
    return txt

def load_plant(num):
    activePlant.load_plant(num)
    plant_name.update_text(activePlant.name)
    with open(fname, "wb") as fout:
        pickle.dump(activePlant, fout)

fname = "plant_bkup.pkl"
try:
    with open(fname, "rb") as fin:
        activePlant = pickle.load(fin)
except FileNotFoundError:
    activePlant = ActivePlant()
#activePlant = ActivePlant()

# root = tk.Tk()
root = Fullscreen_Window()


background_img = tk.PhotoImage(file=BGR_IMG_PATH)
bgr_width, bgr_height = background_img.width(), background_img.height()

root.tk.geometry(f'{bgr_width}x{bgr_height}')
root.tk.title("Hydro-Smart")
root.tk.configure(bg="white")

bg_canvas = tk.Canvas(root.tk, bg="white", height=bgr_height, width=bgr_width, bd=0, highlightthickness=0, relief="ridge")
bg_canvas.place(x=0, y=0)
background = bg_canvas.create_image(0, 0, anchor='nw', image=background_img)

font_sizes = (120, 64, 40, 24, 16)
h = []
for i in range(len(font_sizes)):
    h.append(("Blank River", font_sizes[i]))

nav_btns = []
displays = []
for i in range(0, len(NAV_BTN_PATHS)):
    nav_btns.append(CanvasImageButton(bg_canvas, 0, i*120, NAV_BTN_PATHS[i], nav_clicked, 'nw', i))
    displays.append(CanvasFrame(bg_canvas, 100, 120, tk.HIDDEN))

canvas_icon = CanvasImage(bg_canvas, 780, 15, HSA_ICON_PATH, 'ne')
CanvasText(bg_canvas, 400, 0, h[1], 'n', "Hydro-Smart")

# Home Display
digital_clock = CanvasText(displays[0].canvas, 310, -40, h[0],'n')
weekday = CanvasText(displays[0].canvas, 80, 0, h[3], 'n')
month = CanvasText(displays[0].canvas, 0, 37, h[4])
day = CanvasText(displays[0].canvas, 80, 25, h[1], 'n')
year = CanvasText(displays[0].canvas, 0, 95, h[4])
CanvasText(displays[0].canvas, 670, 0, h[4], 'ne', "Current Plant:")
plant_name = CanvasText(displays[0].canvas, 670, 25, h[2],  'ne', activePlant.name)
CanvasText(displays[0].canvas, 20, 155, h[2], 'w', "Estimated Harvest Date:")
harvest_date = CanvasText(displays[0].canvas, 400, 205, h[2], 'w', activePlant.harvest_date)
CanvasText(displays[0].canvas, 20, 260, h[3], 'nw', "Status:")
leds = []
for i in range(0, len(LED_PATHS)):
    leds.append(CanvasImage(displays[0].canvas, 60, 300, LED_PATHS[i], 'w', tk.HIDDEN))
leds[0].set_state(tk.NORMAL)
status_msg = CanvasText(displays[0].canvas, 200, 300, h[3], "w", "No Program Running")
controls = []
ctl_cmds = (start_program, launch_popup)
for i in range(0, len(CTL_BTN_PATHS)):
    controls.append(CanvasButton(displays[0].canvas, 600, 300, CTL_BTN_PATHS[i], ctl_cmds[i], 'center'))
pause_program()
update_home()

# Plants Display
# canvas_btn_plant2 = CanvasImageButton(displays[1].canvas, 0, 0, NAV_BTN_PATHS[1], btn_clicked)
max_btns = 4
plant_buttons = []
for i in range(len(activePlant.plants)):
    plant_buttons.append(CanvasButton(displays[1].canvas, (i%max_btns)*175+80, int(i/max_btns)*150, PLANT_BTN_PATHS[i], load_plant, 'n', i))
    # plant_buttons.append(CanvasButton(displays[1].canvas, (i%max_btns)*175, int(i/max_btns) * 150, "Click Me", btn_clicked))
    CanvasText(displays[1].canvas, (i%max_btns)*175+80, int(i/max_btns)*150+110, h[3], 'n', activePlant.plants[i])
# Stats Display

# Credits Display
students = ["Hajr Abdullah", "Amelia Allison", "Foday Lamboi", "Cedrick Abotchi", "Brandon Jimenez-Martinez", "Caleb Kolie", "Abdul Bayoh", "Ryan Shoults", "Abdimalik Mire", "Zack Abdullahi", "Salmaan Mosa", "Mohammed Ali"]
instructors = ["Dorma Flemister"]
advisors = ["Savas Kaya", "John Hribar"]
sponsors = ["The Ohio State University", "Ohio University", "SenseICs", "Smarty Pants Consulting", "Horizon Science Academy"]
generate_credits()
# Start from Home
displays[0].set_state(tk.NORMAL)

root.tk.resizable(False, False)
root.tk.mainloop()
