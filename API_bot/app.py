from flask import Flask
from threading import Thread
import os
import time


app = Flask(__name__)

gambl_apes_count = 7777

# would need to be a post http request
@app.route('/offer_data')
def recv_offer_data():
    return

def call_offers():
    expiration_time = 4
    while(True):
        os.system("node make_offers.js {0}".format(expiration_time))
        time.sleep(expiration_time * 60 * 60 + 30) # 30 secs to run make_offers

def main():
    # start discord bot that checks whether a new message has been sent in the chat
    call_offers()
if __name__ == "__main__":
    # app.run(debug=True)
    main()

