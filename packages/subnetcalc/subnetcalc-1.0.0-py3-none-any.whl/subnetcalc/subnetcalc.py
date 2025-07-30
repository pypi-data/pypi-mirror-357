#!/usr/bin/env python3

class Ip():
    def __init__(self,ip_raw):
        if not '/' in ip_raw:
            self.ip_raw = ip_raw+'/24'
        else:
            self.ip_raw = ip_raw

        self.ip = ip_raw.split('/')[0]
        self.bin_ip = self.ip_to_bin(self.ip)
        self.cidr = self.ip_raw.split('/')[1]
        self.bin_netmask = self._calc_netmask()
        self.netmask = self.bin_to_ip(self.bin_netmask)
        self.bin_network_ip = self._calc_bin_network_ip()
        self.network_ip = self.bin_to_ip(self.bin_network_ip)
        self.bin_broadcast = self._calc_bin_broadcast()
        self.broadcast = self.bin_to_ip(self.bin_broadcast)
        if int(self.cidr) <= 30:
            self.min_max_ip = self._calc_min_max()
            self.available_ips = self._calc_available_ip()
        
        elif int(self.cidr) <= 32:
            self.min_max_ip = None
            self.available_ips = None

        else:
            raise ValueError(f"Invalid CIDR: {self.cidr}")

    def _calc_netmask(self):
        netmask = ""
        netmask += "1"*(int(self.cidr.strip('/')))
        netmask += "0"*(32-int(self.cidr.strip('/')))
        return netmask
    
    @staticmethod
    def bin_to_ip(bin):
        bits = [128,64,32,16,8,4,2,1]
        first_octet = bin[:8]
        second_octet = bin[8:16]
        third_octet = bin[16:24]
        fourth_octet = bin[24:32]
        
        first = 0
        second = 0
        third = 0
        fourth = 0

        for i,bit in zip(first_octet,bits):
            first += int(i)*bit
        for i,bit in zip(second_octet,bits):
            second += int(i)*bit
        for i,bit in zip(third_octet,bits):
            third += int(i)*bit
        for i,bit in zip(fourth_octet,bits):
            fourth += int(i)*bit

        return f'{first}.{second}.{third}.{fourth}'

    @staticmethod
    def ip_to_bin(ip):
        first_dec_octet = ip.split('.')[0]
        second_dec_octet = ip.split('.')[1]
        third_dec_octet = ip.split('.')[2]
        fourth_dec_octet = ip.split('.')[3]

        first_octet = bin(int(first_dec_octet)).split('b')[1]
        first_octet = "0" * (8-len(first_octet)) + first_octet

        second_octet = bin(int(second_dec_octet)).split('b')[1]
        second_octet = "0" * (8-len(second_octet)) + second_octet

        third_octet = bin(int(third_dec_octet)).split('b')[1]
        third_octet = "0" * (8-len(third_octet)) + third_octet

        fourth_octet = bin(int(fourth_dec_octet)).split('b')[1]
        fourth_octet = "0" * (8-len(fourth_octet)) + fourth_octet

        return f'{first_octet}{second_octet}{third_octet}{fourth_octet}'

    def _calc_bin_network_ip(self):
        bin_network_ip = ""
        for ip,netmask in zip (self.bin_ip,self.bin_netmask):
            if ip == "1" and netmask == "1":
                bin_network_ip += "1"
            else:
                bin_network_ip += "0"

        return bin_network_ip

    def _calc_bin_broadcast(self):
        broadcast = self.bin_ip[:int(self.cidr)]
        broadcast += "1" * (32-int(self.cidr))
        return broadcast

    def _calc_min_max(self):
        fragmented_network_ip = self.network_ip.split('.')
        fragmented_broadcast = self.broadcast.split('.')

        fragmented_network_ip[3] = str(int(fragmented_network_ip[3])+1)
        fragmented_broadcast[3] = str(int(fragmented_broadcast[3])-1)

        min_ip = '.'.join(fragmented_network_ip)
        max_ip = '.'.join(fragmented_broadcast)
        return (min_ip,max_ip)

    @staticmethod
    def ip_to_dec(ip):
        ip_splitted = ip.split('.')
        entero = 0

        for bit,octet in zip ([24,16,8,0],ip_splitted):
            entero += int(octet)<<bit

        return entero

    @staticmethod
    def dec_to_ip(entero):
        entero = int(entero)
        return '.'.join(str((entero>>i) & 255) for i in [24,16,8,0])

    def _calc_available_ip(self):
        min_ip_int = self.ip_to_dec(self.min_max_ip[0])
        max_ip_int = self.ip_to_dec(self.min_max_ip[1])

        return (self.dec_to_ip(i) for i in range(min_ip_int,max_ip_int+1))

    def __str__(self):
        return f"""
[+] IP --> {self.ip}
[+] CIDR --> {self.cidr}
[+] Netmask --> {self.netmask}
[+] Network ID --> {self.network_ip}
[+] Broadcast --> {self.broadcast}
[+] Min / Max IP --> {str(self.min_max_ip)}
"""

if __name__ == '__main__':
    import argparse
    
    def get_arguments():
        parser = argparse.ArgumentParser(description="Fast IP Subnetting Calculator")
        parser.add_argument('-i','--ip',dest='ip',required=True,help='192.168.11.1/24')
        args = parser.parse_args()
        return Ip(args.ip)

    ip = get_arguments()
    print(ip)