import socket
import os
import struct
from ipaddress import ip_address, ip_network
import threading
from time import sleep

"""NOTE: This tool was created on windows, if in use on other OSes, adjustments may need to be made"""

# host to listen on
HOST = "192.168.100.115"
PORT = 0

tgt_subnet = "192.168.100.0/24"

# magic we'll check ICMP responses for
tgt_message = "TORMA!"


def udp_sender(sub_net, magic_message):
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for ip in ip_network(sub_net).hosts():
        sender.sendto(magic_message.encode('utf-8'), (str(ip), 65212))
    sender.close()

#IP class
class IP:
    def __init__(self, buff=None):
       header = struct.unpack('!BBHHHBBH4s4s', buff)
       #bytes
       self.ver = header[0] >> 4
       self.ihl = header[0] & 0xF
       self.tos = header[1]
       self.len = header[2]
       self.id = header[3]
       self.offset = header[4]
       self.ttl = header[5]
       self.protocol_num = header[6]
       self.sum = header[7]
       self.src = header[8]
       self.dst = header[9]
       
       # map protocol constants to their names
       self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}
       # human readable IP addresses
       self.src_address = socket.inet_ntoa(self.src)
       self.dst_address = socket.inet_ntoa(self.dst)
       # human readable protocol
       try:
         self.protocol = self.protocol_map[self.protocol_num]
       except IndexError:
          self.protocol = str(self.protocol_num)
        
    def get_host_addr(self):
        return f"Protcol: {self.protocol} {self.src_address}->{self.dst_address}"

    def get_l4_proto(self):
        return f"Layer 4 Protocol -> {self.protocol}"
    
    def get_proto_num(self):
        return self.protocol_num
    
    def get_ip_stream_info(self):
        #calculate where our ICMP packet starts
        print('Protocol: %s %s -> %s' % (self.protocol,self.src_address, self.dst_address))
        print(f'Version: {self.ver}')
        print(f'Header Length: {self.ihl}\n TTL: {self.ttl}')
        


class ICMP:
    def __init__(self, buff=None): 
        header = struct.unpack('!BBHHH', buff)
        self.type = header[0]
        self.code = header[1]
        self.sum = header[2]
        self.id = header[3]
        self.seq = header[4]
    
    def icmp_info(self):
        return ("ICMP -> Type: %d Code: %d" % (self.type,self.code))

 


def sniff():
     with socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_IP) as s:
       try:
         s.settimeout(3)
         #Binds raw socket to address below
         s.bind((HOST,PORT))
         #Sets socket options, Socket level is layer 3 in this case, i.e IP
         s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
         #Checks if OS is windows, upon True it enables promiscuos mode
         if os.name == "nt":
            print("[+]Windows nt detected as OS")
            print("[+]Turning on promiscuos mode")
            s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
         #Sniff all packets arriving on interface until KeyboardInterrupt
         while True: 
            #Retrieves data from socket, i.e the packet, note that it returns a tuple(Bytes,IP)
            raw_buf= s.recvfrom(2**16)
            #Since socket has option IP_HDRINCL, the IP header is included in the data
            #IP object is instantiated to work with the data retrieved, see defined IP class above
            pkt= IP(raw_buf[0][0:20])
            #Checks if upper layer is ICMP
            if pkt.protocol == "ICMP":
               #print(pkt.get_host_addr())
               #calculate where our ICMP packet starts
               offset = pkt.ihl * 4
               buf = raw_buf[0][offset:offset + 8]
               #create our ICMP object to make it easier to work with 
               icmp_header = ICMP(buf)
     
               #now check for the TYPE 3 and CODE 3 which indicates
               #a host is up but no port available to talk to           
               if icmp_header.code == 3 and icmp_header.type == 3:
                  #print(icmp_header.icmp_info())
                  #check to make sure we are receiving the response 
                  #that lands is in our subnet
                  if ip_address(pkt.src_address) in ip_network(tgt_subnet):
                    #Checks for signature as ICMP reply sends back part of UDP data, see RFC form more details
                     if raw_buf[0][20:][-6:].decode() == tgt_message:
                        print("Host Up: %s" % pkt.src_address)
                    
    
       except socket.timeout as e :
              print(e)
              if os.name == "nt":
                 print("[-]Turning off promiscuos mode")
                 s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
              exit()
       except KeyboardInterrupt:
         if os.name == "nt":
            print("[-]Turning off promiscuos mode")
            s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
         print("User ended program")
         exit()

if __name__ == "__main__":
   udp_thread = threading.Timer(2,udp_sender,args=(tgt_subnet,tgt_message))
   udp_thread.start()
   sniff()