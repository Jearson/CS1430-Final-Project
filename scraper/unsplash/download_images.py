import os
import sys
import json
import urllib.request as urlr

if len(sys.argv) < 2:
	sys.exit("Give me a query! (Optionally a number of pages to download as well)")


img_dir = "./imgs"
query=sys.argv[1]
query_dir = os.path.join("./imgs", query)

# Create a directory for the images returned from the query
try:
    os.makedirs(query_dir)
except FileExistsError:
    # directory already exists
    pass

# Use the URL format to get the JSON of query results and image links
json_url = "https://unsplash.com/napi/search/photos?query={}&xp=&per_page=30&page={}".format(query,0)
jdict = json.loads(urlr.urlopen(json_url).read().decode())

# Figure out how many total pages we have
num_pgs=jdict["total_pages"]
# If the user supplied a number, then choose the smaller number
if len(sys.argv) > 2:
    req_pgs = int(sys.argv[2])
    num_pgs = min(num_pgs, req_pgs)


# Now that we know the number of pages, then download the images from the links provided by the JSON page
for p in range(num_pgs):
	json_url = "https://unsplash.com/napi/search/photos?query={}&xp=&per_page=30&page={}".format(sys.argv[1],p)
	jdict = json.loads(urlr.urlopen(json_url).read().decode())
	res=jdict["results"]
	print("Downloading {} images from page {}".format(len(res),p))
	for i in range(len(res)):
		img_url = res[i]["urls"]["raw"]
		urlr.urlretrieve(img_url, os.path.join(query_dir, "{}_{}-{}.png").format(query,p,i))
