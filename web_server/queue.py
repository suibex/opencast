import ssl
from socket import * 
import os,io,sys
from multiprocessing import Process
import struct 
import json
import datetime
import locale
from threading import Thread
from multiprocessing import Queue


PORT = 448

"""
    POST /getQueue 
    POST /setQueue

    #in queues you will have stored.
    [dev_info(packed),current_playin_url]

"""



class WebQueuer(object):
    def __init__(self) -> None:
        
        self.queues  = [] 

    def return_err_dwd(self,msg):   

        locale.setlocale(locale.LC_TIME,'en_US')
        dat = datetime.datetime.now().strftime(locale.nl_langinfo(locale.D_T_FMT))
        req = ""
        req+="HTTP/1.1 200 OK\r\n"
        req+="Date: "+dat+"\r\n"
        req+="Server:opencast/1.0a\r\n"
        req+="Last-Modified: "+dat+"\r\n"
        req+="Content-Length: "+str(len(msg))+"\r\n"
        req+="Content-Type: application/json\r\n"
        req+="Connection: Closed\r\n\r\n"
        req+=msg
        return req.encode("utf-8") 


    def handle_request(self,conn,addr):
        req = b""
        while(1):
            dat = conn.read(4)
            req+=dat
            if(b"\r\n\r\n" in req):
                break

        req= req.decode()
        req = req.split("\r\n")
        typed =req[0].split(" ")
        if(typed[0] != "POST"):
            conn.write(self.return_err_dwd("ERR"))
        else:   
            jsoned = b""
            method= typed[1].replace("/","")
            if(method == "setQueue"):

                #{dev_info:[],url:[]}
                for param in req:
                    if("Content-Length" in param or "content-length" in param):

                        length = int(param.split(":")[1].replace(" ",""))
                        for i in range(length):
                            jsoned+=conn.recv(1)
                        break

                
                jsoned = json.loads(jsoned)
                print(jsoned)
                self.queues.append([jsoned['dev_info'],jsoned['url']])
                conn.send(self.return_err_dwd("DEVICE_ADDED"))


            if(method == "getQueue"):

                for param in req:
                    if("Content-Length" in param or "content-length" in param):

                        length = int(param.split(":")[1].replace(" ",""))
                        for i in range(length):
                            jsoned+=conn.recv(1)
                        break

                
                jsoned = json.loads(jsoned)
                try:
                    
                    dev_info = jsoned['dev_info']
                    dev_name = dev_info[0]
                    dev_ip = dev_info[1]
                    found_dev= False
                    url = None
                    for dev in self.queues:
                        if(dev[0][0] == dev_name and dev[0][1] == dev_ip):
                            found_dev = True
                            url = dev[1]
                            break
                    if(found_dev == False and url is None):
                        conn.write(self.return_err_dwd("DEVICE_NOT_ADDED"))

                    else:

                        conn.write(url.encode())
                    
                except Exception as e:
                    print(e)
                    conn.write(self.return_err_dwd("ERR"))





        conn.shutdown(SHUT_RDWR)
        conn.close()
        exit(1)


    def prep_socket(self):
        sock = socket(AF_INET,SOCK_STREAM,IPPROTO_TCP)
        sock.bind(('',PORT))
        sock.listen(0xFFFF)
        return sock
    

    def start_queue(self):

        print("****~ Web Querer started ~****")
        server = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server.load_cert_chain("./cert.pem","./key.pem")
        sockd = self.prep_socket()
        print(sockd)
        sock = server.wrap_socket(sockd,True)

        while True:

            conn,addr =  sock.accept()
            p = Thread(target=self.handle_request,args=(conn,addr,))
            p.daemon=True
            p.start()
            p.join()

        


q = WebQueuer()
q.start_queue()