import os,io,sys
import httpx
import asyncio
import requests
sys.path.insert(1,'/Users/gavrilo/Desktop/opencast/opencast/client/lib/')
from caster import * 

from multiprocessing import Process
QUEUE_URL = "https://127.0.0.1:53/"

if(len(sys.argv) < 2):
    print("** Provide URL and a device name.")
    exit(1)

url = sys.argv[1]
dev_name = sys.argv[2]

async def send_req(dev_name,url):

    dev_ip = requests.get("https://ifconfig.co/json").json()['ip']
    dev_info = [dev_name,dev_ip]
    cli =httpx.AsyncClient(verify=False)
    req = {
        'dev_info':dev_info,
        'url':url
    }

    try:
        
        dat = await cli.post(QUEUE_URL+"setQueue",json=req)
        print(dat.text)


    except Exception as e:
        pass
    

asyncio.run(send_req(dev_name=dev_name,url=url))