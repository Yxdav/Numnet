import customtkinter
import os


from .network import *


from abc import ABC, abstractmethod
from json import load
from time import sleep, strftime
from tkinter import messagebox

RECON_PATH = "./recon/recon.json"

class Callback(ABC):
      
      @abstractmethod
      def __init__(self, *args, **kwargs):
      	 """Pass additional arguements"""
      
      @abstractmethod
      def __call__(self, event):
      	 """Calls handler function, additionaly parameters may be supplied to handler function"""
      
      @abstractmethod
      def handler(self, *args, **kwargs):
      	  """Implement here"""


class OptionMenu(Callback):
      def __init__(self, *args, **kwargs):
          self.args = args
          self.kwargs = kwargs
          
      def __call__(self, choice ):
          self.handler(choice)

      def handler(self, choice):
          
          self.app = self.args[0]
         
         
          if self.app.CURRENT_MODULES.get("current") is None:
             self.app.CURRENT_MODULES.update({"current":choice})
             self.app.MODULE_DICT.get(choice)(self.app.inner_user_options_frame)

          
          if self.app.CURRENT_MODULES.get("current") == choice:
             pass
          else:
             for child in self.app.inner_user_options_frame.grid_slaves():
                 child.destroy()
                
             self.app.MODULE_DICT.get(choice)(self.app.inner_user_options_frame)
             
                
          self.app.CURRENT_MODULES.update({"current":choice})
          
          


class ModifyLabelValues(Callback):

      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self):
          self.handler()
      
      def handler(self):
          ip_value_label = self.args[0]
          net_value_label = self.args[1]
          mac_value_label = self.args[2]

          new_ip_value = get_local_ip()
          new_net_value = get_local_net_addr(new_ip_value)
          new_mac_value =  get_mac()

          ip_value_label.configure(text=new_ip_value)
          net_value_label.configure(text=new_net_value)
          mac_value_label.configure(text=new_mac_value)

class GetSwitchValue(Callback):

      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self):
          self.handler()
      
      def handler(self):
          switch_value = self.args[0].get()
          return switch_value

class ResizeTextBox(Callback):

      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self, event):
          self.handler(event, self.args[0])

      def handler(self, event, textbox):
          if event.delta > 0:
             textbox.configure(font=("roboto",textbox.cget("font")[1]+1))
          elif event.delta < 0:
             textbox.configure(font=("roboto",textbox.cget("font")[1]-1))


class MoveCompIcons(Callback):
      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self, event):
          self.handler(event, self.args[0], self.args[1], self.args[2], self.args[3])

      def handler(self, event, root, tag, text_tag, line_tag):
          self.root = root
          self.event = event
          self.tag = tag
          self.text_tag = text_tag
          self.line_tag = line_tag
          
          self.root.my_canvas.moveto(self.tag, self.root.my_canvas.canvasx(self.event.x-50), self.root.my_canvas.canvasy(self.event.y-50))
          self.root.my_canvas.moveto(self.text_tag, self.root.my_canvas.canvasx(self.event.x-50), self.root.my_canvas.canvasy(self.event.y+40))

          x = ((self.root.my_canvas.bbox(self.tag)[2] - self.root.my_canvas.bbox(self.tag)[0])/2)+ self.root.my_canvas.bbox(self.tag)[0]
          y = ((self.root.my_canvas.bbox(self.tag)[3] - self.root.my_canvas.bbox(self.tag)[1])/2)+ self.root.my_canvas.bbox(self.tag)[1]
          x2 = ((self.root.my_canvas.bbox("router")[2] - self.root.my_canvas.bbox("router")[0])/2)+ self.root.my_canvas.bbox("router")[0]
          y2 = ((self.root.my_canvas.bbox("router")[3] - self.root.my_canvas.bbox("router")[1])/2)+ self.root.my_canvas.bbox("router")[1]

          self.root.my_canvas.coords(self.line_tag, x, y, x2, y2)


class SaveFile(Callback):
      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self, event):
          self.handler(event)

      def handler(self, event):
          try:
            if not os.path.exists("./Results/"):
              os.mkdir("./Results")
            else:
               filename = "Results/%s.json"%strftime('%Y-%m-%d %H-%M-%S')
               with open(RECON_PATH, "r") as fp:
                    info = fp.read()
               with open(filename, "w") as fp:
                    fp.write(info)
            messagebox.showinfo(title="Success!", message="Data has been saved to the Results folder")

          except Exception as e:
                   messagebox.showerror(title="Error", message=f"{e}\n Report issue to https://github.com/Haz3l-cmd/Netnum")

class HelpMenu(Callback):

      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self,event):
          self.handler(event)
      
      def handler(self, event):
          HELP_MSG = "<Ctrl+s> --> Save \n<Ctrl+Scroll> --> Zo0m in/out\n<Ctrl+l> --> Clear info panel\n<Ctrl+w> --> Open map(May be closed if unused\n<Ctrl+h> --> Help"
          messagebox.showinfo(title="Stuck?!", message=HELP_MSG)
