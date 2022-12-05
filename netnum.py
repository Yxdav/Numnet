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
from time import sleep
from contextlib import contextmanager
from tkinter import Canvas, messagebox, PhotoImage
from PIL import Image, ImageTk

#Constants
RECON_PATH = "./recon/recon.json"
ROUTER_PATH ="./assets/images/router.png"
REFRESH_PATH ="./assets/images/refresh.png"
COMP_PATH = "./assets/images/computadora.png"
EXIT_MSG = "Are you sure to want to exit, doing so will not save gathered information in /recon/recon.json. Press ctrl+s if you want to save. The information will be stored in the results folder. Report issue to https://github.com/Haz3l-cmd/Netnum"
DISCLAIMER_MSG = "This project was created solely for learning purposes and not otherwise. I am not responsible for your actions."

class Gmap(customtkinter.CTk):
      
      # All networking functions are implement in myutils/network.py
      IP:str = get_local_ip() # Gets local IP
      NET_ADDR:str = get_local_net_addr(IP) # Get network address
      MAC:str = get_mac() # Get local MAC which may be spoofed
      hosts_list:list = all_hosts(NET_ADDR) # List of all hosts in the subnet
      hosts_list.insert(0, "None")
      #Internals constants for configuration purposes
      MODULE_DICT:Dict[str, Callable] = {} # Maps module to their respective method that constructs their options interface
      CURRENT_MODULES = {"current": None} # Keep track of current module
      
      #Mapper constants
      TAG_TO_ICON = {} # Maps Tags to PhotoImage objects
      
      #Internal constants for root window
      _WINDOW_DIMENSION = "700x400"
      _WINDOW_TITLE  = "NetNum"
      
      #Internal constants for widgets
      PADDING = 5 
      LABEL_FONT_SIZE = 16
      CENTER = "nsew"

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
      def change_state(self)->None:
          """This method acts as a context mananger and yields the Textbox widget(Used to dsiplay info)
             It changes the state to normal(normally this would be in the __enter__ dunder method) so that data can be wrritten and upon exit(__exit__) the Textbox is set back read-only 

             :return: None
          """
          try:
             self.inner_info_panel_text_box.configure(state="normal")
             yield self.inner_info_panel_text_box
          finally:
             self.inner_info_panel_text_box.configure(state="disabled")

      
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
          with self.change_state() as text_box:
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

      def create_toplevel(self, *args)->None:
           """This method implements the top level window which is also the map that allows a graphical representation of 
              the network. *NOTE* Nodes will appear after scanning the network and pressing the refres button. The gateway is always centered
              cannot be dragged around

              :param args: Additonal arguements

              :Return: None
           """
           self.window = customtkinter.CTkToplevel(self)
           self.window.minsize(800, 800)
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
           

      def map_refresh(self)->None:
          """This method is responsible for refreshing the canvas. It is responsible
             for deleting images and reloading them by accordingly removing them from self.TAG_TO_ICON()
             so as to not eat up all your RAM

             :Return: None
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
            
            for key in data:
                
                if key == self.gateway_ip_value.get():
                  self.generate_icon(ROUTER_PATH, f"IP: {key}\n MAC:{data.get(key)}")
                else:
                  self.generate_icon(COMP_PATH, f"IP: {key}\nMAC:{data.get(key)}")

          except json.decoder.JSONDecodeError:
                 pass
          

         
      
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
         
      
      def ARP_options_ui(self, frame)->None:
          """This method is responsible for constructing the interface that allows users to
            to change module options accordingly and is module dependent, i.e each module will have it's dedicated
            method/function, as a result the interface will not be the same for all modules

            :param frame: Frame here should always be self.inner_user_options_frame as this is the frame that will allow the user to change module options
            
            :Return: None
          """
          
          self.grid_maker(row=7, column=3, weight=1, widget=frame,)

          self.target_ip_label = customtkinter.CTkLabel(master=frame, text="Target IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.target_ip_label.grid(row=0, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.target_ip_value = customtkinter.CTkComboBox(master=frame, values=self.hosts_list)
          self.target_ip_value.grid(row=0, column=1, pady=self.PADDING)
        
          
          self.gateway_ip_label = customtkinter.CTkLabel(master=frame, text="Gateway IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.gateway_ip_label.grid(row=1, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.gateway_ip_value = customtkinter.CTkComboBox(master=frame, values=self.hosts_list)
          self.gateway_ip_value.grid(row=1, column=1, pady=self.PADDING)
          self.gateway_ip_value.configure(command=InitRouter(self))
          
          self.net_ip_label = customtkinter.CTkLabel(master=frame, text="Subnet IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.net_ip_label.grid(row=2, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.net_ip_value = customtkinter.CTkLabel(master=frame, text=self.NET_ADDR, font=("robot", self.LABEL_FONT_SIZE) )
          self.net_ip_value.grid(row=2, column=1, pady=self.PADDING)          
          
          self.interval_label = customtkinter.CTkLabel(master=frame, text="Interval :", font=("robot", self.LABEL_FONT_SIZE))
          self.interval_label.grid(row=3, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.interval_value = customtkinter.CTkEntry(master=frame, border_width=2, corner_radius=10, placeholder_text="interger")
          self.interval_value.grid(row=3, column=1, pady=self.PADDING)         
          
          self.threads_label = customtkinter.CTkLabel(master=frame, text="threads :", font=("robot", self.LABEL_FONT_SIZE))
          self.threads_label.grid(row=4, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.threads_value = customtkinter.CTkEntry(master=frame, border_width=2, corner_radius=10, placeholder_text="interger")
          self.threads_value.grid(row=4, column=1, pady=self.PADDING)
          
          self.two_way_label = customtkinter.CTkLabel(master=frame, text="Enable two-way poisoning :", font=("roboto", self.LABEL_FONT_SIZE))
          self.two_way_label.grid(row=5, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.two_way_value = customtkinter.CTkSwitch(master=frame, text=None)
          self.two_way_value.grid(row=5, column=1, pady=self.PADDING )

          scan_button = customtkinter.CTkButton(master=frame, text="Scan", command=self.ARP_scan )
          scan_button.grid(row=6, column=1, pady=self.PADDING)
          
      def ARP_scan(self)->None:
          """This function starts the scan and interfaces with this file(__file__) to display results
             in the info panel and temporarily save it to /recon/recon.json. Additionally the results of recon.json can
             be saved to the Results folder with Ctrl+s. See /modules/ARP_scan.py and /myutils/callback.py

             :Return: None
          """
          tgt_ip = self.target_ip_value.get()
          gtw_ip = self.gateway_ip_value .get()
          net_ip = self.NET_ADDR
          interval = self.interval_value.get()
          threads = self.threads_value.get()
          two_way_flag = bool(self.two_way_value.get())
          ARP_thread = threading.Thread(target=Arpy,
                                        daemon=True,
                                        args=(net_ip, gtw_ip,self.MAC), 
                                        kwargs={"interval":interval, 
                                                "two_way_flag":two_way_flag, 
                                                "output_frame":self.inner_info_panel_text_box,
                                                "target_ip": tgt_ip,
                                                 "threads": threads},)
          ARP_thread.start()

         
          


        

      def UDP_options_ui(self, frame):
         """In developement"""
         self.grid_maker(row=1, column=1, widget=frame)
         Label = customtkinter.CTkLabel(master=frame, text="I'm UDP scanner options and current in developmet, yayy!")
         Label.grid(row=0, column=0, sticky="nsew")
      
      def UDP_scan(self):
         """Implement"""


app = Gmap()
app.mainloop()


