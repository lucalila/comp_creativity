## source: https://rapidapi.com/contextualwebsearch/api/web-search/
import requests


def insert_a_pic(query_topic):
    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"
    query_topic = query_topic
    querystring = {"q": query_topic,
                   "pageNumber": "1",
                   "pageSize": "5",
                   "autoCorrect": "true"}

    headers = {
        'x-rapidapi-host': "contextualwebsearch-websearch-v1.p.rapidapi.com",
        'x-rapidapi-key': "5d502e722cmsh821affefe2df487p18c6a9jsn22da331d2b01"
    }

    ## search for images
    response = requests.request("GET", url, headers=headers, params=querystring)

    r = response.json()
    ## get first result
    r["value"][0]["url"]

    ## request image
    photo_url = r["value"][0]["url"]
    response = requests.get(photo_url)
    query_topic = query_topic.replace(' ', '_')
    ## save image
    path = f"./images/pic_{query_topic}.png"
    # storage_location = path + query_topic + ".png"
    file = open(path, "wb")
    file.write(response.content)
    file.close()
    return path

# insert_a_pic('funsion 7')