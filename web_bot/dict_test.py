from sqlitedict import SqliteDict
from datetime import datetime

dbdict = SqliteDict('./bid_db.sqlite', autocommit=True)
apidict = SqliteDict('./api_db.sqlite', autocommit=True)

out_bids = 0
print("BID DATA")
for i in enumerate(dbdict):
    # print("Key:", key, "Value:", dbdict[key])
    out_bids += 1
print("Outstanding Bids:", out_bids)

print("API DATA")    
for key, value in apidict.iteritems():
    print(apidict[key])