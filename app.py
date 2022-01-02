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
    expiration_time = 1
    collection_count = 500
    count = 0
    while(True):
        current_index = (count * 50)
        count += 1
        if current_index > collection_count:
            current_index = 0
        os.system("node make_offers.js {0} {1}".format(expiration_time, current_index))
        time.sleep(expiration_time * 60 * 60 + 30) # 30 secs to run make_offers

def main():
    # start discord bot that checks whether a new message has been sent in the chat
    call_offers()
if __name__ == "__main__":
    # app.run(debug=True)
    main()

