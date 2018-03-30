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
        "getAccessToken: Error init token. Response status {}".format(rsps.status_code)

    return accessToken


def getProducts(site_category_id, accessToken):
    items_count = 48
    url = "https://api.joom.com/1.1/search/products"
    headers = {'Accept': '*/*',
               'Authorization': 'Bearer ' + accessToken,
               'Content-Encoding': 'gzip'
               }
    body = {"count": items_count,
            "filters": [{"id": "categoryId", "value": {"type": "categories", "items": [{"id": site_category_id}]}}]}

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
            newItem = Items(site_item_id=item["id"])
            session.add(newItem)
            session.commit()

        # getting info for request to next page
        if 'nextPageToken' in jsonresponse["payload"]:
            nextPageToken = jsonresponse["payload"]["nextPageToken"]
            body = {"count": items_count,
                    "pageToken": str(nextPageToken),
                    "filters": [{"id": "categoryId", "value": {"type": "categories", "items": [{"id": site_category_id}]}}]}
            print("nextPageToken=", nextPageToken)
        else:
            print("INFO: nextPageToken is absent. Break page loop")
            break

        # Just in case, if something goes wrong
        if cnt == 50:
            print("INFO: pages loop limit")
            break
    return


def getReviews(site_item_id, accessToken):

    # https://api.joom.com/1.1/products/1500618810160360862-64-1-709-3493395750/reviews?filter_id=all&count=8&sort=top&language=ru-RU&currency=UAH&_=jfdxc8ye
    url = 'https://api.joom.com/1.1/products/{}/reviews'.format(site_item_id)
    headers = {'Accept': '*/*',
               'Authorization': 'Bearer ' + accessToken,
               'Content-Encoding': 'gzip'
               }
    payload = {'filter_id': 'all',
               'count': '8',
               'sort': 'top'
               }
    cnt = 0
    while True:
        cnt = cnt+1
        print(cnt)

        time.sleep(2)
        rsps = requests.get(url=url, headers=headers, params=payload)

        if rsps.status_code == 200:
            jsonresponse = rsps.json()
            reviews = jsonresponse["payload"]["items"]

            for review in reviews:
                site_review_id = review["id"]
                createdTimeMs = review["createdTimeMs"]
                updatedTimeMs = review["updatedTimeMs"]

                if "text" in review:
                    text = review["text"]

                starRating = review["starRating"]

                print(site_review_id)
                print(createdTimeMs)
                print(updatedTimeMs)
                print(text)
                print(starRating)

                if "photos" in review:
                    for photo in review["photos"]:
                        print(photo["images"][0]["url"])
                        print(photo["images"][1]["url"])
                        print(photo["images"][2]["url"])
                        print(photo["images"][3]["url"])
                        print(photo["images"][4]["url"])

                # getting info for request to next page

                if 'nextPageToken' in jsonresponse["payload"]:
                    nextPageToken = jsonresponse["payload"]["nextPageToken"]
                    # print(nextPageToken)
                    payload = {'filter_id': 'all',
                               'count': '8',
                               'sort': 'top',
                               'pageToken': nextPageToken
                               }
                else:
                    print("INFO: pageToken for next reviews page is absent. Break review page loop")
                    break

                # Just in case, if something goes wrong
                if cnt == 100:
                    print("INFO: pages loop limit")
                    break

        else:
            "getReviews: Error getting review. Response status {}".format(rsps.status_code)
            return


accessToken = getAccessToken()
category_id = "1473502937203552604-139-2-118-470466103"
site_item_id = "1500618810160360862-64-1-709-3493395750"


getReviews(site_item_id, accessToken)
