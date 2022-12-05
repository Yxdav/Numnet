### While selecting Arpy you might have seen this:
![image](https://user-images.githubusercontent.com/91953982/205690016-9e8f4a7a-b6b9-4e77-9819-6d93031dc015.png)
Let me explain:
- `Target IP` -> Pretty straight forward, if it is set to *None* then the whole network is scanned else only the target IP is scanned
- `Gateway IP` -> Ip address of default gateway, despite having to fill it in. It doesnt't have any effect on the scan. It is only used when performing ARP cache poisoning, which will be added in the next version
- `Interval` -> The number of seconds between gratuitous ARP replies, again It doesnt't have any effect on the scan. It is only used when performing ARP cahce poisoning, which will be added in the next version
- `Threads` -> The number of threads to use when scanning the whole network, only takes effect when Target IP is set to *None* or is empty
- `Two way poisoning` -> Whether to poison cache of target only or both  the target and the router's cache

Congrats!, You now know all the options. I would recommend using wireshark to understand what is actually happening on the wire. 
#### WARNING!!
Do not use this on a network that you do not own!!

