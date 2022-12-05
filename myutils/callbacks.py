import customtkinter
import os
import json

from .network import *


from abc import ABC, abstractmethod
from time import sleep, strftime
from tkinter import messagebox
from sys import stderr

ROUTER_PATH ="./assets/images/router.png"
RECON_PATH = "./recon/recon.json"

class Callback(ABC):
      """This abstract method represents the blueprint for following sub classes. Instances
         if this class are callables, this allows us to circumvent the limation of not being able 
         to pass arguemnts to callbacks, e.g if we want to  invoke the callback with the arguement text="hello" 
         to customTkinter.CTkButton(master=self), instead of customTkinter.CTkButton(master=self, command=close),
         we would do customTkinter.CTkButton(master=self, command=CloseClass(text="hello")), in this case the callback will be like this :
         CloseClass(text="hello")(), i.e CloseClass(text="hello").__call__(self). As you can see, this gives us much more control and flexibility.
      """
      
      @abstractmethod
      def __init__(self, *args, **kwargs):
      	 """Pass additional arguements"""
      
      @abstractmethod
      def __call__(self, event):
      	 """Calls handler function, additionaly parameters may be supplied to handler function"""
      
      @abstractmethod
      def handler(self, *args, **kwargs):
      	  """Implement here"""


class OptionMenuUI(Callback):
      """This subclass of Callback is responsible for changing self.inner_user_options_frame,
          which is the frame that allows user to change module options, with respect to the selected
          value(module) in the drop down menu.
      """
      def __init__(self, *args, **kwargs):
          self.args = args
          self.kwargs = kwargs
          
      def __call__(self, choice ):
          self.handler(choice)

      def handler(self, choice):
          # Here self.app refers to the root/main window, which would be "self" in netnum.py
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
          
          
class ResizeTextBox(Callback):
      """This sub class is responsible for the zooming in and out of info panel"""
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
      """This sub class is responsible for saving information gathered to the Resources folder
        *NOTE TO SELF* : Remove hard values
      """
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
                   messagebox.showerror(title="Error", message=f"{e}\n Report issue to https://github.com/Haz3l-cmd/Numnet")

class HelpMenu(Callback):
      """This sub class is responsible for the help menu"""
      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self,event):
          self.handler(event)
      
      def handler(self, event):
          HELP_MSG = "<Ctrl+s> --> Save \n<Ctrl+Scroll> --> Zo0m in/out\n<Ctrl+l> --> Clear info panel\n<Ctrl+w> --> Open map(May be closed if unused\n<Ctrl+h> --> Help"
          messagebox.showinfo(title="Stuck?!", message=HELP_MSG)

class InitRouter(Callback):
      """This subclass ensures that the router is always present in the diagram"""

      def __init__(self, *args, **kwargs):
         self.args = args 
         self.kwargs = kwargs

      def __call__(self,choice):
          self.handler(choice)
      
      def handler(self, choice):
          root = self.args[0]
          temp_dict = {choice: "None"}
          try:
            with open(RECON_PATH, "r") as fp:
                 data = json.load(fp)
            if data:
               key_to_rplc = None
               for key,val in data.items():
                  if val == "None":
                     key_to_rplc = key
               data.pop(key_to_rplc)
               with open(RECON_PATH, "w") as fp:
                    data.update(temp_dict)
                    json.dump(data, fp, indent=4)
           
              
          except json.decoder.JSONDecodeError:
                 with open(RECON_PATH, "w") as fp:
                    json.dump(temp_dict, fp, indent=4)
           