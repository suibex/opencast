
import os,io,sys
import struct
from caster import * 

#Run this to set the actual queue
#wget https://127.0.0.1:35/setQueue --post-data "{\"dev_info\":[\"gavrilo\",\"185.56.221.3\"],\"url\":\"https://www.youtube.com/watch?v=8HBcV0MtAQg&ab_channel=J.Cole-Topic\"}" --no-check-certificate


IP = "127.0.0.1"
port=int(os.getenv("SERVER_PORT"))
q_port=int(os.getenv("QUEUE_PORT"))

comm = Communicator(IP,IP,port,q_port)
msg =None

while(1):

    msgd = comm._get_device_queue()
    print("Queue:" ,msgd,msg)
    if(msgd != "none " and msgd != "DEVICE_NOT_ADDED" and msgd != msg ):
        msg = msgd
        os.system(f"open {msg}")
    time.sleep(5)




