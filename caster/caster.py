
from socket import * 
import os,io,sys
from multiprocessing import Process
import struct 
import json
import datetime
import time
import locale
import requests
from threading import Thread
import ssl
from multiprocessing import Queue

def prep_data(x):
    x=x.encode()
    chunks = []
    size = 32
    i = 0 
    while(1):
        if(i>=len(x)):
            break
        chunk = x[i:i+size]
        chunks.append(chunk)
        i+=size

    return chunks
    

class Communicator:
    def __init__(self,queue_ip,server_ip,server_port,queue_port) -> None:
        
        self.queue_ip = queue_ip
        self.queue_port = queue_port
        self.port =server_port
        self.server_ip = server_ip
        self.cont = ssl._create_unverified_context()
        self.device_info = None


    def add_post_data(self,data,type):

        req = ""
        req+="POST /"+type+" HTTP/1.1\r\n"
        req+="Host: "+self.server_ip+"\r\n"
        req+="Content-Type: application/json\r\n"
        req+="Content-Length: "+str(len(data))
        req+="\r\n\r\n"

        return req


    def _get_device_queue(self):
        
        if(self.device_info == None):
            print("*** Connecting to the network...")
            ret = self._add_device_to_server()
            if(ret == -1):
                print("*** This device is already connected on the network.")
               

        request = self.add_post_data(str(self.device_info),"getQueue")
        request += str(self.device_info)
        request=request.encode()
       
        sockd = create_connection((self.server_ip,self.queue_port))
        ssock = self.cont.wrap_socket(sock=sockd,server_hostname=self.server_ip)    
        ssock.write(request)
        resp = b""
        while(1):
            dat = ssock.recv(4)
            resp+=dat
            if(b"\r\n\r\n" in resp):
                break
        
        resp_length= 0 
        resp_message = ""
        dt = resp.split(b"\r\n\r\n")
        if(len(dt) > 1 ):
            resp_length+=len(dt[1])
            resp_message+=dt[1].decode()

        resp = resp.split(b"\r\n")
        for dat in resp:
            dat = dat.lower().split(b":")
            if(dat[0] ==b"content-length"):
                resp_length=(int(dat[1])-resp_length)
                break
        
        for _ in range(resp_length):
            msg = ssock.recv(1).decode()
            resp_message+=(msg)
       


        ssock.close()
        ssock.detach()
        
        return resp_message


    def _set_queue_for_device(self,url):

        try:
            assert(( self.device_info != None ) )
        except AssertionError as e:
            print("Device not initialized")
            exit(1)

        sockd = create_connection((self.server_ip,self.queue_port))
        ssock = self.cont.wrap_socket(sock=sockd,server_hostname=self.server_ip)    
        
        dotd = self.device_info.copy()
        dotd['url'] = url
        dotd = str(dotd).replace("'","\"")

       
        request = self.add_post_data(dotd,"setQueue")
        
        request += dotd
        request=request.encode()

        ssock.write(request)

        print("Queue set.")
        

       

    def _add_device_to_server(self):

        hostname = os.getenv("LOGNAME")
        req = requests.get("https://ifconfig.co/json").json()
        ip = req['ip']


        sockd = create_connection((self.server_ip,self.port))
        print(sockd.fileno())

        ssock = self.cont.wrap_socket(sock=sockd,server_hostname=self.server_ip)
        print(ssock.fileno())

        data={
            "dev_info":[
                hostname,ip
            ]
        }

        self.device_info  = data
        dat= str(self.device_info).replace("'","\"")
        req ="POST /add_device HTTP/1.1\r\nHost: 127.0.0.1:64\r\nUser-Agent: Wget/1.21.3\r\nAccept: */*\r\nAccept-Encoding: identity\r\nConnection: Keep-Alive\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "+str(len(str(data)))+"\r\n\r\n"
        ssock.write(req.encode())
        ssock.write(dat.encode())
        resp=b""

        while(1):
            
            dat = ssock.recv(4)
            resp+=dat
            if(b"\r\n\r\n" in dat):
                break   
        
        resp = resp.decode()

        headers = resp.split("\r\n")
        for header in headers:
            header = header.lower().split(":")
            if(header[0] == "content-length"):
                lend =int(header[1])
       
                dat = b""
                for _ in range(lend):
                    dat  += ssock.recv(1)
               
                dat = json.loads(dat)['result']
                ssock.close()
                ssock.detach()

                if(dat == "INVALID_PARAMS" or dat == "DEVICE_ALREADY_ADDED"):
                    return -1
                else:

                    return 1
                


IP = "127.0.0.1"
port=int(os.getenv("SERVER_PORT"))
q_port=int(os.getenv("QUEUE_PORT"))

comm = Communicator(IP,IP,port,q_port)
comm._add_device_to_server()
#comm._set_queue_for_device("https://www.youtube.com/watch?v=Zo2pMNSkIvE&ab_channel=DrakeMedia")

msg =None

while(1):

    msgd = comm._get_device_queue()
    print("Queue:" ,msgd,msg)
    if(msgd != "none " and msgd != "DEVICE_NOT_ADDED" and msgd != msg ):
        msg = msgd
        os.system(f"open {msg}")
    time.sleep(5)




