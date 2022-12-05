import customtkinter
import threading
import sys
import random
import json

#Custom modules
from myutils.callbacks import *
from myutils.network import *
from modules.ARP_scan import *

from typing import Callable
from time import sleep
from contextlib import contextmanager
from tkinter import Canvas, messagebox, PhotoImage
from PIL import Image, ImageTk

RECON_PATH = "./recon/recon.json"
ROUTER_PATH ="./assets/images/router.png"
REFRESH_PATH ="./assets/images/refresh.png"
COMP_PATH = "./assets/images/computadora.png"
EXIT_MSG = "Are you sure to want to exit, doing so will not save gathered information in /recon/recon.json. Press ctrl+s if you want to save. The information will be stored in the results folder. Report issue to https://github.com/Haz3l-cmd/Netnum"


class Gmap(customtkinter.CTk):
      
      #Constants for info window/frame
      IP = get_local_ip()
      NET_ADDR = get_local_net_addr(IP)
      MAC = get_mac()
      hosts_list = all_hosts(NET_ADDR)
      hosts_list.insert(0, "None")
      #Internals constants for configuration purposes
      MODULE_DICT:dict[str:Callable] = {}
      CURRENT_MODULES = {"current": None}
      
      #Mapper constants
      COUNT = 0
      TAG_TO_ICON = {}
      
      #Internal constants for root window
      _WINDOW_DIMENSION = "700x400"
      _WINDOW_TITLE  = "NetNum"
      
      #Internal constants for widgets
      PADDING = 5 
      LABEL_FONT_SIZE = 16
      CENTER = "nsew"

      def __init__(self):
          super().__init__()
          self.MODULE_DICT = {"Arpy": self.ARP_options_ui,
                              "UDP Scan": self.UDP_options_ui}
          
          self.wm_state('zoomed')
          # self.geometry(self._WINDOW_DIMENSION)
          self.title(self._WINDOW_TITLE)
          self.protocol("WM_DELETE_WINDOW", self.on_closing) 
          self.warning()
          self.grid_maker(widget=self)

  
          
          
         
       

      
      def warning(self):
          self.warning_frame = customtkinter.CTkFrame(master=self)
          self.warning_frame.pack(expand=True, fill="both")
          self.grid_maker(row= 3, column=3, weight=1, widget=self.warning_frame)


          self.warning_label = customtkinter.CTkLabel(master=self.warning_frame, text="This project was created solely for learning purposes and not otherwise. I am not responsible for your actions.", font=("",15))
          self.warning_label.grid(row=1, column=1, sticky="nsew")

          self.warning_button = customtkinter.CTkButton(master=self.warning_frame, text="Continue", command=self.clear_root)
          self.warning_button.grid(row=2, column=1, sticky="n")

     

      def clear_root(self):
          for child in self.children.copy().values(): 
              child.destroy()
          self.setup()
      
      @contextmanager
      def delete(self):
          try:
             self.inner_info_panel_text_box.configure(state="normal")
             yield self.inner_info_panel_text_box
          
          finally:
             self.inner_info_panel_text_box.configure(state="disabled")

      def setup(self):
          
     
          
          #This frame is split into two, it consits of two child frames, see below
          # self.user_frame = customtkinter.CTkFrame(master=self)
          # self.user_frame.grid(row=0, column=1, padx=self.PADDING, pady=self.PADDING, sticky=self.CENTER)
          # self.grid_maker(row=1, column=2, widget=self.user_frame)
          
          #This frame allows the user to choose a module
          self.inner_user_select_frame = customtkinter.CTkFrame(master=self)
          self.inner_user_select_frame.grid(row=0, column=0, sticky=self.CENTER, padx=self.PADDING, pady=self.PADDING)
          self.grid_maker(widget=self.inner_user_select_frame)
           
          self.select_module_label = customtkinter.CTkLabel(master=self.inner_user_select_frame, text="Select module : ", font=("roboto",self.LABEL_FONT_SIZE))
          self.select_module_label.grid(row=0, column=0, sticky="se")

          self.module_drop_menu = customtkinter.CTkOptionMenu(master=self.inner_user_select_frame, values=list(self.MODULE_DICT.keys()))
          self.module_drop_menu.grid(row=0, column=1,sticky="sw")

        
          self.inner_user_options_frame = customtkinter.CTkFrame(master=self)
          self.inner_user_options_frame.grid(row=0, column=1, sticky=self.CENTER, padx=self.PADDING, pady=self.PADDING)



          # self.info_panel = customtkinter.CTkFrame(master=self.info_frame)
          # self.info_panel.pack( padx=self.PADDING, pady=self.PADDING,)

          self.inner_info_panel_text_box = customtkinter.CTkTextbox(master=self, font=("roboto",15))
          self.inner_info_panel_text_box.grid(row=1, column=0,columnspan=2, sticky=self.CENTER, padx=self.PADDING, pady=self.PADDING)
          self.inner_info_panel_text_box.insert(index="1.0", text="This panel provides information about modules")
          self.inner_info_panel_text_box.configure(state="disabled")

          





          #After initialising all necessary widgets
          self.module_drop_menu.configure(command=OptionMenu(self))
          self.inner_info_panel_text_box.bind("<Control-MouseWheel>", ResizeTextBox(self.inner_info_panel_text_box))
          
          # self.create_toplevel()
          
          """Configure the mapper frame, using canvas, see debug.py for a refresher""" 
        
          self.bind("<Control-l>", self.clear)
          self.bind("<Control-w>", self.create_toplevel)
          self.bind("<Control-s>", SaveFile())
          self.bind("<Control-h>", HelpMenu())
        
  
          
          

          


      def on_closing(self):

          if messagebox.askokcancel("Quit", EXIT_MSG):
             with open(RECON_PATH, "w") as fp:
                  pass
             self.destroy()
             sys.exit()    
      
      def clear(self, event):

          with self.delete() as text_box:
               text_box.delete("1.0", "end")
         
      
      def grid_maker(self, row:int = 2, column:int =2 , weight:int = 1, widget=None):
          for row in range(row):
              widget.rowconfigure(row, weight=weight)
              
          
          for column in range(column):
              widget.columnconfigure(column, weight=weight)

      def create_toplevel(self, *args):
           self.window = customtkinter.CTkToplevel(self)
           self.window.geometry("400x200")
           self.my_canvas = Canvas(master=self.window,bg="black")
           self.my_canvas.pack(expand=True, fill="both")
          
          
          
           self.my_canvas.bind("<Button-3>", self.scan)
           self.my_canvas.bind("<Button3-Motion>", self.drag)
           self.my_canvas.bind("<Motion>", self.display_coords)
           self.my_label = customtkinter.CTkLabel(master=self.my_canvas, text="X: None Y: None", height=20, width=100)
           self.my_label.pack(padx="10px", pady="10px", anchor="ne")
           self.refresh_map_button = customtkinter.CTkButton(master=self.my_canvas, text="Refresh!", command=self.map_refresh, height=30, width=30)
           self.refresh_map_button.pack(padx=self.PADDING, pady=self.PADDING, anchor="ne")
           self.my_canvas.bind("<Control-s>", SaveFile())
           

      def map_refresh(self):
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
                if data.get(key)[1] == "Gateway":
                  self.generate_icon(ROUTER_PATH, f"IP: {key}\n MAC:{data.get(key)[0]}")
                else:
                  self.generate_icon(COMP_PATH, f"IP: {key}\nMAC:{data.get(key)}")

            
          except json.decoder.JSONDecodeError:
                 pass
          

         
      
      def scan(self, event):
          self.my_canvas.scan_mark(event.x, event.y)

      def drag(self, event):
          self.my_canvas.scan_dragto(event.x, event.y, gain=2)

      def display_coords(self, event):
          self.my_label.configure(text=f"X: {self.my_canvas.canvasx(event.x)} Y:{self.my_canvas.canvasy(event.y)}")

      def generate_icon(self, path, text):
          if path == COMP_PATH:
            img = Image.open(COMP_PATH)
            resized_image = img.resize((100,100))
            self.image = ImageTk.PhotoImage(resized_image)
            self.image = self.image
            # self.TAG_TO_ICON.update({self.COUNT: self.image })
            self.my_image = self.my_canvas.create_image(random.randrange(0, 500-50),random.randrange(0, 700-50), image=self.image)
            self.TAG_TO_ICON.update({self.my_image: self.image })
            x = ((self.my_canvas.bbox(self.my_image)[2] - self.my_canvas.bbox(self.my_image)[0])/2)+ self.my_canvas.bbox(self.my_image)[0]
            y  = ((self.my_canvas.bbox(self.my_image)[3] - self.my_canvas.bbox(self.my_image)[1])/2)+ self.my_canvas.bbox(self.my_image)[1]
            x2  = ((self.my_canvas.bbox("router")[2] - self.my_canvas.bbox("router")[0])/2)+ self.my_canvas.bbox("router")[0]
            y2  = ((self.my_canvas.bbox("router")[3] - self.my_canvas.bbox("router")[1])/2)+ self.my_canvas.bbox("router")[1]
            self.line_tag = self.my_canvas.create_line(x, y, x2, y2, fill="white")
            x3 = self.my_canvas.bbox(self.my_image)[0]
            y3 = self.my_canvas.bbox(self.my_image)[3]
            self.text_tag = f"{self.my_image}-Complement"
            self.my_canvas.tag_bind(self.my_image,"<Button1-Motion>", MoveCompIcons(self, self.my_image, self.text_tag, self.line_tag ), add="+")
            self.my_canvas.create_text(x3, y3, text=text, fill="white",tags=self.text_tag, anchor="nw")
           
          else:
            canvas_width =self.my_canvas.winfo_width()
            canvas_height = self.my_canvas.winfo_height()
            img = Image.open(ROUTER_PATH)
            resized_image = img.resize((100,100))
            self.image = ImageTk.PhotoImage(resized_image)
            self.image = self.image
            # self.TAG_TO_ICON.update({self.COUNT: self.image })
            self.my_image = self.my_canvas.create_image(canvas_width/2, canvas_height/2, image=self.image, tags="router")
            self.TAG_TO_ICON.update({self.my_image: self.image })
            self.line_tag = self.my_canvas.create_line(0, 0, 0, 0, fill="white")
            self.text_tag = f"{self.my_image}-Complement"
            self.my_canvas.tag_bind(self.my_image,"<Button1-Motion>", MoveCompIcons(self, self.my_image, self.text_tag), add="+")
            x1, y1, x2, y2 = self.my_canvas.bbox(self.my_image)
            self.my_canvas.create_text(x1, y2-20, text=text, fill="white",tags=self.text_tag, anchor="nw", width=(x2-x1)+20)
            self.my_canvas.create_text(x1, y2-20, text=None, fill="white",tags=self.text_tag, anchor="nw", width=(x2-x1)+20)
         
      
      def ARP_options_ui(self, frame):
          
          self.grid_maker(row=7, column=3, weight=1, widget=frame,)

          self.target_ip_label = customtkinter.CTkLabel(master=frame, text="Target IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.target_ip_label.grid(row=0, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.target_ip_value = customtkinter.CTkComboBox(master=frame, values=self.hosts_list)
          self.target_ip_value.grid(row=0, column=1, pady=self.PADDING)
        
          
          self.gateway_ip_label = customtkinter.CTkLabel(master=frame, text="Gateway IP :", font=("robot", self.LABEL_FONT_SIZE))
          self.gateway_ip_label.grid(row=1, column=0, pady=self.PADDING, padx=self.PADDING,)
          self.gateway_ip_value = customtkinter.CTkComboBox(master=frame, values=self.hosts_list)
          self.gateway_ip_value.grid(row=1, column=1, pady=self.PADDING)
          
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
          
      def ARP_scan(self):
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
         self.grid_maker(row=1, column=1, widget=frame)
         Label = customtkinter.CTkLabel(master=frame, text="I'm UDP scanner options and current in developmet, yayy!")
         Label.grid(row=0, column=0, sticky="nsew")
      
      def UDP_scan(self):
         """Implement"""


app = Gmap()
app.mainloop()


