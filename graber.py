from bs4 import BeautifulSoup
import requests, json
from requests.auth import HTTPBasicAuth
import re,os, time
# database
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
            #print(accessToken)

    else:
        "getAccessToken: Error init token. Responce status {}".format(rsps.status_code)

    return accessToken


accessToken = getAccessToken()

category_id = "1473502937203552604-139-2-118-470466103"
items_count = 10

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

    for item in items:
        print(item["id"])

        # newRestaurant = Restaurant(name=request.form['name'])
        # session.add(newRestaurant)
        # session.commit()

    if 'nextPageToken' in jsonresponse["payload"]:
        nextPageToken = jsonresponse["payload"]["nextPageToken"]
        body = {"count": items_count,
                "pageToken": str(nextPageToken),
                "filters": [{"id": "categoryId", "value": {"type": "categories", "items": [{"id": category_id}]}}]}
        print("nextPageToken=", nextPageToken)
    else:
        print("INFO: nextPageToken is absent. Break page loop")
        break

    if cnt == 1:
        print("INFO: pages loop limit")
        break


