## source: https://rapidapi.com/contextualwebsearch/api/web-search/
import requests

url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

query_topic = "furious 7"
querystring = {"q":query_topic,
               "pageNumber":"1",
               "pageSize":"5",
               "autoCorrect":"true"}

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

## save image
path = "/Users/lauraluckert/TEST_IMAGE/"
storage_location = path + query_topic + ".png"
file = open(path, "wb")
file.write(response.content)
file.close()