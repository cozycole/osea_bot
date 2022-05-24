from distutils.command.clean import clean
from sqlitedict import SqliteDict
from datetime import datetime
lions_db = SqliteDict('./bid_db.sqlite', autocommit=True)
chicks_db = SqliteDict('./lazy-lions.sqlite', autocommit=True)
apidict = SqliteDict('./api_db.sqlite', autocommit=True)

out_bids = 0
print("BID DATA")
def clean_db(dict_db):
    # checks timestamps of each stored bid and removes if day old
    now = datetime.now()
    for key, value in dict_db.iteritems():
        print(key, value)
        duration = now - value
        if duration.total_seconds() > 86400/2:
            del dict_db[key]

clean_db(lions_db)
for i in enumerate(lions_db):
    # print("Key:", key, "Value:", lions_db[key])
    out_bids += 1
print("Outstanding Lazy Lion Bids:", out_bids)
out_bids = 0
clean_db(chicks_db)
for i in enumerate(chicks_db):
    # print("Key:", key, "Value:", lions_db[key])
    out_bids += 1
print("Outstanding Crypto Chicks Bids:", out_bids)
print("API DATA")
for key, value in apidict.iteritems():
    print(apidict[key])