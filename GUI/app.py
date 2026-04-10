import tkinter as tk  # PEP 8 recommends avoiding `import *`.
from tkinter import font
import tkinter.messagebox
from time import gmtime, strftime, time, sleep
import json
from serial import Serial, SerialException
from datetime import date, timedelta
import random, pickle, os, sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
class Plant():
    tolerance = 0.1
    def __init__(self, name, pH_min, pH_max, ec_min, ec_max,cf_min, 
                 cf_max, ppm700_min, ppm700_max, ppm500_min, ppm500_max,
                 sun_min, sun_max, germ_days, harvest_days, desc):
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
        self.sun_min = sun_min
        self.sun_max = sun_max
        self.germ_days = germ_days
        self.harvest_days = harvest_days
        self.desc = desc

class ActivePlant(Plant):
    available_plants = ["Lettuce", "Basil", "Strawberries"]
    available_indices = []
    def __init__(self, plant):
        super().__init__(plant.name, plant.pH_min, plant.pH_max, plant.ec_min, 
                         plant.ec_max, plant.cf_min, plant.cf_max, plant.ppm700_min, 
                         plant.ppm700_max, plant.ppm500_min, plant.ppm500_max, 
                         plant.sun_min, plant.sun_max, plant.germ_days,
                         plant.harvest_days, plant.desc)
        self.total_days = self.harvest_days + self.germ_days
        self.start_date = 0
        self.running = False
        self.paused = False
        self.error = False
        self.error_msgs = ("pH is too low", "pH is too high", "tds is too low",
                           "tds is too high", "serial communication is lost")
        self.error_msg = "Error"
        self.tds = 800
        self.ph = 6.2
        self.light_status = 0
        self.time_left = self.total_days
        self.set_date()
    
    def start_stop(self):
        self.running = not self.running

    def pause(self):
        self.paused = not self.paused
    
    def index_available(self):
        for available_plant in self.available_plants:
            self.find_indices(available_plant)
        print(self.available_indices)
    
    def find_indices(self, available_plant):
        try:
            self.available_indices.append(next(filter(
                lambda x: x[1].name == available_plant, enumerate(plantDB)))[0])
        except StopIteration:
            self.available_indices.append(-1)

    def set_date(self):
        if not self.running:
            self.start_date = 0
            self.harvest_date = "--/--/--"
        else:
            self.start_date = date.today()
            self.harvest = self.start_date + timedelta(days=self.total_days)
            self.harvest_date = self.harvest.strftime("%m/%d/%y")

class SerialInterface:
    """Creates a Serial Interface with the specified parameters and allows to read from
    and write to it."""
    def __init__(self, port="/dev/ttyACM0", baud=115200):
        self.no_response = False
        self.timeout_timer = time()
        self.ser = Serial(port, baudrate=baud)
        sleep(2)

    def read_from(self):
        """Reads a line from the serial buffer,
        decodes it and returns its contents as a dict."""
        now = time()
        if (now - self.timeout_timer) > 3:
            print("Timeout reached. No message received.")
            return None

        if self.ser.in_waiting == 0:
            # Nothing received
            self.no_response = True
            return None

        incoming = self.ser.readline().decode("utf-8")
        resp = None
        self.no_response = False
        self.timeout_timer = time()

        try:
            resp = json.loads(incoming)
        except json.JSONDecodeError:
            print("Error decoding JSON message!")

        return resp

    def send_to(self, message=None):
        """Sends a JSON-formatted command to the serial
        interface."""
        if self.no_response:
            # If no response was received last time, we don't send another request
            return

        try:
            json_msg = json.dumps(message)
            self.ser.write(json_msg.encode("utf-8"))
        except TypeError:
            print("Unable to serialize message.")

    def close(self):
        """Close the Serial connection."""
        self.ser.close()



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

    def __init__(self, parent, abort_cmd, pause_cmd, nav_btns):
        self.parent = parent
        self.nav_btns = nav_btns
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
        button_pause = tk.Button(content, text="Pause", 
                                 command=lambda:[pause_cmd(), self.close()])
        button_pause.grid(column=3, row=4, sticky='e', pady=20)
        button_abort = tk.Button(content, text="Abort", 
                                 command=lambda:[abort_cmd(), self.close()])
        button_abort.grid(column=4, row=4, sticky='e', pady=20)
        self.deiconify()

    def close(self, event=None):
        for nav_btn in self.nav_btns:
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
            print(btn_num)
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

    def align_text(self, alignment):
        self.canvas.itemconfigure(self.canvas_txt_obj, justify=alignment)

    def update_width(self, width):
        self.canvas.itemconfigure(self.canvas_txt_obj, width=width)
        # self.bbox = self.canvas.bbox(self.canvas_txt_obj)
        # self.canvas.create_rectangle(self.bbox, outline="blue")

class CanvasFrame:
    def __init__(self, canvas, x, y, root_width, root_height, 
                 background_img, state=tk.NORMAL):
        self.root_canvas = canvas
        self.background_img = background_img
        self.frame_height = root_height-y
        self.frame_width = root_width-x
        self.F = tk.Frame(canvas, bg='', height=self.frame_height, 
                          width=self.frame_width)
        self.canvas_frame_obj = canvas.create_window(x, y, anchor='nw', 
                                                     state=state, window=self.F)
        self.canvas = tk.Canvas(self.F, bg="white", height=self.frame_height, 
                                width=self.frame_width, bd=0, highlightthickness=0, 
                                relief="ridge")
        self.canvas.place(x=0,y=0)
        self.canvas.create_image(self.frame_width, self.frame_height, 
                                 anchor='se', image=self.background_img)
        self.set_state(state)
    def set_state(self, state):
        self.root_canvas.itemconfigure(self.canvas_frame_obj, state=state)
    def clear(self):
        self.canvas.delete("all")
        self.canvas.create_image(self.frame_width, self.frame_height, 
                                 anchor='se', image=self.background_img)

class HomeScreen:
    def __init__(self, display, led_paths, ctl_btn_paths, 
                 start_cmd, popup_cmd, activePlant, h):
        self.h = h
        self.display = display
        self.led_paths = led_paths
        self.ctl_btn_paths = ctl_btn_paths
        self.digital_clock = CanvasText(self.display.canvas, 310, -40, self.h[0],'n')
        self.weekday = CanvasText(self.display.canvas, 80, 0, self.h[3], 'n')
        self.month = CanvasText(self.display.canvas, 0, 37, self.h[4])
        self.day = CanvasText(self.display.canvas, 80, 35, self.h[2], 'n')
        self.year = CanvasText(self.display.canvas, 0, 77, self.h[4])
        CanvasText(self.display.canvas, 670, 0, self.h[4], 'ne', "Current Plant:")
        self.plant_name = CanvasText(self.display.canvas, 670, 25, self.h[2],
                                     'ne', activePlant.name)
        CanvasText(self.display.canvas, 20, 155, self.h[2], 'w', 
                   "Estimated Harvest Date:")
        self.harvest_date = CanvasText(self.display.canvas, 400, 205, self.h[2], 
                                       'w', activePlant.harvest_date)
        CanvasText(self.display.canvas, 20, 260, self.h[3], 'nw', "Status:")
        self.leds = []
        for i in range(0, len(self.led_paths)):
            self.leds.append(CanvasImage(self.display.canvas, 60, 300, 
                                         self.led_paths[i], 'w', tk.HIDDEN))
        self.status_msgs = ("No Program Running", "All Systems Normal")
        self.status_msg = CanvasText(self.display.canvas, 200, 300, self.h[3], 
                                     "w", "")
        self.controls = []
        self.ctl_cmds = (start_cmd, popup_cmd)
        for i in range(0, len(ctl_btn_paths)):
            self.controls.append(CanvasButton(self.display.canvas, 600, 300, 
                                              self.ctl_btn_paths[i], self.ctl_cmds[i],
                                              'center', None, tk.HIDDEN))
        self.change_state(activePlant)

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
     
    def update_home(self, activePlant):
        self.update_time()
        if self.activePlant.error:
            self.leds[2].set_state(tk.NORMAL)
            self.status_msg.update_text(self.activePlant.error_msg)
        elif self.update_controls:
            self.update_controls = False
            for control in self.controls:
                control.set_state(tk.HIDDEN)
            for led in self.leds:
                led.set_state(tk.HIDDEN)
            if self.activePlant.running and not self.activePlant.paused:
                self.controls[1].set_state(tk.NORMAL)
                self.leds[1].set_state(tk.NORMAL)
                self.status_msg.update_text("All Systems Normal")
            else:
                self.controls[0].set_state(tk.NORMAL)
                self.leds[0].set_state(tk.NORMAL)
                if self.activePlant.paused:
                    self.status_msg.update_text("Program Paused")
                else:
                    self.status_msg.update_text("No Program Running")
        # lambda:(command(btn_num))
        # self.display.canvas.after(1000, self.update_home)

    def change_state(self, activePlant):
        self.update_controls = True
        self.activePlant = activePlant
        self.plant_name.update_text(self.activePlant.name)
        self.update_home(activePlant)
        self.harvest_date.update_text(self.activePlant.harvest_date) 

class PlantsScreen:
    def __init__(self, display, plant_btn_paths, plant_img_paths, plant_load_cmd, 
                 activePlant, h, num_col=4, num_row=2): 
        self.display = display
        self.plant_btn_paths = plant_btn_paths
        self.plant_img_paths = plant_img_paths
        self.plant_load_cmd = plant_load_cmd
        self.activePlant = activePlant
        self.h = h
        self.num_col = num_col
        self.num_row = num_row
        self.page = 0
        self.num_plants = len(self.activePlant.available_plants)
        # self.additional = True if self.num_plants >= self.num_col * self.num_row else False
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
                                                           # self.plant_btn_paths[index%3],
                                                           self.plant_btn_paths[index],
                                                           self.display_plant, 
                                                           'n', index))
                    CanvasText(self.display.canvas, j*175+80, i*150+110, 
                               self.h[3], 'n', self.activePlant.available_plants[index])
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
        self.sel_plant = plantDB[self.activePlant.available_indices[plant_num]]
        self.plant_portrait = CanvasImage(self.display.canvas, 0, 0, 
                                          # self.plant_img_paths[plant_num%3], 'nw')
                                          self.plant_img_paths[plant_num], 'nw')
        self.plant_name = CanvasText(self.display.canvas, 500, 0, self.h[3],
                                     'n', self.sel_plant.name)
        self.plant_desc = CanvasText(self.display.canvas, 470, 35, self.h[4],
                                     'n', self.sel_plant.desc)
        self.plant_desc.update_width(320)
        tds_str = str(self.sel_plant.ppm700_min) + "-" + str(self.sel_plant.ppm700_max)
        CanvasText(self.display.canvas, 60, 220, self.h[3], 'n', 'TDS')
        CanvasText(self.display.canvas, 60, 260, "TkHeadingFont", 'n', tds_str)
        CanvasText(self.display.canvas, 60, 280, "TkHeadingFont", 'n', "ppm")
        ph_str = str(self.sel_plant.pH_min) + "-" + str(self.sel_plant.pH_max)
        CanvasText(self.display.canvas, 240, 220, self.h[3], 'n', 'pH')
        CanvasText(self.display.canvas, 240, 270, "TkHeadingFont", 'n', ph_str)
        sun_str = str(self.sel_plant.sun_min) + '-' + str(self.sel_plant.sun_max)
        CanvasText(self.display.canvas, 420, 220, self.h[3], 'n', 'Sunlight')
        CanvasText(self.display.canvas, 420, 260, "TkHeadingFont", 'n', sun_str)
        CanvasText(self.display.canvas, 420, 280, "TkHeadingFont", 'n', "hours")
        time_str = str(self.sel_plant.germ_days + self.sel_plant.harvest_days)
        CanvasText(self.display.canvas, 600, 220, self.h[3], 'n', 'Est. Time')
        CanvasText(self.display.canvas, 600, 260, "TkHeadingFont", 'n', time_str)
        CanvasText(self.display.canvas, 600, 280, "TkHeadingFont", 'n', "days")
        self.back_button = CanvasButton(self.display.canvas, 175, 325, 
                                            "Back", self.gen_buttons,
                                            'center')
        if not self.activePlant.running:
            self.load_button = CanvasButton(self.display.canvas, 525, 325, 
                                                "Load", self.plant_load_cmd,
                                                'center', self.sel_plant)
    def reset(self):
        self.page = 0
        self.gen_buttons()

class StatsScreen:
    def __init__(self, display, activePlant, h):
        self.display = display
        self.activePlant = activePlant
        self.h = h
        self.x = []
        self.y1 = []
        self.y2 = []
        self.fig = Figure(figsize=(5.4,2.5), dpi=100)
        self.display_stats(activePlant)
        if self.activePlant.name == "None":
            self.displays_active = False
        else:
            self.displays_active = True

    def display_stats(self, activePlant):
        self.activePlant = activePlant
        self.display.clear()
        try:
            self.gcanvas.get_tk_widget().destroy()
        except AttributeError:
            pass
        if self.activePlant.name == "None":
            warning = CanvasText(self.display.canvas, 350, 100, self.h[2], 'n',
                                 "Please Run a Plant Program To View Stats")
            warning.update_width(650)
            warning.align_text("center")
            self.x.clear()
            self.y1.clear()
            self.y2.clear()
            self.displays_active = False
        else:
            # self.plant_name = CanvasText(self.display.canvas, 500, 0, self.h[3], 'n', self.activePlant.name)
            CanvasText(self.display.canvas, 60, 255, self.h[3], 'n', 'TDS')
            self.tds_disp =CanvasText(self.display.canvas, 60, 295, 
                                 "TkHeadingFont", 'n', self.activePlant.tds)
            CanvasText(self.display.canvas, 60, 315, "TkHeadingFont", 'n', "ppm")
            CanvasText(self.display.canvas, 240, 255, self.h[3], 'n', 'pH')
            self.ph_disp = CanvasText(self.display.canvas, 240, 305, 
                                 "TkHeadingFont", 'n', self.activePlant.ph)
            CanvasText(self.display.canvas, 420, 255, self.h[3], 'n', 'Light')
            if self.activePlant.light_status == 0:
                light_msg = "Off"
            else:
                light_msg = "On"
            self.light_status = CanvasText(self.display.canvas, 420, 305, 
                                           "TkHeadingFont", 'n', 
                                           light_msg)
            CanvasText(self.display.canvas, 600, 255, self.h[3], 'n', 'Est. Time')
            self.time_left = CanvasText(self.display.canvas, 600, 295, 
                                        "TkHeadingFont", 'n', self.activePlant.time_left)
            CanvasText(self.display.canvas, 600, 315, "TkHeadingFont", 'n', "days")
            
            self.plot1 = self.fig.add_subplot(111)
            self.line1, = self.plot1.plot([], [], 'r-', label="TDS")
            self.plot1.set_ylim(600, 800)
            self.plot1.set_title("Sensor History")
            self.plot1.set_xlabel("Time")
            self.plot1.set_ylabel("Parts per Million (ppm)")
            self.plot2 = self.plot1.twinx()
            self.line2, = self.plot2.plot([], [], 'b-', label="pH")
            self.plot2.set_ylim(5, 8)
            self.plot2.set_ylabel("pH")

            self.lns = [self.line1, self.line2]
            self.labs = [l.get_label() for l in self.lns]
            self.plot1.legend(self.lns, self.labs)
            
            self.gcanvas = FigureCanvasTkAgg(self.fig, master=self.display.canvas)
            self.gcanvas.get_tk_widget().place(x=60, y=0)
            
            self.displays_active = True

    def update_plot(self):
        self.x.append(time() % 50)
        self.y1.append(self.activePlant.tds)
        self.y2.append(self.activePlant.ph)

        if len(self.y1) > 50:
            self.x.pop(0)
            self.y1.pop(0)
            self.y2.pop(0)

        self.line1.set_data(range(len(self.y1)), self.y1)
        self.line2.set_data(range(len(self.y2)), self.y2)
        self.plot1.set_xlim(0, len(self.y1))
        self.gcanvas.draw()

    def update_stats(self, activePlant):
        self.activePlant = activePlant
        if self.displays_active:
            self.tds_disp.update_text(self.activePlant.tds)
            self.ph_disp.update_text(self.activePlant.ph)
            if self.activePlant.light_status == 0:
                light_msg = "Off"
            else:
                light_msg = "On"
            self.light_status.update_text(light_msg)
            self.time_left.update_text(self.activePlant.time_left)
            self.update_plot()

class CreditsScreen:
    def __init__(self, display, students, second_line, instructors, advisors, 
                 sponsors, h, num_col = 3):
        self.display = display
        self.num_col = num_col
        self.students = students
        self.second_line = second_line
        self.instructors = instructors
        self.advisors = advisors
        self.sponsors = sponsors
        self.h = h
        self.generate_credits()

    def generate_credits(self):
        st_fmt = self.students.copy()
        random.shuffle(st_fmt)
        CanvasText(self.display.canvas, 350, 0, self.h[3], 'n', 
                   "HSA Engineering 2026 Graduating Class")
        while (len(st_fmt)+len(self.second_line)) % self.num_col != 0:
            st_fmt.append("")
        num_students = len(st_fmt)
        num_row = (num_students+len(second_line))//self.num_col
        for i in range(self.num_col):
            j = 0
            while (j < num_row):
                pos = j+i*num_row
                student = st_fmt[pos]
                if pos % num_row == num_row - 1:
                    if student in self.second_line.keys():
                        # print("Moving")
                        x = 1
                        while st_fmt[pos+x] in self.second_line.keys():
                            x += 1
                        st_fmt[pos], st_fmt[pos+x] = st_fmt[pos+x], st_fmt[pos]
                        student = st_fmt[pos]
                if student != "":
                    txt = "\u2022 " + student
                else:
                    txt = student
                CanvasText(self.display.canvas, 30+i*210, 30*j+40, self.h[3], 'nw', txt)
                if student in self.second_line.keys():
                    j += 1
                    st_fmt.insert(pos+1, self.second_line[student])
                    txt = "   " + st_fmt[pos+1]
                    CanvasText(self.display.canvas, 30+i*210, 30*j+40, self.h[3], 
                               'nw', txt)
                j += 1
    
        txt = self.gen_str("Instructor", self.instructors)
        CanvasText(self.display.canvas, 30, 30*(num_students//self.num_col+2)+20, 
                   self.h[3], 'nw', txt)
        txt = self.gen_str("Advisor", self.advisors)
        CanvasText(self.display.canvas, 30, 30*(num_students//self.num_col+3)+30, 
                   self.h[3], 'nw', txt)
        txt = self.gen_str("Special Thank", self.sponsors)
        thanks = CanvasText(self.display.canvas, 30, 
                            30*(num_students//self.num_col+4)+50, self.h[4], 'nw', txt)
        thanks.update_width(600)
        del st_fmt
    
    def gen_str(self, start, elements):
        txt = start
        num_elements = len(elements)
        if num_elements > 1:
            random.shuffle(elements)
            txt = txt + "s: "
        else:
            txt = txt + ": "
        for i in range(num_elements):
            txt = txt + elements[i]
            if i < num_elements - 1:
                txt = txt + ", "
        return txt       

class App:
    def __init__(self, root):
        self.root = root
        self.background_img = tk.PhotoImage(file=BGR_IMG_PATH)
        self.bgr_width = self.background_img.width()
        self.bgr_height = self.background_img.height()
        self.root.tk.geometry(f'{self.bgr_width}x{self.bgr_height}')
        self.root.tk.title("Hydro-Smart")
        self.root.tk.configure(bg="white")
        self.root.tk.resizable(False, False)

        self.bg_canvas = tk.Canvas(root.tk, bg="white", height=self.bgr_height, 
                                   width=self.bgr_width, bd=0, highlightthickness=0, 
                                   relief="ridge")
        self.bg_canvas.place(x=0, y=0)
        self.background = self.bg_canvas.create_image(0, 0, anchor='nw', 
                                                      image=self.background_img)
        self.fname = "plant_bkup.pkl"
        try:
            with open(self.fname, "rb") as fin:
                self.activePlant = pickle.load(fin)
        except FileNotFoundError:
            self.activePlant = ActivePlant(plantDB[-1])
        
        self.activePlant.index_available()

        # self.arduino = self.start_arduino()
        
        font_sizes = (120, 64, 40, 24, 16)
        self.h = []
        for i in range(len(font_sizes)):
           self.h.append(("Blank River", font_sizes[i]))

        self.nav_btns = []
        self.displays = []
        for i in range(0, len(NAV_BTN_PATHS)):
            self.nav_btns.append(CanvasImageButton(self.bg_canvas, 0, i*120, 
                                                   NAV_BTN_PATHS[i], self.nav_clicked, 
                                                   'nw', i))
            self.displays.append(CanvasFrame(self.bg_canvas, 100, 120, 
                                             self.bgr_width, self.bgr_height, 
                                             self.background_img, tk.HIDDEN))

        self.canvas_icon = CanvasImage(self.bg_canvas, 780, 15, HSA_ICON_PATH, 'ne')
        CanvasText(self.bg_canvas, 400, 0, self.h[1], 'n', "Hydro-Smart")

        # Home Display
        self.homeScreen = HomeScreen(self.displays[0], LED_PATHS, CTL_BTN_PATHS,
                                     self.start_program, self.launch_popup, 
                                     self.activePlant, self.h)

        # Plants Display
        self.plantsScreen = PlantsScreen(self.displays[1], PLANT_BTN_PATHS, 
                                         PLANT_IMG_PATHS, self.load_plant, 
                                         self.activePlant, self.h)

        # Stats Display
        self.statsScreen = StatsScreen(self.displays[2], self.activePlant, self.h)

        # Credits Display
        self.creditsScreen = CreditsScreen(self.displays[3], students, second_line, 
                                           instructors, advisors, sponsors, self.h)
        # Start from Home
        self.nav_clicked(0)

        self.index = 0
        self.max_index = 9
        self.tds_tuple = (712, 704, 701, 722, 729, 736, 742, 744, 701, 733)
        self.ph_tuple = (6.9, 6.9, 6.6, 7.3, 6.8, 6.5, 6.6, 7.1, 7.1, 7.3)
        
        self.update_displays()

    def btn_clicked():
        """ Prints to console a message every time the button is clicked """
        print("Button Clicked")
    
    def nav_clicked(self,btn):
        print(btn)
        self.nav_btns[btn].flash()
        for display in self.displays:
            display.set_state(tk.HIDDEN)
        self.displays[btn].set_state(tk.NORMAL)
        if btn == 3:
            self.displays[3].clear()
            self.creditsScreen.generate_credits()
    
    def launch_popup(self):
        for nav_btn in self.nav_btns:
            nav_btn.set_state(tk.DISABLED)
        popupWindow = PopupWindow(self.root.tk, self.abort_program, 
                                  self.pause_program, self.nav_btns)
        popupWindow.focus_set()
        
    def abort_program(self):
        self.activePlant = ActivePlant(plantDB[-1])
        self.homeScreen.change_state(self.activePlant)
        self.statsScreen.display_stats(self.activePlant)
        msg = {"msg": "CMD", "light_state": "0"}  # Define your JSON message
        # self.arduino.send_to(msg)
        os.remove(self.fname)
    
    def pause_program(self):
        self.activePlant.pause()
        self.homeScreen.change_state(self.activePlant)
        self.save_state()

    def start_program(self):
        if self.activePlant.name == "None":
            tk.messagebox.showerror(title="No Plant Selected",
                                    message="Select a plant from the Plants tab")
        else:
            if self.activePlant.paused:
                self.activePlant.pause()
            else:
                self.activePlant.start_stop()
                self.activePlant.set_date()
                self.statsScreen.display_stats(self.activePlant)
                self.plantsScreen.reset()
            self.homeScreen.change_state(self.activePlant)
            self.save_state()
            msg = {"msg": "CMD", "light_state": "1"}  # Define your JSON message
            # self.arduino.send_to(msg)

    def load_plant(self, plant):
        self.activePlant = ActivePlant(plant)
        self.homeScreen.change_state(self.activePlant)
        with open(self.fname, "wb") as fout:
            pickle.dump(self.activePlant, fout)
        self.plantsScreen.reset()
        self.nav_clicked(0)

    def update_displays(self):
        # print("Updating")
        self.index += 1
        if self.index > self.max_index:
            self.index = 0
        self.activePlant.tds = self.tds_tuple[self.index]
        self.activePlant.ph = self.ph_tuple[self.index]
        self.homeScreen.update_home(self.activePlant)
        self.statsScreen.update_stats(self.activePlant)
        self.plantsScreen.activePlant.running = self.activePlant.running
        root.frame.after(1000, self.update_displays)

    def save_state(self):
        if self.activePlant.running:
            with open(self.fname, "wb") as fout:
                pickle.dump(self.activePlant, fout)

    def start_arduino(self):
        connection_est = False
        while not connection_est:
            try:    
                arduino = SerialInterface()
                connection_est = True
            except SerialException:
                print("Cannot establish connection!!")
                sleep(2)
        return arduino



# Read-only Data
BGR_IMG_PATH = "assets/bg.png"
NAV_BTN_PATHS = ("assets/button-home.png", "assets/button-plant.png", 
                 "assets/button-stats.png", "assets/button-people.png")
HSA_ICON_PATH = "assets/hsa-ico.png"
LED_PATHS = ("assets/led-white.png", "assets/led-green.png", "assets/led-red.png")
CTL_BTN_PATHS = ("assets/button-start.png", "assets/button-abort.png")
PLANT_BTN_PATHS = ('assets/button-lettuce.png', "assets/button-basil.png", "assets/button-strawberries.png")
PLANT_IMG_PATHS = ('assets/portrait-lettuce.png', 'assets/portrait-basil.png', 'assets/portrait-strawberries.png')
students = ["Hajr Abdullah", "Amelia Allison", "Foday Lamboi", "Brandon Jimenez-", "Cedrick Abotchi", "Caleb Kolie", "Abdul Bayoh", "Abdimalik Mire", "Zack Abdullahi", "Salmaan Mosa", "Mohammed Ali"]
second_line = {"Brandon Jimenez-":"Martinez"}
instructors = ["Dorma Flemister"]
advisors = ["John Hribar", "Dr. Savas Kaya"]
sponsors = ["The Ohio State University", "Ohio University", "SenseICs", "Smarty Pants Consulting", "Horizon Science Academy"]

try:
    with open('plant_db.pkl', 'rb') as fin:
        plantDB = pickle.load(fin)
    for plant in plantDB:
        print(plant.name)
except:
    print("Plant Database failed to load!!")
    sys.exit("No Plant Database")
plantDB.append(Plant("None", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "This plant is not in the proper format or is misspelled in the available_plants list. Please check the spelling or review the database, recompile and try again")) 

# Main Application
root = Fullscreen_Window()
app = App(root)
# root.protocol("WM_DELETE_WINDOW", ask_quit)
root.tk.mainloop()
