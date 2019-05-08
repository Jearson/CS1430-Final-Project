import os
import sys
import json
import urllib.request as urlr
import urllib.parse as urlp

IMG_ROOT = "./imgs"
URL_TEMPLATE = "https://unsplash.com/napi/search/photos?query={}&xp=&per_page=30&page={}"

def querypgdir(query_string):
    s = query_string.split(",")
    if len(s) == 2: # then just <query>,<dirname> 
        return (s[0],-1,s[1])
    return (s[0],int(s[1]),s[2])

def download_images(query, req_pgs, dirname):
    query_dir = os.path.join(IMG_ROOT, dirname)
    # Create a directory for the images returned from the query
    try:
        os.makedirs(query_dir)
    except FileExistsError:
        pass # directory already exists
        
    # Use the URL format to get the JSON of query results and image links
    json_url = URL_TEMPLATE.format(urlp.quote(query),0)
    print("JSON URL: {}".format(json_url))
    # Download the json with the image links
    jdict = json.loads(urlr.urlopen(json_url).read().decode())
    # Figure out how many total pages we have
    num_pgs=jdict["total_pages"]
    print("Total number of pages for '{}': {}".format(query,  num_pgs))
    # If the user specified a specific number of pages, download the smaller 
    # of between that number and the number of pages
    num_pgs = min(num_pgs, req_pgs) if req_pgs != -1 else num_pgs
    print("Garbbing {} pages of results for {} and putting into '{}' directory".format(num_pgs, query, query_dir))

    # Now that we know the number of pages, download the images from the 
    # links provided by the JSON page
    for pg_num in range(num_pgs):
        json_url = URL_TEMPLATE.format(urlp.quote(query),pg_num)
        jdict = json.loads(urlr.urlopen(json_url).read().decode())
        res=jdict["results"]
        print("Downloading {} images from {}".format(len(res), json_url))
        for i in range(len(res)):
            img_url = res[i]["urls"]["raw"]
            urlr.urlretrieve(img_url, os.path.join(query_dir, "unsplash_{}_{}-{}.png").format(query,pg_num,i))

def main():
    queries_file = "queries.txt" # default
    if len(sys.argv) >= 2:
        # sys.exit("Give me a path to a textfile with "
        #     "<double-quoted-query>,<number-pages-to-get> tuples, each on their "
        #     "own line!")
        queries_file = sys.argv[2]

    print("Getting queries from '{}'".format(queries_file))
    f = open(queries_file, "r")
    if f.mode == 'r':
        # Parse the command line args into a list and download each query
        queryt = [querypgdir(q) for q in f.read().splitlines()]
        print(queryt)
        for qt in queryt:
            download_images(qt[0],qt[1],qt[2])

if __name__ == "__main__":
    main()
