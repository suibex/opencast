import os,io,sys
import httpx
import asyncio
sys.path.insert(1,'./clipboard/macos/')
from clipboard import * 
from multiprocessing import Process
QUEUE_URL = "https://127.0.0.1:53/"

def run_clipboard_task():
    async def catch_clipboard_changes(device):
        
        clip = Clipboard(0,"./clipboard/macos/clip.so")
        prev_val = clip.read_clipboard()
        print(prev_val)
        cli =  httpx.AsyncClient(verify=False)
        while(1):
            dat = clip.read_clipboard()
            if(dat != prev_val and dat is not None):
                req = {
                    
                    'dev_info':device,
                    'clipboard':dat.decode()
                
                }

                dob = await cli.post(url=QUEUE_URL+"setClipboard",json=req)
                print(dob)

                prev_val = dat



    asyncio.run(catch_clipboard_changes(['gavrilo','178.148.213.134']))

run_clipboard_task()
