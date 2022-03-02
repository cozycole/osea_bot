import bidder
import os
import threading
import argparse
from dotenv import load_dotenv
from time import sleep
import file_crypt
import sale_monitor as sm
import logging

# usage: python thread_manager.py [-h] [--slug SLUG] [--nthread NTHREAD] [--bidtime BIDTIME]
########################################################################
# Flags needed for thread_manager invocation
# - Number of total threads
# - Collection id
# - Bid duration
########################################################################
# (slug, royalties, contract address)

collection_dict = {
    "chick" : ("the-crypto-chicks", 0.925, "0x1981cc36b59cffdd24b01cc5d698daa75e367e04"),
    "lion" : ("lazy-lions", 0.935, "0x8943c7bac1914c9a7aba750bf2b6b09fd21037e0"),
    "gape" : ("gamblingapes", 0.925, "0x90ca8a3eb2574f937f514749ce619fdcca187d45")
}

def get_thread_args():
    parser = argparse.ArgumentParser(description="Start osea bidding threads")
    parser.add_argument('--slug', type=str, nargs=1, help="collection name (chick, lion, gape...)")
    parser.add_argument('--nthread', type=int, nargs=1, help="number of bid threads")
    parser.add_argument('--bidtime', type=int, nargs=1, help="duration of bids in hours")
    args = parser.parse_args()
    return args

def start_threads(thread_args, num):
    tids = []
    for i in range(num):
        new_thread = threading.Thread(target=bidder.main, args=thread_args)
        tids.append(new_thread)
        new_thread.start()
        sleep(60)
    return tids

def main():
    os.system("del logs\*.log /a /s")
    os.system("del *.log /a /s")
    # logging.basicConfig(filename="MAIN_error.log", level=logging.ERROR)
    load_dotenv()
    print(f"DAEMON THREAD{threading.get_ident()}")
    wallet_address = os.getenv('POLLING_ADDRESS')
    args = get_thread_args()
    bid_lock = threading.Lock()
    if args.slug[0] in collection_dict:
        thread_args = collection_dict[args.slug[0]]
        thread_args = tuple([*thread_args, *args.bidtime, bid_lock])
    else:
        print("ERROR: Cannot identify collection string.")
        return
    # Starting N bid threads
    tids = start_threads(thread_args, *args.nthread)
    # Now start polling etherscan and periodically monitoring the status of each thread
    while True:
        sleep(20)
        sale_status = sm.poll_etherscan(wallet_address)
        if sale_status:
            print("SALE DETECTED!")
            recovery = file_crypt.decrypt_file_contents("encrypted.txt")
            password = os.getenv('PASS')
            driver = bidder.setUpDriver()
            osea = driver.current_window_handle
            change = False
            while not change:
                for w in driver.window_handles:
                    if w != osea:
                        driver.switch_to.window(w)
                        change = True
            # Now in metamask window
            bidder.meta_login(driver, password, recovery)
            print("Converting WETH") # This should cause threads to quit
            sm.convert_to_ETH(driver, driver.current_window_handle)
            print("Waiting for threads to join")
            for tid in tids:
                tid.join()
            print("Threads joined. Ending process")
            return
        # This is where we would check the threads and see what their offer rates are
        # if rates are low or consitantly erroring, end thread and restart it
        # We could also be periodically changing the VPN location (not sure if it is necessary tho)
        threads_dead = True
        for thread in tids:
            if thread.is_alive():
                threads_dead = False
                break
        if threads_dead:
            print("All threads have terminated")
            return
if __name__ == "__main__":
    main()
