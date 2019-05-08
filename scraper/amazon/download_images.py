import os
import re
import sys
import base64
import json
import urllib.parse as urlp
import urllib.request as urlr
import requests
from bs4 import BeautifulSoup
import random

IMG_ROOT = "./imgs"
SEARCHPG_URL = "https://www.amazon.com/s?k={}&lo=list&page={}&qid=1556933209&ref=sr_pg_1"
URLOPENER = urlr.build_opener()
USRAGENT_TEMPLATE = "Mozilla/5.0 (Macintosh; Intel Mac OS X {}.{}; rv:{}.0) Gecko/20100101 Firefox/{}.0"
REFERER_URL_TEMPLATE = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords={}"
# USRAGENT_TEMPLATE = "Mozilla/5.0 (Windows NT {}.{}; rv:{}.0) Gecko/20100101 Firefox/{}.0" # I don't think this works as well...
# Oohh okay, so they were sus about the number of requests I made AND the lack of headers (maybe both together is a sparate entity)
# Hmmm okay, so it definitely seems like they're watching ip addresses for this...
# Maybe if I switch wifi networks?
# More headers == more airtime before captcha kicks in
# TODO: Lookinto weird startup issue?

"""
Host: m.media-amazon.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0
Accept: image/webp,*/*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=television
Connection: keep-alive
TE: Trailers
"""

# This entire thing work for around a little more than 21 min, when amazon catches on to us

def querypgdir(query_string):
    s = query_string.split(",")
    return (s[0],int(s[1]),int(s[2]),s[3]) # expecting <search query>,<start pg num>,<end pgnum>,<name of dest dir>
def DEFAULT_URLOPENER_HEADERS():
    URLOPENER.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv,66.0) Gecko/20100101 Firefox/66.0'),
            ('Referer', ''),
            ('Host', 'm.media-amazon.com'),
            ('Accept', 'image/webp,*/*'),
            ('Accept-Language', 'en-US,en;q=0.5'),
            # ('Accept-Encoding', 'gzip, deflate, br'),
            ('Connection', 'keep-alive'),
            # ('TE', 'Trailers')
            ]

def ROLL_URLOPENER_HEADERS():    
    print("Rerolling User-Agent header for url openers...")
    print("Old User-Agent header: {}".format(URLOPENER.addheaders))
    # For now just change MacOSX versions
    maj = random.randint(8,10) # Mac
    min = random.randint(1,11) # Mac
    # maj = random.randint(4,6) # Windows
    # min = random.randint(1,3) # Windows
    cvs_tag = random.randint(1,60)
    ffx_vers = random.randint(63,64)
    URLOPENER.addheaders[0] = ("User-Agent", USRAGENT_TEMPLATE.format(maj, min, cvs_tag, ffx_vers)) # User-Agent is first index
    print ("New User-Agent header: {}".format(URLOPENER.addheaders))


def download_images(query, start_pg, end_pg, dirname):
    query_dir = os.path.join(IMG_ROOT, dirname)
    # Create a directory for the images returned from the query
    try:
        os.makedirs(query_dir)
    except FileExistsError:
        pass # directory already exists
    # Add headers to the request to make the Amazon servers not hate us
    DEFAULT_URLOPENER_HEADERS()
    URLOPENER.addheaders[1] = ('Referer', REFERER_URL_TEMPLATE.format(urlp.quote(query))) # update the referrer headers to suit the query
    print("Starting URL opener headers: {}".format(URLOPENER.addheaders))
    print("===== QUERY: {}".format(query))
    for pg_num in range(start_pg, end_pg):
        searchpg_url = SEARCHPG_URL.format(urlp.quote(query),pg_num)
        test = urlr.build_opener()
        response = URLOPENER.open(searchpg_url)
        result_pg = response.read()
        # Parse the received page (x2 parse becaue the first time is a bit messy)
        soup = BeautifulSoup(result_pg, 'html.parser')
        soup = BeautifulSoup(str(soup), 'html.parser')

        # STEP 1: SEARCH PAGE: Grab the links to the product pages
        data_indexes = soup.findAll('div', attrs={'data-index':re.compile("^\d")})
        print("Num data indexes on page: {}".format(len(data_indexes)))
        if (len(data_indexes) == 0):
            # In this case CAPTCHA is probably activated and we should switch headers
            # (Write the html of the requested page anyway, just in case)
            errorfile = os.path.join("errors", "{}-pg{}.html").format(query,pg_num)
            with open(errorfile, 'w+') as f:
                f.write(str(soup))
            # Retry with new headers
            ROLL_URLOPENER_HEADERS() # gotta avoid being CAPTCHA'd
            response = URLOPENER.open(searchpg_url)
            result_pg = response.read()
            # Parse the received page (x2 parse becaue the first time is a bit messy)
            soup = BeautifulSoup(result_pg, 'html.parser')
            soup = BeautifulSoup(str(soup), 'html.parser')
            data_indexes = soup.findAll('div', attrs={'data-index':re.compile("^\d")})
            print("- Num data indexes on new page: {}".format(len(data_indexes)))
            if (len(data_indexes) == 0):
                # Dang, they got us twice
                print("Man, we've really done goofed. Detected us x2")
                errorfile = os.path.join("errors", "{}-pg{}x2.html").format(query,pg_num)
                with open(errorfile, 'w+') as f:
                    f.write(str(soup))
           
        # Go through each of the product links of the search results
        for i in range(len(data_indexes)):
            prod_links = data_indexes[i].findAll("a", href=True, attrs={"class":"a-link-normal"})
            # print("Num product links in data index: {}".format(len(prod_links)))
            if (len(prod_links) == 0):
                print("No product links for data index {}".format(i))
                continue
             # These product links are repeated, so just choose the first
            link = str(prod_links[0]['href'])

            # There seems to be at least 1 '#' link and 1 'bestseller' link per page
            if link == "#":
                print("NOTE: Encountered '#' as link. Skipping...")
                continue
            if "bestsellers" in link: # this is to (fragily) deal with /gp/bestsellers/pc/17935294011/ref=sr_bs_6_17935294011_1
                print("NOTE: Encountered 'bestsellers' in link. Using next product page link...")
                link = str(prod_links[1]['href']) # move on to the next link as that probably has the real product redirect link rather than an unrelated bestseller link
            
            # Sometimes the links don't need to be appended
            if ("www.amazon.com" not in link):
                link = "https://www.amazon.com{}".format(link)
            
            print("Query: {}, Pg:{}, index:{}".format(query, pg_num, i))
            try:
                product_soup = BeautifulSoup(URLOPENER.open(link).read(), 'html.parser') # There are errors here with the links
            except:
                print("Error opening product page. Link {}".format(link))
                continue
            product_soup = BeautifulSoup(str(product_soup), 'html.parser') # Double soup to clean up irregularities

            # STEP 2: PRODUCT PAGE: We've gotten the page and can now scrape images
            # Originally we were gonna get all of the images on the product page, but bc of time we only get one (the others require running JS)

            # TODO: Maybe print out a summer of how many images from each category has been downloaded
            # TODO: Visit 10th page of each thing and check quality is still passable
            # TODO: I should probably do away with Sponsored stuff, since they're sometimes unrellated (ex. mac laptop case)
            # TODO: To address repeats, I think I should keep a hashtable of visited (+fully resolved) urls so that I don't visite the smae page twice. Some products are just that popular....
            # TODO: Use phantom js to activate the javascript of the images on the left
            # TODO: explore just looking at <img> and grabbing the src from there
            # For now, just go to the large image box and grab the image data already there
            product_divs = product_soup.findAll('div', attrs={'id':'imgTagWrapperId'})
            if (len(product_divs) == 0):
                # print("WARNING: Looks like {} doesn't have any imgTagWrapperId elements".format(link))
                # print("No imgTagWrapperId elements for {}-{}".format(pg_num, i))
                # print("Continuing...")
                continue

            # The entirety of the image data for the picture has already been downloaded by the url requester
            # Strip the metadata, decode, and write to file
            img_data = product_divs[0].img['src'] # TODO: Something wronge with PC laptop = binascii.Error: Invalid base64-encoded string: number of data characters (41) cannot be 1 more than a multiple of 4
            data_len = len(img_data)
            try:
                if ('.jpg' in img_data):
                    imgdata = urlr.urlopen(img_data).read() # The 'img data' was actually a link
                    filename = os.path.join(query_dir, "amazon_{}_{}-{}.jpg").format(query,pg_num,i)
                    with open(filename, 'wb') as f:
                        f.write(imgdata)
                elif ('.png' in img_data):
                    imgdata = urlr.urlopen(img_data).read() # The 'img data' was actually a link
                    filename = os.path.join(query_dir, "amazon_{}_{}-{}.png").format(query,pg_num,i)
                    with open(filename, 'wb') as f:
                        f.write(imgdata)
                else:
                    imgdata = base64.b64decode(img_data[24:-1])
                    filename = os.path.join(query_dir, "amazon_{}_{}-{}.png").format(query,pg_num,i)
                    with open(filename, 'wb') as f:
                        f.write(imgdata)
            except:
                print("Error occured decoding image on page-index '{}-{}' for query '{}'. Contents of 'src' tag: {}".format(pg_num, i, query, product_divs[0].img['src']))


def main():
    queries_file = "queries.txt" # default
    if len(sys.argv) >= 2:
        # sys.exit("Give me a path to a textfile with "
        #     "<double-quoted-query>,<number-pages-to-get> tuples, each on their "
        #     "own line!")
        queries_file = sys.argv[2]

    # DEBUG: print("Getting queries from '{}'".format(queries_file))
    f = open(queries_file, "r")
    if f.mode == 'r':
        # Parse the command line args into a list and download each query
        queryt = [querypgdir(q) for q in f.read().splitlines() if q[0] != '#']
        # DEBUG: print(queryt)
        for qt in queryt:
           download_images(qt[0],qt[1],qt[2],qt[3])

if __name__ == "__main__":
    main()
