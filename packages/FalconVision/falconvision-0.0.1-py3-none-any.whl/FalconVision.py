import argparse
import binascii
import ipaddress
import json
import re
import socket
import struct
import warnings
from clear import clear

class TheSilent:
    def __init__(self,host,port,protocol):
        self.host = host
        self.port = port
        self.protocol = protocol

    def java(self):
        hits = {}
        if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}",self.host):
            hosts = list(ipaddress.ip_network(args.host,strict=False).hosts())
            for host in hosts:
                print(f"Checking: {host}:{self.port}")
                handshake = binascii.unhexlify("00") + b"".join([bytes([(b := (self.protocol >> 7 * i) & 0x7F) | (0x80 if self.protocol >> 7 * (i + 1) else 0)]) for i in range(5) if (self.protocol >> 7 * i)]) + struct.pack(">b",len(str(host))) + str(host).encode() + struct.pack(">H", self.port) + b"\x01"
                packets = [struct.pack(">b",len(handshake)) + handshake, binascii.unhexlify("0100")]
                try:
                    s = socket.socket()
                    s.settimeout(10)
                    s.connect((str(host),self.port))
                    for i in packets:
                        s.send(i)
                    response = ""
                    while True:
                        new_response = s.recv(2**8).decode("ascii",errors="ignore").replace("\\n","").replace("\n","").replace(" ","")
                        if new_response:
                            response += new_response
                        else:
                            break

                    if response:
                        data = "{" + "".join(response.split("{")[1:]).lower()
                        if not data.endswith("}"):
                            data += "}"
                            
                        max_players = int(re.sub(r"[\"\'\:]","",re.findall(r"max(.+)(?=[,])",data)[0]).split(",")[0])
                        online_players = int(re.sub(r"[\"\'\:]","",re.findall(r"online(.+)(?=[,])",data)[0]).split(",")[0])
                        protocol = int(re.sub(r"[\"\'\:]","",re.findall(r"protocol(.+)(?=[\}])",data)[0]).split("}")[0])
                        hits.update({self.host:{"max players":max_players,"online players":online_players,"protocol":protocol,"favicon":favicon}})
                except:
                    pass

        else:
            print(f"Checking: {self.host}:{self.port}")
            handshake = binascii.unhexlify("00") + b"".join([bytes([(b := (self.protocol >> 7 * i) & 0x7F) | (0x80 if self.protocol >> 7 * (i + 1) else 0)]) for i in range(5) if (self.protocol >> 7 * i)]) + struct.pack(">b",len(self.host)) + self.host.encode() + struct.pack(">H", self.port) + b"\x01"
            packets = [struct.pack(">b",len(handshake)) + handshake, binascii.unhexlify("0100")]
            try:
                s = socket.socket()
                s.settimeout(10)
                s.connect((self.host,self.port))
                for i in packets:
                    s.send(i)
                response = ""
                while True:
                    new_response = s.recv(2**8).decode("ascii",errors="ignore").replace("\\n","").replace("\n","").replace(" ","")
                    if new_response:
                        response += new_response
                    else:
                        break

                if response:
                    data = "{" + "".join(response.split("{")[1:]).lower()
                    if not data.endswith("}"):
                        data += "}"
                        
                    max_players = int(re.sub(r"[\"\'\:]","",re.findall(r"max(.+)(?=[,])",data)[0]).split(",")[0])
                    online_players = int(re.sub(r"[\"\'\:]","",re.findall(r"online(.+)(?=[,])",data)[0]).split(",")[0])
                    protocol = int(re.sub(r"[\"\'\:]","",re.findall(r"protocol(.+)(?=[\}])",data)[0]).split("}")[0])
                    hits.update({self.host:{"max players":max_players,"online players":online_players,"protocol":protocol,"favicon":favicon}})
            except:
                pass

        hits = json.dumps(hits,indent=4,sort_keys=True)
        return hits

if __name__ == "__main__":
    clear()
    parser = argparse.ArgumentParser()
    parser.add_argument("-host",required=True)
    parser.add_argument("-port",default=25565)
    parser.add_argument("-protocol",default=770)
    args = parser.parse_args()
    hits = TheSilent(args.host,args.port,args.protocol).java()
    print(hits)
