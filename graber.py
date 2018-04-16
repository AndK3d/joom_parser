import requests
import time
# for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Items, Reviews, ReviewsImages, Categories

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
    items_count = 1000
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
            newItem = Items(site_item_id=item["id"], category_id = site_category_id )
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


def getReviews(site_item_id, accessToken, reviews_per_page=100):

    # https://api.joom.com/1.1/products/1500618810160360862-64-1-709-3493395750/reviews?filter_id=all&count=8&sort=top&language=ru-RU&currency=UAH&_=jfdxc8ye
    url = 'https://api.joom.com/1.1/products/{}/reviews'.format(site_item_id)
    headers = {'Accept': '*/*',
               'Authorization': 'Bearer ' + accessToken,
               'Content-Encoding': 'gzip'
               }
    payload = {'filter_id': 'all',
               'count': reviews_per_page,
               'sort': 'top'
               }
    print('item_id=', site_item_id)
    cnt = 0
    while True:
        cnt = cnt+1
        print("Reviews page ", cnt)

        time.sleep(2)
        rsps = requests.get(url=url, headers=headers, params=payload)

        if rsps.status_code == 200:
            jsonresponse = rsps.json()
            reviews = jsonresponse["payload"]["items"]

            for review in reviews:
                createdTimeMs = review["createdTimeMs"]
                updatedTimeMs = review["updatedTimeMs"]
                review_id = review["id"]
                product_id = review["productId"]
                product_variant_id = review["productVariantId"]
                likesCount = review["likesCount"]
                user_id = review["user"]["id"]
                user_fullName = review["user"]["fullName"]
                print("review_id=", review_id)
                if "avatar" in review["user"]:
                    user_avatar = review["user"]["avatar"]["images"][0]["url"]

                else:
                    user_avatar = None

                if "text" in review:
                    text = review["text"]
                else:
                    text = None
                starRating = review["starRating"]

                # Checking for existingReviews. If Review already exist in database - continue loop.
                # Else add this review to database
                existingReviews = session.query(Reviews).filter_by(product_id=product_id, review_id=review_id).first()

                if existingReviews == None:

                    session.add(Reviews(createdTimeMs=createdTimeMs,
                                        updatedTimeMs=updatedTimeMs,
                                        review_id=review_id,
                                        product_id=product_id,
                                        product_variant_id=product_variant_id,
                                        likesCount=likesCount,
                                        user_id=user_id,
                                        user_fullName=user_fullName,
                                        user_avatar=user_avatar,
                                        text=text,
                                        starRating=starRating
                                        ))
                    session.commit()

                    if "photos" in review:
                        for photo in review["photos"]:

                            img_count = len(photo["images"])
                            print(img_count)
                            url_pic_size0 = None
                            url_pic_size1 = None
                            url_pic_size2 = None
                            url_pic_size3 = None
                            url_pic_size4 = None

                            if img_count > 0: url_pic_size0 = photo["images"][0]["url"]
                            if img_count > 1: url_pic_size1 = photo["images"][1]["url"]
                            if img_count > 2: url_pic_size2 = photo["images"][2]["url"]
                            if img_count > 3: url_pic_size3 = photo["images"][3]["url"]
                            if img_count > 4: url_pic_size4 = photo["images"][4]["url"]

                            session.add(ReviewsImages(review_id=review_id,
                                                      url_pic_size0=url_pic_size0,
                                                      url_pic_size1=url_pic_size1,
                                                      url_pic_size2=url_pic_size2,
                                                      url_pic_size3=url_pic_size3,
                                                      url_pic_size4=url_pic_size4
                                                      ))
                            session.commit()


                # getting info for request to next page

                if 'nextPageToken' in jsonresponse["payload"]:
                    nextPageToken = jsonresponse["payload"]["nextPageToken"]
                    payload = {'filter_id': 'all',
                               'count': reviews_per_page,
                               'sort': 'top',
                               'pageToken': nextPageToken
                               }
                else:
                    print("INFO: pageToken for next reviews page is absent. Break review page loop")
                    return

                # Just in case, if something goes wrong
                if cnt == 100:
                    print("INFO: pages loop limit")
                    return

        else:
            "getReviews: Error getting review. Response status {}".format(rsps.status_code)
            return


def getCategories(accessToken):

    url = 'https://api.joom.com/1.1/categoriesHierarchy'

    headers = {'Accept': '*/*',
               'Authorization': 'Bearer ' + accessToken,
               'Content-Encoding': 'gzip'
               }

    payload = {'levels': -1,
               'parentLevels': 1
               }

    rsps = requests.get(url=url, headers=headers, params=payload)

    if rsps.status_code == 200:
        jsonresponse = rsps.json()
        for category in jsonresponse['payload']['children']:

            category_id = category['id']
            category_name = category['name']
            hasPublicChildren = category['hasPublicChildren']
            if 'parentId' in category:
                parent_id = category['parentId']
            else:
                parent_id = None
            session.add(Categories(category_id=category_id,
                                   category_name=category_name,
                                   hasPublicChildren=hasPublicChildren,
                                   parent_id=parent_id
                                   ))
            session.commit()

            getChildren(category)

    return

def getChildren(tree):

    if 'children' in tree:
        for category in tree['children']:

            category_id = category['id']
            category_name = category['name']
            hasPublicChildren = category['hasPublicChildren']
            if 'parentId' in category:
                parent_id = category['parentId']
            else:
                parent_id = None

            session.add(Categories(category_id=category_id,
                                   category_name=category_name,
                                   hasPublicChildren=hasPublicChildren,
                                   parent_id=parent_id
                                   ))

            print(category_id, category_name, hasPublicChildren, parent_id)
            if category['hasPublicChildren']:
                getChildren(category)

            # session.commit()


def scrap(category_id, accessToken):

    getProducts(category_id, accessToken)
    items = session.query(Items).filter_by(category_id=category_id).all()

    for item in items:
        getReviews(item.site_item_id, accessToken, 100)

    return

accessToken = getAccessToken()
category_id = "1473502937203552604-139-2-118-470466103"
site_item_id = "1500618810160360862-64-1-709-3493395750"

category_id ="1481982628148420959-25-2-26312-2483073901" #AS toys

scrap(category_id, accessToken)

#getReviews(site_item_id, accessToken)

#getCategories(accessToken)