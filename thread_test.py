import os
import threading
import time

def call_bot():
    os.system("python call.py")
x = threading.Thread(target=call_bot)
print("starting thread")
x.start()
time.sleep(10)
print("ending thread")
x.join()
print("exiting main thread")

