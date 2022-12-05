import socket
import ipaddress
import subprocess
import uuid

def get_local_ip()->str: 
    """Gets the local IP address of the user
       
       :Return: IP address of user
    """
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
		 s.connect(("192.168.1.1",2))
		 local_ip = s.getsockname()[0]
		 return local_ip

def get_local_net_addr(ip_addr:str)->str:
    """Calculates network address from locall IP

       :param ip_addr: Local IP, obtained from get_local_ip()

       :Return: Network addresse
    """
    ip = ip_addr
    proc = subprocess.Popen('ipconfig',stdout=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if ip.encode() in line:
           break
    mask = proc.stdout.readline().rstrip().split(b':')[-1].replace(b' ',b'').decode()
    ipv4_network_addr = str(ipaddress.IPv4Network(f"{ip}/{mask}", strict=False))
    return ipv4_network_addr

def get_mac()->str : 
    """Returns MAC address
    """
	mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
	return mac

def all_hosts(net_addr)->list[str]:
    """Returns a list of all host within a subnet
    """
    hosts_list = [str(ip) for ip in ipaddress.IPv4Network(net_addr).hosts()]
    return hosts_list


