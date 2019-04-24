import sys
import json
import urllib.request as urlr

if len(sys.argv) < 2:
	sys.exit("Give me a query!")

query=sys.argv[1]
json_url = "https://unsplash.com/napi/search/photos?query={}&xp=&per_page=30&page={}".format(query,0)
jdict = json.loads(urlr.urlopen(json_url).read().decode())
num_pgs=jdict["total_pages"]


# Now that we know the number of pages, then do the rest
for p in range(num_pgs):
	json_url = "https://unsplash.com/napi/search/photos?query={}&xp=&per_page=30&page={}".format(sys.argv[1],p)
	jdict = json.loads(urlr.urlopen(json_url).read().decode())
	res=jdict["results"]
	print("Downloading {} images from page {}".format(len(res),p))
	for i in range(len(res)):
		img_url = res[i]["urls"]["raw"]
		urlr.urlretrieve(img_url, "imgs/{}_{}-{}.png".format(query,p,i))
