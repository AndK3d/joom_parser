import requests
import time
# for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items

engine = create_engine('sqlite:///joom.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def getAccessToken():
    rsps = requests.post("https://www.joom.com/tokens/init?")
    accessToken = None
    if rsps.status_code == 200:
        jsonresponse = rsps.json()

        if "accessToken" in jsonresponse:
            accessToken = jsonresponse["accessToken"]

    else:
        "getAccessToken: Error init token. Responce status {}".format(rsps.status_code)

    return accessToken


accessToken = getAccessToken()

category_id = "1473502937203552604-139-2-118-470466103"
items_count = 48

url = "https://api.joom.com/1.1/search/products"
headers = {'Accept': '*/*',
           'Authorization': 'Bearer ' + accessToken,
           'Content-Encoding': 'gzip'
           }
body = {"count": items_count, "filters": [{"id": "categoryId", "value": {"type": "categories", "items": [{"id": category_id}]}}]}

# Pages loop.
# Getting items from each page
cnt = 0
while True:
    cnt = cnt + 1
    print(cnt)

    time.sleep(2)
    rsps = requests.post(url=url, headers=headers, json=body)
    jsonresponse = rsps.json()

    items = jsonresponse["contexts"][0]["value"]

    # insert items into database
    for item in items:
        newItem = Items(item_id=item["id"],
                        search_category_id=category_id)
        session.add(newItem)
        session.commit()

    # getting info for request to next page
    if 'nextPageToken' in jsonresponse["payload"]:
        nextPageToken = jsonresponse["payload"]["nextPageToken"]
        body = {"count": items_count,
                "pageToken": str(nextPageToken),
                "filters": [{"id": "categoryId", "value": {"type": "categories", "items": [{"id": category_id}]}}]}
        print("nextPageToken=", nextPageToken)
    else:
        print("INFO: nextPageToken is absent. Break page loop")
        break

    # Just in case, if something goes wrong
    if cnt == 50:
        print("INFO: pages loop limit")
        break


