import tkinter as tk  # PEP 8 recommends avoiding `import *`.
from tkinter import font
import tkinter.messagebox
from time import gmtime, strftime
import random, pickle, os, sys

class Plant():
    tolerance = 0.1
    def __init__(self, name, pH_min, pH_max, ec_min, ec_max,cf_min, 
                 cf_max, ppm700_min, ppm700_max, ppm500_min, ppm500_max):
        self.name = name
        self.pH_min = pH_min
        self.pH_max = pH_max
        self.ec_min = ec_min
        self.ec_max = ec_max
        self.cf_min = cf_min
        self.cf_max = cf_max
        self.ppm700_min = ppm700_min
        self.ppm700_max = ppm700_max
        self.ppm500_min = ppm500_min
        self.ppm500_max = ppm500_max

class ActivePlant(Plant):
    available_plants = ["Lettuce", "Basil", "Strawberries"]
    # available_plants = ["Lettuce", "Bazsil", "Strawberries", "Lettuce", "Basil", "Strawberries", "Lettuce", "Basil", "Strawberries", "Lettuce", "Basil", "Strawberries", "Lettuce", "Basil", "Strawberries", "Lettuce", "Basil", "Strawberries", "Lettuce", "Basil", "Strawberries", "Lettuce", "Basil", "Strawberries"]
    available_indices = []
    # def __init__(self, name='None', pH_min=0, pH_max=0, ec_min=0, ec_max=0,cf_min=0, 
    #              cf_max=0, ppm700_min=0, ppm700_max=0, ppm500_min=0, ppm500_max=0):
    def __init__(self, plant):
        super().__init__(plant.name, plant.pH_min, plant.pH_max, plant.ec_min, plant.ec_max, plant.cf_min, plant.cf_max, plant.ppm700_min, plant.ppm700_max, plant.ppm500_min, plant.ppm500_max)
        self.harvest_date = "--/--/----"
        self.running = False
        self.error = False
        self.error_msg = "Error"
    def set_running(self, value):
        self.running = value
    def index_available(self):
        for available_plant in self.available_plants:
            self.find_indices(available_plant)
        print(self.available_indices)
    def find_indices(self, available_plant):
        # my_filter = filter(lambda x: x[1].name == available_plant, enumerate(plantDB))
        #print(next(my_filter)[0])
        #self.available_indices.append(next(my_filter)[0])
        #print(next(filter(lambda x: x[1].name == 'joe', enumerate(Test.all_objects)))[0], 'Not Found')
        try:
            self.available_indices.append(next(filter(lambda x: x[1].name == available_plant, enumerate(plantDB)))[0])
        except StopIteration:
            self.available_indices.append(-1)

class Fullscreen_Window:

    def __init__(self):
        self.tk = tk.Tk()
        self.tk.attributes('-zoomed', True)
        self.frame = tk.Frame(self.tk)
        self.frame.pack()
        self.state = False
        self.tk.attributes("-fullscreen", self.state)
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

    def __init__(self, canvas, x, y, display, command, anchor='nw', 
                 btn_num=None, state=tk.NORMAL):
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
        self.canvas_btn_obj = canvas.create_window(x, y, anchor=anchor, 
                                                   window=self.button)
        self.set_state(state)

    def set_state(self, state):
        self.canvas.itemconfigure(self.canvas_btn_obj, state=state)

class CanvasImageButton:
    """ Create leftmost mouse button clickable canvas image object.

    The x, y coordinates are relative to the top-left corner of the canvas.
    """
    flash_delay = 100  # Milliseconds.

    def __init__(self, canvas, x, y, image_path, command, anchor='nw', 
                 btn_num=None, state=tk.NORMAL):
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
        self.set_state(state)
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
        self.set_state(state)
        # self.bbox = self.canvas.bbox(self.canvas_img_obj)
        # self.canvas.create_rectangle(self.bbox, outline="blue")
    def set_state(self, state):
        self.canvas.itemconfigure(self.canvas_img_obj, state=state)

class CanvasText:
    def __init__(self, canvas, x, y, font, align='nw', text='', state=tk.NORMAL):
        self.canvas = canvas
        self.canvas_txt_obj = canvas.create_text(x, y, anchor=align, 
                                                 font=font, text=text)
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
        self.F = tk.Frame(canvas, bg='', height=self.frame_height, 
                          width=self.frame_width)
        self.canvas_frame_obj = canvas.create_window(x, y, anchor='nw', 
                                                     state=state, window=self.F)
        self.canvas = tk.Canvas(self.F, bg="white", height=self.frame_height, 
                                width=self.frame_width, bd=0, highlightthickness=0, 
                                relief="ridge")
        self.canvas.place(x=0,y=0)
        self.canvas.create_image(self.frame_width, self.frame_height, 
                                 anchor='se', image=background_img)
        self.set_state(state)
    def set_state(self, state):
        self.root_canvas.itemconfigure(self.canvas_frame_obj, state=state)
    def clear(self):
        self.canvas.delete("all")
        self.canvas.create_image(self.frame_width, self.frame_height, 
                                 anchor='se', image=background_img)

class HomeScreen:
    def __init__(self, display, led_paths, ctl_btn_paths):
        self.display = display
        self.led_paths = led_paths
        self.ctl_btn_paths = ctl_btn_paths
        self.digital_clock = CanvasText(self.display.canvas, 310, -40, h[0],'n')
        self.weekday = CanvasText(self.display.canvas, 80, 0, h[3], 'n')
        self.month = CanvasText(self.display.canvas, 0, 37, h[4])
        self.day = CanvasText(self.display.canvas, 80, 25, h[1], 'n')
        self.year = CanvasText(self.display.canvas, 0, 95, h[4])
        CanvasText(self.display.canvas, 670, 0, h[4], 'ne', "Current Plant:")
        self.plant_name = CanvasText(self.display.canvas, 670, 25, h[2],
                                     'ne', activePlant.name)
        CanvasText(self.display.canvas, 20, 155, h[2], 'w', "Estimated Harvest Date:")
        self.harvest_date = CanvasText(self.display.canvas, 400, 205, h[2], 
                                       'w', activePlant.harvest_date)
        CanvasText(self.display.canvas, 20, 260, h[3], 'nw', "Status:")
        self.leds = []
        for i in range(0, len(self.led_paths)):
            self.leds.append(CanvasImage(self.display.canvas, 60, 300, 
                                         self.led_paths[i], 'w', tk.HIDDEN))
        self.leds[0].set_state(tk.NORMAL)
        self.status_msg = CanvasText(self.display.canvas, 200, 300, h[3], 
                                     "w", "No Program Running")
        self.controls = []
        self.ctl_cmds = (start_program, launch_popup)
        for i in range(0, len(ctl_btn_paths)):
            self.controls.append(CanvasButton(self.display.canvas, 600, 300, 
                                              self.ctl_btn_paths[i], self.ctl_cmds[i],
                                              'center', None, tk.HIDDEN))
        self.controls[0].set_state(tk.NORMAL)
        self.update_home()

    def update_time(self):
        string_time = strftime('%H:%M ')
        self.digital_clock.update_text(string_time)
        str_weekday = strftime('%A')
        padded = str_weekday.center(8)
        self.weekday.update_text(padded)
        str_month = strftime('%m/ ')
        self.month.update_text(str_month)
        self.month.move_text_lr(self.weekday.bbox[0])
        str_day = strftime('%d')
        self.day.update_text(str_day)
        str_year = strftime('/%y')
        self.year.update_text(str_year)
        self.year.move_text_lr(self.weekday.bbox[2]-self.year.bbox[2]+
                               self.year.bbox[0]-3)
     
    def update_home(self):
        self.update_time()
        if activePlant.running:
            self.controls[1].set_state(tk.NORMAL)
        else:
            self.controls[0].set_state(tk.NORMAL)
    
        self.display.canvas.after(1000, self.update_home)

    def update_status(self, index, msg):
        for control in self.controls:
            control.set_state(tk.HIDDEN)
        for led in self.leds:
            led.set_state(tk.HIDDEN)
        if activePlant.error:
            self.leds[2].set_state(tk.NORMAL)
            self.status_msg.update_text(activePlant.error_msg)
        else:
            self.leds[index].set_state(tk.NORMAL)
            self.status_msg.update_text(msg)
        self.controls[index].set_state(tk.NORMAL)

class PlantsScreen:
    def __init__(self, display, plant_btn_paths, plant_img_paths, num_col=4, num_row=2): 
        self.display = display
        self.plant_btn_paths = plant_btn_paths
        self.plant_img_paths = plant_img_paths
        self.num_col = num_col
        self.num_row = num_row
        self.page = 0
        self.num_plants = len(activePlant.available_plants)
        self.additional = True if self.num_plants >= self.num_col * self.num_row else False
        self.plant_buttons = []
        self.gen_buttons()

    def gen_buttons(self):
        self.display.clear()
        self.plant_buttons.clear()
        self.additional = True
        for i in range (self.num_row):
            for j in range (self.num_col):
                index = i * self.num_col + j + self.page * self.num_col * self.num_row
                # print(index)
                if index < self.num_plants:
                    self.plant_buttons.append(CanvasButton(self.display.canvas, 
                                                           j*175+80, i*150, 
                                                           self.plant_btn_paths[index],
                                                           self.display_plant, 
                                                           'n', index))
                    CanvasText(self.display.canvas, j*175+80, i*150+110, 
                               h[3], 'n', activePlant.available_plants[index])
                else:
                    self.additional = False
                    break
                if index + 1 == self.num_plants:
                    self.additional = False
        if self.page > 0:
            self.prev_button = CanvasButton(self.display.canvas, 175, 325, 
                                            "Prev", self.prev_page,
                                            'center')
        if self.additional:
            self.next_button = CanvasButton(self.display.canvas, 525, 325, 
                                            "Next", self.next_page,
                                            'center')
     
    def next_page(self):
        self.page += 1
        self.gen_buttons()
        print("Next Page")

    def prev_page(self):
        self.page -= 1
        self.gen_buttons()
        print("Prev Page")

    def display_plant(self, plant_num):
        self.display.clear()
        self.selected_plant = plantDB[activePlant.available_indices[plant_num]]
        self.plant_portrait = CanvasImage(self.display.canvas, 0, 0, 
                                          self.plant_img_paths[plant_num%3], 'nw')
        self.plant_name = CanvasText(self.display.canvas, 500, 0, h[2],
                                     'n', self.selected_plant.name)
        CanvasText(self.display.canvas, 100, 220, h[3], 'n', 'TDS')
        tds_str = str(self.selected_plant.ppm700_min) + "-" + str(self.selected_plant.ppm700_max)
        CanvasText(self.display.canvas, 100, 270, "TkHeadingFont", 'n', tds_str)
        CanvasText(self.display.canvas, 200, 220, h[3], 'n', 'pH')
        CanvasText(self.display.canvas, 300, 220, h[3], 'n', 'Sunlight')
        CanvasText(self.display.canvas, 400, 220, h[3], 'n', 'Est. Time')
        self.back_button = CanvasButton(self.display.canvas, 175, 325, 
                                            "Back", self.gen_buttons,
                                            'center')
        self.load_button = CanvasButton(self.display.canvas, 525, 325, 
                                            "Load", load_plant,
                                            'center', self.selected_plant)





class CreditsScreen:
    def __init__(self, display, students, second_line, instructors, advisors, 
                 sponsors, num_col = 3):
        self.display = display
        self.num_col = num_col
        self.students = students
        self.second_line = second_line
        self.instructors = instructors
        self.advisors = advisors
        self.sponsors = sponsors
        self.generate_credits()
    def generate_credits(self):
        students_formatted = self.students.copy()
        random.shuffle(students_formatted)
        CanvasText(self.display.canvas, 350, 0, h[3], 'n', 
                   "HSA Engineering 2026 Graduating Class")
        while (len(students_formatted)+len(self.second_line)) % self.num_col != 0:
            students_formatted.append("")
        num_students = len(students_formatted)
        num_row = (num_students+len(second_line))//self.num_col
        for i in range(self.num_col):
            j = 0
            while (j < num_row):
                pos = j+i*num_row
                student = students_formatted[pos]
                if pos % num_row == num_row - 1:
                    if student in self.second_line.keys():
                        print("Moving")
                        x = 1
                        while students_formatted[pos+x] in self.second_line.keys():
                            x += 1
                        students_formatted[pos], students_formatted[pos+x] = students_formatted[pos+x], students_formatted[pos]
                        student = students_formatted[pos]
                if student != "":
                    txt = "\u2022 " + student
                else:
                    txt = student
                CanvasText(self.display.canvas, 30+i*210, 30*j+40, h[3], 'nw', txt)
                if student in self.second_line.keys():
                    j += 1
                    students_formatted.insert(pos+1, self.second_line[student])
                    txt = "   " + students_formatted[pos+1]
                    CanvasText(self.display.canvas, 30+i*210, 30*j+40, h[3], 'nw', txt)
                j += 1
    
        txt = self.gen_str("Instructor", self.instructors)
        CanvasText(self.display.canvas, 30, 30*(num_students//self.num_col+2)+20, 
                   h[3], 'nw', txt)
        txt = self.gen_str("Advisor", self.advisors)
        CanvasText(self.display.canvas, 30, 30*(num_students//self.num_col+3)+30, 
                   h[3], 'nw', txt)
        txt = self.gen_str("Special Thank", self.sponsors)
        thanks = CanvasText(self.display.canvas, 30, 
                            30*(num_students//self.num_col+4)+50, h[4], 'nw', txt)
        thanks.update_width(600)
        del students_formatted
    
    def gen_str(self, start, elements):
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

BGR_IMG_PATH = "assets/bg.png"
NAV_BTN_PATHS = ("assets/button-home.png", "assets/button-plant.png", 
                 "assets/button-stats.png", "assets/button-people.png")
HSA_ICON_PATH = "assets/hsa-ico.png"
LED_PATHS = ("assets/led-white.png", "assets/led-green.png", "assets/led-red.png")
CTL_BTN_PATHS = ("assets/button-start.png", "assets/button-abort.png")
PLANT_BTN_PATHS = ('assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png")
# PLANT_BTN_PATHS = ('assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png", 'assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png")
PLANT_IMG_PATHS = ('assets/portrait-lettuce.png', 'assets/portrait-basil.png', 'assets/portrait-strawberries.png')
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
        creditsScreen.generate_credits()

def launch_popup():
    for nav_btn in nav_btns:
        nav_btn.set_state(tk.DISABLED)
    popupWindow = PopupWindow(root.tk)
    popupWindow.focus_set()
    
def abort_program():
    global activePlant
    os.remove(fname)
    activePlant = ActivePlant(plantDB[-1])
    homeScreen.plant_name.update_text(activePlant.name)
    homeScreen.update_status(0,"No Program Running")

def pause_program():
    global activePlant
    activePlant.set_running(False)
    homeScreen.update_status(0,"Program Paused")

def start_program():
    global activePlant
    if activePlant.name == "None":
        tk.messagebox.showerror(title="No Plant Selected",
                                message="You must select a plant from the Plants tab")
    else:
        activePlant.set_running(True)
        homeScreen.update_status(1,"All Systems Normal")

def load_plant(plant):
    global activePlant
    activePlant = ActivePlant(plant)
    homeScreen.plant_name.update_text(activePlant.name)
    with open(fname, "wb") as fout:
        pickle.dump(activePlant, fout)
    plantsScreen.page = 0
    plantsScreen.gen_buttons()
    nav_clicked(0)

try:
    with open('plant_db.pkl', 'rb') as fin:
        plantDB = pickle.load(fin)
    for plant in plantDB:
        print(plant.name)
except:
    print("Plant Database failed to load!!")
    sys.exit("No Plant Database")
plantDB.append(Plant("None", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)) 

fname = "plant_bkup.pkl"
try:
    with open(fname, "rb") as fin:
        activePlant = pickle.load(fin)
except FileNotFoundError:
    activePlant = ActivePlant(plantDB[-1])

activePlant.index_available()

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
homeScreen = HomeScreen(displays[0], LED_PATHS, CTL_BTN_PATHS)

# Plants Display
plantsScreen = PlantsScreen(displays[1], PLANT_BTN_PATHS, PLANT_IMG_PATHS)

# Stats Display

# Credits Display
students = ["Hajr Abdullah", "Amelia Allison", "Foday Lamboi", "Brandon Jimenez-", "Cedrick Abotchi", "Caleb Kolie", "Abdul Bayoh", "Ryan Shoults", "Abdimalik Mire", "Zack Abdullahi", "Salmaan Mosa", "Mohammed Ali"]
second_line = {"Brandon Jimenez-":"Martinez"}
instructors = ["Dorma Flemister"]
advisors = ["John Hribar", "Dr. Savas Kaya"]
sponsors = ["The Ohio State University", "Ohio University", "SenseICs", "Smarty Pants Consulting", "Horizon Science Academy"]
creditsScreen = CreditsScreen(displays[3], students, second_line, instructors, advisors, sponsors)

# Start from Home
displays[1].set_state(tk.NORMAL)

root.tk.resizable(False, False)
root.tk.mainloop()
