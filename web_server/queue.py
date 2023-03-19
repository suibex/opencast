"""

    @title:  Queue module for queueing URLs
    @author: nitrodegen (Gavrilo Palalic)

    Copyright (c) 2023 Gavrilo Palalic

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    
"""
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


PORT = int(os.getenv("QUEUE_PORT"))
print(PORT)


"""
    POST /getQueue 
    POST /setQueue

    #in queues you will have stored.
    [dev_info(packed),current_playin_url]

    #in keyboard queues you will have stored
    element will contain: [dev_info,clipboard]


"""



class WebQueuer(object):
    def __init__(self) -> None:
        
        self.queues  = [] 
        self.clipboard_queue=[]

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
        depd = req
        req = req.split("\r\n")
        typed =req[0].split(" ")
        if(typed[0] != "POST"):
            conn.write(self.return_err_dwd("ERR"))
        else:   
            jsoned = b""
            method= typed[1].replace("/","")


            if(method == "setClipboard"):
                
                for param in req:
                    if("Content-Length" in param or "content-length" in param):
                        dod = depd.split("\r\n\r\n")
                        length = int(param.split(":")[1].replace(" ",""))
                        if(len(dod) > 1) :
                            length-=len(dod[1])
                            jsoned+=dod[1].encode()                                
                        for i in range(length):
                            jsoned+=conn.recv(1)

                        break
                        
                
                try:
                    jsoned = json.loads(jsoned)

                    dev_info = jsoned['dev_info']
                    clipbrd = jsoned['clipboard']
                    found_device = False
        
                    for i in range(len(self.clipboard_queue)):

                            queue = self.clipboard_queue[i]
                            dev = queue[0]
                            
                            if(dev[0] == dev_info[0] and dev[1] == dev_info[1]):
                                
                                found_device = True
                                self.clipboard_queue[i][1]  =  clipbrd

                    if(not found_device):
                        self.clipboard_queue.append([dev_info,clipbrd])
                    print("Clipboard set ",dev_info,clipbrd)
                    conn.send(self.return_err_dwd("OK"))
                except Exception as e:
                    conn.send(self.return_err_dwd("server returned:"+str(e)))
              
            if(method == "getClipboard"):
                for param in req:
                    if("Content-Length" in param or "content-length" in param):
                        dod = depd.split("\r\n\r\n")
                        length = int(param.split(":")[1].replace(" ",""))
                        if(len(dod) > 1) :
                            length-=len(dod[1])
                            jsoned+=dod[1].encode()                                
                        for i in range(length):
                            jsoned+=conn.recv(1)

                        break
                        
                
                try:
                    jsoned = json.loads(jsoned)
                    dev_info = jsoned['dev_info']
                    found_device = False
                    clipboard_data_found = None

                    for i in range(len(self.clipboard_queue)):
                        dev_c = self.clipboard_queue[i]
                        if(dev_c[0][0] == dev_info[0] and dev_c[0][1] == dev_info[1]):
                            found_device=True
                            clipboard_data_found = dev_c[1]
                    if(found_device and clipboard_data_found is not None):
                        conn.send(self.return_err_dwd(clipboard_data_found))
                    else:
                        conn.send(self.return_err_dwd("no clipboard data found"))

                    

                except Exception as e:
                    conn.send(self.return_err_dwd("server returned:"+str(e)))

            if(method == "setQueue"):
                

                for param in req:
                    if("Content-Length" in param or "content-length" in param):

                        
                        dod = depd.split("\r\n\r\n")
                        length = int(param.split(":")[1].replace(" ",""))
                        if(len(dod) > 1) :
                            length-=len(dod[1])
                            jsoned+=dod[1].encode()

                             
                        for i in range(length):
                            jsoned+=conn.recv(1)

                        break

                jsoned = json.loads(jsoned)
                if(jsoned['url'] == "none"):
                    for i in range(len(self.queues)):
                        dev = self.queues[i]
                        if(dev[0][0] == jsoned['dev_info'][0]):
                            print("deleting device :",dev)

                            del self.queues[i]
                            break

                else:
                    if(len(self.queues) > 1):
                        for i in range(len(self.queues)):
                            q = self.queues[i]
                            if(q[0][0] == jsoned['dev_info'][0]):
                                q[1] = jsoned['url']
                         
                    else:
                        devd = [jsoned['dev_info'],jsoned['url']]
                        if(devd not in self.queues):
                            self.queues.append([jsoned['dev_info'],jsoned['url']])
                    #conn.send(self.return_err_dwd("DEVICE_ADDED"))
                
             



            if(method == "getQueue"):


                for param in req:
                    if("Content-Length" in param or "content-length" in param):

                        length = int(param.split(":")[1].replace(" ",""))
                        for i in range(length):
                            jsoned+=conn.recv(1)
                        break
                
      
                jsoned = jsoned.replace(b"\r\n",b"")
                jsoned = jsoned.replace(b"\r",b"")
                jsoned = jsoned.replace(b"\n",b"")
                jsoned = jsoned.replace(b"'",b"\"")
               
                jsoned = json.loads(jsoned)
               # print("DD:",jsoned)

                try:
                    
                    dev_info = jsoned['dev_info']
                    dev_name = dev_info[0]
                    dev_ip = dev_info[1]
                    found_dev= False
                    url = None
                    #print(dev_info)

                    for dev in self.queues:
                        print("DEV:",dev,dev_ip,)
                        
                        if(str(dev[0][0]) == str(dev_name) and str(dev[0][1]) == str(dev_ip)):
                            found_dev = True
                            print(" I MATCH !!! ")
                            url = dev[1]
                            break   

                    
                    print("FOUND:",found_dev,"URL:",url)
                    
                    if(found_dev == False and url is None):
                        conn.write(self.return_err_dwd("DEVICE_NOT_ADDED"))

                    else:
                        if(url == "none"):
                            conn.write(self.return_err_dwd("none"))
                        else:
                            conn.write(self.return_err_dwd(url))
                            
                    
                except Exception as e:
                    print(e)
                    conn.write(self.return_err_dwd("ERR"))




        try:
            conn.shutdown(SHUT_RDWR)
            conn.close()
            exit(1)

        except Exception as e:
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