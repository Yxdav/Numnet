import customtkinter
import threading
import sys
import random
import json

#Custom modules
from myutils.callbacks import *
from myutils.network import *
from modules.Arpy import *


from typing import Callable, Dict
from collections import OrderedDict
from time import sleep
from contextlib import contextmanager
from tkinter import Canvas, messagebox, PhotoImage
from PIL import Image, ImageTk
from queue import Queue

#Constants
RECON_PATH = "./recon/recon.json"
ROUTER_PATH ="./assets/images/router.png"
REFRESH_PATH ="./assets/images/refresh.png"
COMP_PATH = "./assets/images/computadora.png"
EXIT_MSG = "Are you sure to want to exit, doing so will not save gathered information in /recon/recon.json. Press ctrl+s if you want to save. The information will be stored in the results folder. Report issue to https://github.com/Haz3l-cmd/Numnet"
DISCLAIMER_MSG = "This project was created solely for learning purposes and not otherwise. I am not responsible for your actions."


class Gmap(customtkinter.CTk):
      
      # All networking functions are implement in myutils/network.py
      IP:str = get_local_ip() # Gets local IP
      NET_ADDR:str = get_local_net_addr(IP) # Get network address
      MAC:str = get_mac() # Get local MAC which may be spoofed
      hosts_list:list[str] = all_hosts(NET_ADDR) # List of all hosts in the subnet
      hosts_list.insert(0, "None")
      instances = Queue()
      scanned_instances = []

      #Internals constants for configuration purposes
      MODULE_DICT:Dict[str, Callable] = OrderedDict() # Maps module to their respective method that constructs their options interface
      CURRENT_MODULES = {"current": None} # Keep track of current module
      THREADS = None
      
      #Mapper constants
      TAG_TO_ICON = OrderedDict() # Maps Tags to PhotoImage objects
      
      #Internal constants for root window
      _WINDOW_DIMENSION = "700x400"
      _WINDOW_TITLE  = "NetNum"
      
      #Internal constants for widgets
      PADDING = 5 
      LABEL_FONT_SIZE = 16
      CENTER = "nsew"

      TL_COUNT = 0

      def __init__(self):
          """This function is responsible for initialising the main window"""
          
          super().__init__()
          
          # Mapping modules to their respective callables
          # This allows option frame to be dynamic
          self.MODULE_DICT = {"Arpy": self.ARP_options_ui,
                              "UDP Scan": self.UDP_options_ui}
          
          #Ensures that window starts in full mode
          self.wm_state('zoomed')
        
          self.title(self._WINDOW_TITLE) # Main window title
          self.protocol("WM_DELETE_WINDOW", self.on_closing) # Warns user before exiting
          self.warning() # Disclaimer window
          self.grid_maker(widget=self)  # Makes a 2x2 grid within the root/main window

  
          
          
         
       

      
      def warning(self)->None:
          """Thsi method sets up the disclaimer window, users can decide whether they want to continue beyond this point
             
             :return: None
          """

          # Frame that fills up main window
          self.warning_frame = customtkinter.CTkFrame(master=self)
          self.warning_frame.pack(expand=True, fill="both")
          self.grid_maker(row= 3, column=3, weight=1, widget=self.warning_frame)

          # Label displaying disclaimer messgae
          self.warning_label = customtkinter.CTkLabel(master=self.warning_frame, text=DISCLAIMER_MSG, font=("",15))
          self.warning_label.grid(row=1, column=1, sticky="nsew")
          
          # Button that allows user to proceed further
          self.warning_button = customtkinter.CTkButton(master=self.warning_frame, text="Continue", command=self.clear_root)
          self.warning_button.grid(row=2, column=1, sticky="n")

     

      def clear_root(self)->None:
          """This method clears up the main window after user reads disclaimer and invokes self.setup() to initialise 
             the actual user interface

             :return: None
          """

          # Loops through every child widget and destroys them, a copy is made to prevent RuntimeError: dictionary changed size during iteration
          for child in self.children.copy().values(): 
              child.destroy()
          
          self.setup() # Sets up actual user interface
      
      @contextmanager
      def change_state(self, widget,init_state:str , final_state:str)->None:
          """This method acts as a context mananger and yields the Textbox widget(Used to dsiplay info)
             It changes the state to normal(normally this would be in the __enter__ dunder method) so that data can be wrritten and upon exit(__exit__) the Textbox is set back read-only 
             
             :param widget: Frame/Widget to change state off
             :param init_state: Initial state for widget, normal is enabled, disabled for disabled
             :param final: Initial state for widget, normal is enabled, disabled for disabled
             
             :return: None
          """
          try:
             widget.configure(state=init_state)
             yield widget
          finally:
             widget.configure(state=final_state)

      
      def setup(self)->None:
          """This method is one of the core methods as it responsible for setting the actual interface
             
             :return: None
          """
          
          #This frame allows the user to choose a module
          self.inner_user_select_frame = customtkinter.CTkFrame(master=self)
          self.inner_user_select_frame.grid(row=0, column=0, sticky=self.CENTER, padx=self.PADDING, pady=self.PADDING)
          self.grid_maker(widget=self.inner_user_select_frame)
          # Label which display "Select module: " 
          self.select_module_label = customtkinter.CTkLabel(master=self.inner_user_select_frame, text="Select module : ", font=("roboto",self.LABEL_FONT_SIZE))
          self.select_module_label.grid(row=0, column=0, sticky="se")
          # Drop down menu to select module
          self.module_drop_menu = customtkinter.CTkOptionMenu(master=self.inner_user_select_frame, values=list(self.MODULE_DICT.keys()))
          self.module_drop_menu.grid(row=0, column=1,sticky="sw")
          
          # This frame frame allows the user to change options of modules
          # and is dynamic, hence it will vary with respect to the module chosen, see implementation in  myutils/callbacks.py
          self.inner_user_options_frame = customtkinter.CTkFrame(master=self)
          self.inner_user_options_frame.grid(row=0, column=1, sticky=self.CENTER, padx=self.PADDING, pady=self.PADDING)

          # Provides user with information about the module chosen
          self.inner_info_panel_text_box = customtkinter.CTkTextbox(master=self, font=("roboto",15))
          self.inner_info_panel_text_box.grid(row=1, column=0,columnspan=2, sticky=self.CENTER, padx=self.PADDING, pady=self.PADDING)
          self.inner_info_panel_text_box.insert(index="1.0", text="This panel provides information about modules")
          # This line prevents users from modify the info panel
          # To prevent redundancy, the alternation between states is nicely wrapped up in  self.delete()
          # which is used as a context manager
          self.inner_info_panel_text_box.configure(state="disabled")

          # After initialising all necessary widgets
          self.module_drop_menu.configure(command=OptionMenuUI(self)) # See implementation in myutils/callbacks.py
          self.inner_info_panel_text_box.bind("<Control-MouseWheel>", ResizeTextBox(self.inner_info_panel_text_box)) # See implementation in myutils/callbacks.py
          
          # Shortcuts, try Ctrl+h for help menu or read the README.md(Usage section) file at https://github.com/Haz3l-cmd/Netnum
          self.bind("<Control-l>", self.clear)
          self.bind("<Control-w>", self.create_toplevel)
          self.bind("<Control-s>", SaveFile()) # See implementation of SaveFile() in myutils/callbacks.py
          self.bind("<Control-h>", HelpMenu()) # See implementation of HelpMenu() in myutils/callbacks.py
        
  
          
          

          


      def on_closing(self)->None:
          """This method implements the messagebox that warns the user about saving data before quiting
             
             :Return: None
          """
          if messagebox.askokcancel("Quit", EXIT_MSG):
            # This portion clears /recon/recon.json
             with open(RECON_PATH, "w") as fp:
                  pass
             self.destroy() # Destroys main window before exiting program
             sys.exit()    
      
      def clear(self, event):
          """This method clears the info panel, just like unix like system, Ctrl+l is used
             
             :param event: Used to access event value, in this case it is futile to do so

             :Return: None
          """
          with self.change_state(self.inner_info_panel_text_box, "normal", "disabled") as text_box:
               text_box.delete("1.0", "end")
         
      
      def grid_maker(self, row:int = 2, column:int =2 , weight:int = 1, widget=None)->None:
          """This process automates the process of creating grid and coloumn within a widget
             
             :param row: Number of rows
             :param coloumn: Number of column
             :param weight: Width of column/row relative to others
             :param widget: the widget or frame with needs to have grid and columns configured

             :return: None
          """
          for row in range(row):
              widget.rowconfigure(row, weight=weight)
              
          
          for column in range(column):
              widget.columnconfigure(column, weight=weight)
      def TLC(self)->None:
          """Keeps track of self.TL_COUNTer"""
          
          self.TL_COUNT -=1
          self.window.destroy()

      def create_toplevel(self, *args)->None:
            """This method implements the top level window which is also the map that allows a graphical representation of 
              the network. *NOTE* Nodes will appear after scanning the network and pressing the refres button. The gateway is always centered
              cannot be dragged around

              :param args: Additonal arguements

              :Return: None
            """
            if self.TL_COUNT < 1:
             self.window = customtkinter.CTkToplevel(self)
             self.window.minsize(400, 400)
             self.window.protocol("WM_DELETE_WINDOW", self.TLC)
             self.my_canvas = Canvas(master=self.window,bg="black") # Sets up black canvas, who the f*ck uses light mode anyways
             self.my_canvas.pack(expand=True, fill="both")
             
             # Bindings, Implementation are found withinn this file itself, though that might change in the
             # future to be more organised
             self.my_canvas.bind("<Button-3>", self.scan)
             self.my_canvas.bind("<Button3-Motion>", self.drag)
             self.my_canvas.bind("<Motion>", self.display_coords)
             self.my_label = customtkinter.CTkLabel(master=self.my_canvas, text="X: None Y: None", height=20, width=100)
             self.my_label.pack(padx="10px", pady="10px", anchor="ne")
             self.refresh_map_button = customtkinter.CTkButton(master=self.my_canvas, text="Refresh!", command=self.map_refresh, height=30, width=30)
             self.refresh_map_button.pack(padx=self.PADDING, pady=self.PADDING, anchor="ne")
             self.my_canvas.bind("<Control-s>", SaveFile())
             self.TL_COUNT += 1
            else:
                with self.change_state(self.inner_info_panel_text_box, "normal", "disabled") as tbox:
                     tbox.configure(text_color="orange")
                     tbox.insert(index="end", text="\n[-]Only one top level window can be opened at a time")

      def map_refresh(self)->None:
          """This method is responsible for refreshing the canvas. It is responsible
             for deleting images and reloading them by accordingly removing them from self.TAG_TO_ICON()
             so as to not eat up all your RAM

             :Return: None

             parsed config file looks like this --> {IP:{MAC:MAC,
                                                        is_gateway:bool}}
          """
          try:
            if len(self.my_canvas.find_all()) > 1:
               for child in self.my_canvas.find_all():
                    try:
                       self.my_canvas.delete(child)
                       self.my_canvas.delete(f"{child}-Complement")
                       self.TAG_TO_ICON.pop(child)
                    except KeyError:
                       continue
            
            with open(RECON_PATH, "r") as fp:
                 data = json.load(fp)
            
            for key, value in data.items():
                if value.get("is_gateway") is True:
                    self.generate_icon(ROUTER_PATH, f"IP: {key}\nMAC: {value.get('MAC')}")
            for key, value in data.items():
                if value.get("is_gateway") is not True:
                    self.generate_icon(COMP_PATH, f"IP: {key}\nMAC: {value.get('MAC')}")

          except json.decoder.JSONDecodeError:
                 self.err_insert(text="Scan the network first to construct the map")
          

         
      
      def scan(self, event)->None:
          """This method works together with self.drag() to allow user to move around canvas
             
             :param event: Used to access event atrributes
          """
          self.my_canvas.scan_mark(event.x, event.y)

      def drag(self, event):
          """This method works together with self.scan() to allow user to move around canvas
             
             :param event: Used to access event attributes

             :Return: None
          """
          self.my_canvas.scan_dragto(event.x, event.y, gain=2)

      def display_coords(self, event)->None:
          """This method is responsible for updating the X and Y label

             :param event: Used to access event attributes
          """
          self.my_label.configure(text=f"X: {self.my_canvas.canvasx(event.x)} Y:{self.my_canvas.canvasy(event.y)}")

      def generate_icon(self, path:str, text:str)->None:
        """This method generates icons/images on the canvas
             
             :param path: File path of image/icon
             :param text: Text to be display below icon/image, this has to be the IP and MAC. Fortunately self.map_refresh() handles all of that for us

             :Return: None
        """
        try:
          if path == COMP_PATH:
            img = Image.open(COMP_PATH) # Opens image
            resized_image = img.resize((100,100)) # Resizez image to appropriate size
            self.image = ImageTk.PhotoImage(resized_image) # Create PhotoImage object
            self.image = self.image # For persistance
            
            # self.my_image is a tag(an integer in this case) to later modify the image/icon
            # random.randrange() causes the image/icon to appear at differnet location after each refresh
            self.my_image = self.my_canvas.create_image(random.randrange(0, 500-50),random.randrange(0, 700-50), image=self.image)
            
            # A mapping of tags to PhotoImage object,
            # This allows the image to remain in memory and not be overwritten otherwise it would defeat the whole purpose of this project
            self.TAG_TO_ICON.update({self.my_image: self.image })

            # (x, y) represents the midpoint of the hosts image/icon, in this case it is found at COMP_PATH, see above
            x = ((self.my_canvas.bbox(self.my_image)[2] - self.my_canvas.bbox(self.my_image)[0])/2)+ self.my_canvas.bbox(self.my_image)[0]
            y  = ((self.my_canvas.bbox(self.my_image)[3] - self.my_canvas.bbox(self.my_image)[1])/2)+ self.my_canvas.bbox(self.my_image)[1]
        
            # (x2, y2) represents the midpoint of the router image/icon, in this case it is found at ROUTER_PATH, see above
            x2  = ((self.my_canvas.bbox("router")[2] - self.my_canvas.bbox("router")[0])/2)+ self.my_canvas.bbox("router")[0]
            y2  = ((self.my_canvas.bbox("router")[3] - self.my_canvas.bbox("router")[1])/2)+ self.my_canvas.bbox("router")[1]

            # Draws line between the two midpoints
            self.line_tag = self.my_canvas.create_line(x, y, x2, y2, fill="white")
            
            # (x3, y3) marks the start of the label which display the IP and MAC
            x3 = self.my_canvas.bbox(self.my_image)[0]
            y3 = self.my_canvas.bbox(self.my_image)[3]

            # All tags of label which display IP and MAC will have a trailing "-Complement" after the tag of their 
            # respective icon they are representing, e.g and icon having a tag of 4 will have a label with the tag
            # 4-Complement
            self.text_tag = f"{self.my_image}-Complement" # Here we it being implemented

            # See implementation of MoveCompIcon() in myutils/callbacks.py
            self.my_canvas.tag_bind(self.my_image,"<Button1-Motion>", MoveCompIcons(self, self.my_image, self.text_tag, self.line_tag ), add="+")
            self.my_canvas.tag_bind(self.my_image,"<ButtonPress-3>", self.attack, add="+")
            self.my_canvas.create_text(x3, y3, text=text, fill="white",tags=self.text_tag, anchor="nw")
           
          else:
            canvas_width =self.my_canvas.winfo_width() # width of canvas
            canvas_height = self.my_canvas.winfo_height() # height of canvas
            img = Image.open(ROUTER_PATH) # Opens image
            resized_image = img.resize((100,100)) # Resizez image to appropriate size
            self.image = ImageTk.PhotoImage(resized_image)  # Create PhotoImage object
            self.image = self.image  # For persistance

            # self.my_image is a tag(an integer in this case) to later modify the image/icon
            # This canvas item always spawns in the center after a refresh, regardless of canvas dimensions
            self.my_image = self.my_canvas.create_image(canvas_width/2, canvas_height/2, image=self.image, tags="router")

            # A mapping of tags to PhotoImage object,
            # This allows the image to remain in memory and not be overwritten otherwise it would defeat the whole purpose of this project            
            self.TAG_TO_ICON.update({self.my_image: self.image })

            # Initialy no line is created due to the fact that
            # router image/router is create alone
            self.line_tag = self.my_canvas.create_line(0, 0, 0, 0, fill="white")

            # All tags of label which display IP and MAC will have a trailing "-Complement" after the tag of their 
            # respective icon they are representing, e.g and icon having a tag of 4 will have a label with the tag
            # 4-Complement
            self.text_tag = f"{self.my_image}-Complement"

            # See implementation of MoveCompIcon() in myutils/callbacks.py
            # self.my_canvas.tag_bind(self.my_image,"<Button1-Motion>", MoveCompIcons(self, self.my_image, self.text_tag), add="+")
            
            # These coordinates are used to align label with router icon/image
            x1, y1, x2, y2 = self.my_canvas.bbox(self.my_image)
            self.my_canvas.create_text(x1, y2-20, text=text, fill="white",tags=self.text_tag, anchor="nw", width=(x2-x1)+20)
            self.my_canvas.create_text(x1, y2-20, text=None, fill="white",tags=self.text_tag, anchor="nw", width=(x2-x1)+20) #Filler
        
        except  Exception as e:
               with self.change_state(self.inner_info_panel_text_box, "normal", "disabled") as tbox:
                     tbox.configure(text_color="red")
                     tbox.insert(index="end", text="\n[Whoops!] An error occured, please restart your application and report issue to https://github.com/Haz3l-cmd/Numnet")
                     tbox.insert(index="end", text=f"\n{e}")
        
      def none_converter(self, value:str)-> None|str:
            """This method takes a string value and if is is equal to "None" return None else return value back

               :param value: A string
            """
            if value == "None":
               return None
            else:
               return value
      
      def attack(self, *args):
          self.attack_opt = customtkinter.CTkToplevel(self)
          self.attack_opt.maxsize(400, 400)
          self.grid_maker(row = 4, column = 2, widget=self.attack_opt)

          self.interval_label = customtkinter.CTkLabel(master=self.attack_opt, text="Interval :", font=("robot", self.LABEL_FONT_SIZE))
          self.interval_label.grid(row=0, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.interval_value = customtkinter.CTkEntry(master=self.attack_opt, border_width=2, corner_radius=10, placeholder_text="interger")
          self.interval_value.grid(row=0, column=1, pady=self.PADDING) 

          self.two_way_label = customtkinter.CTkLabel(master=self.attack_opt, text="Enable two-way poisoning :", font=("roboto", self.LABEL_FONT_SIZE))
          self.two_way_label.grid(row=1, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.two_way_value = customtkinter.CTkSwitch(master=self.attack_opt, text=None)
          self.two_way_value.grid(row=1, column=1, pady=self.PADDING )
          
          self.target_ipt_label = customtkinter.CTkLabel(master=self.attack_opt, text="Target IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.target_ipt_label.grid(row=2, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.target_ipt_value = customtkinter.CTkComboBox(master=self.attack_opt, values=self.hosts_list)
          self.target_ipt_value.grid(row=2, column=1, pady=self.PADDING)

          self.att_btn = customtkinter.CTkButton(master=self.attack_opt, text="Run", font=("roboto", self.LABEL_FONT_SIZE), command = self.start_attack)
          self.att_btn.grid(row=3, column=1, pady=self.PADDING )
      
      def start_attack(self):
          for obj in self.scanned_instances:
              if obj.target == self.target_ipt_value.get():
                 obj.interval = int(self.interval_value.get())
                 obj.two_way = bool( self.two_way_value.get())
                 obj.inject_packet()

      def ARP_options_ui(self, frame)->None:
          """This method is responsible for constructing the interface that allows users to
            to change module options accordingly and is module dependent, i.e each module will have it's dedicated
            method/function, as a result the interface will not be the same for all modules

            :param frame: Frame here should always be self.inner_user_options_frame as this is the frame that will allow the user to change module options
            
            :Return: None
          """
          
          self.grid_maker(row=5, column=3, weight=1, widget=frame,)

          self.target_ip_label = customtkinter.CTkLabel(master=frame, text="Target IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.target_ip_label.grid(row=0, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.target_ip_value = customtkinter.CTkComboBox(master=frame, values=self.hosts_list)
          self.target_ip_value.grid(row=0, column=1, pady=self.PADDING)
        
          
          self.gateway_ip_label = customtkinter.CTkLabel(master=frame, text="Gateway IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.gateway_ip_label.grid(row=1, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.gateway_ip_value = customtkinter.CTkOptionMenu(master=frame, values=self.hosts_list)
          self.gateway_ip_value.grid(row=1, column=1, pady=self.PADDING)
                 
          self.net_ip_label = customtkinter.CTkLabel(master=frame, text="Subnet IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.net_ip_label.grid(row=2, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.net_ip_value = customtkinter.CTkLabel(master=frame, text=self.NET_ADDR, font=("robot", self.LABEL_FONT_SIZE) )
          self.net_ip_value.grid(row=2, column=1, pady=self.PADDING)          
          
                 
          
          # self.threads_label = customtkinter.CTkLabel(master=frame, text="threads :", font=("robot", self.LABEL_FONT_SIZE))
          # self.threads_label.grid(row=3, column=0, pady=self.PADDING, padx=self.PADDING,)
          # self.threads_value = customtkinter.CTkEntry(master=frame, border_width=2, corner_radius=10, placeholder_text="interger")
          # self.threads_value.grid(row=3, column=1, pady=self.PADDING)
          
         
          self.update_button = customtkinter.CTkButton(master=frame, text="Update!", command=self.update )
          self.update_button.grid(row=3, column=0, pady=self.PADDING)
          
          self.scan_button = customtkinter.CTkButton(master=frame, text="Scan", command=self.ARP_scan )
          self.scan_button.grid(row=3, column=1, pady=self.PADDING)
        
      def ARP_scan(self)->None:
          """This function starts the scan and interfaces with this file(__file__) to display results
             in the info panel and temporarily save it to /recon/recon.json. Additionally the results of recon.json can
             be saved to the Results folder with Ctrl+s. See /modules/ARP_scan.py and /myutils/callback.py

             :Return: None
          """
          with self.change_state(self.scan_button, "disabled", "normal") as buttton:
              self.insert(text="Starting scan...")
              target = self.none_converter(self.target_ip_value.get())
              gateway =  self.gateway_ip_value.get()
    
              threads = []
              if  target is None and self.instances.empty():
                    for ip in self.hosts_list:
                        if ip != "None":
                           arpy = Arpy(target = ip, gateway = gateway, output_frame = self.inner_info_panel_text_box)
                           t = threading.Thread(target=arpy.get_mac, kwargs={"target":arpy.target})
                           threads.append(t)
                           self.instances.put(arpy)
                           t.start()
              
              else:
                arpy = Arpy(target = target, gateway = gateway, output_frame = self.inner_info_panel_text_box)
                Garpy = Arpy(target = gateway, gateway = gateway, output_frame = self.inner_info_panel_text_box)
                self.instances.put(arpy)
                self.instances.put(Garpy)
                threading.Thread(target=arpy.get_mac, kwargs={"target":arpy.target}).start()
                threading.Thread(target=Garpy.get_mac, kwargs={"target":Garpy.target}).start()
             
              
                
              
              threads.clear()
              self.insert(text="Finshed scanning...")
              
              

              
           


      def update(self):
          self.scanned_instances.clear()
          for _ in range(len(self.hosts_list)-1):
                  try:
                     obj = self.instances.get_nowait()
                     self.scanned_instances.append(obj)
                     obj.save()
                  except queue.Empty:
                         self.err_insert(text="It seems like there are no new hosts online")
                         break


      def UDP_options_ui(self, frame):
         """In developement"""
         self.grid_maker(row=1, column=1, widget=frame)
         Label = customtkinter.CTkLabel(master=frame, text="I'm UDP scanner options and current in developmet, yayy!")
         Label.grid(row=0, column=0, sticky="nsew")
      
      def UDP_scan(self):
         """Implement"""


      def insert(self, text:str =None)->None:
        """This method outputs message to info panel, you can think of it as redirecting stdout to info panel
           
           :param text: text to ouput
           :Return:None
        """
        self.inner_info_panel_text_box.configure(text_color="lime green")
        self.inner_info_panel_text_box.configure(state="normal")
        self.inner_info_panel_text_box.insert(index="end", text="\n[{}] (Using {}) : [+] {}".format(strftime("%H:%M:%S"),self.CURRENT_MODULES.get("current"), text))
        self.inner_info_panel_text_box.configure(state="disabled")
    
    
      def err_insert(self, text=None):
        """This method outputs error message to info panel, you can think of it as redirecting stderr to info panel
           
           :param text: text to ouput
           :Return:None
        """
        self.inner_info_panel_text_box.configure(text_color="orange")
        self.inner_info_panel_text_box.configure(state="normal")
        self.inner_info_panel_text_box.insert(index="end", text="\n[{}] (Using {}) : [-] {}".format(strftime("%H:%M:%S"),self.CURRENT_MODULES.get("current"), text))
        self.inner_info_panel_text_box.configure(state="disabled")


app = Gmap()

app.mainloop()


