



# Numnet
![image](https://user-images.githubusercontent.com/91953982/205681154-7d5e7dfb-96ce-4646-a1cd-de8c09ce1827.png)
## About
Numnet is a network enumeration tool written entirely in python and provides the user with a graphical interface. Numnet is easy and fast to use due to its built-in shortcuts, see below. Moreover, it also allows you to visualise the network, see the demo below.

## Installation guide
 ***Note that after running the *requirements.txt*, it should run out of the box. The installation is pretty simple, just copy and paste the command/s below, you may wish to run it in a virtual envinronment, see [here](https://docs.python.org/3/library/venv.html)***
    
-    `pip3 install -r requirements.txt`

## Demo 
https://user-images.githubusercontent.com/91953982/205724566-5499f469-c436-4ee4-8ec4-f265e236c905.mp4

## File structure
- assets/images -> Contain images
- modules/ -> Contain the modules that can be used, current only an ARP scan is possible
- Module Documentation/ -> Documentation about each individual modules
- myutils/ -> Contains classes and functions to facilate  this project, the individual files in *myutils* are documented
- recon/ -> Where gathered information is temporarily stored during runtime
- Results/ -> This folder is created after the user presses `Ctrl+s` to save the data aquired. The data is saved in a JSON format and the file name is the timestamp of when it was saved/created

## Note
- This software is current in a "pre pre-alpha state" so please feel free to report any bugs
- The ARP_scan module currently only scans the network but you may have seen additional parameters which are not used. These parameters will be used in the next version of Netnum where ARP spoofing will be implemented and the UDP_scan  will be made available

## Usage
- `Ctrl+h` --> Causes help menu to pop up
- `Ctrl+s` --> Save gathered information as as json file in `Resources` folder.(This folder may or may not be already there, nonetheless it will automatically created)
- `Ctrl+w` --> Opens the network mapper, this allows you to visualise the network
- `Ctrl+Scroll` --> Zoom in/out of info panel
- `Ctrl+l` --> Clear info panel


---
# Warning
- *This program has only been tested on windows so far, hence Linux users or users from other operating systems may experience compatibility issues. However, we assure we are working to make sure that this program can run on almost all platforms*
- If the program was not closed proporly and you experience some issue, try deleting /recon/recon.json
- This is the stable Version

