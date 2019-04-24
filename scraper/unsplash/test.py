import sys
from requests import get
from bs4 import BeautifulSoup

if len(sys.argv) < 2:
    sys.exit("Usage: test.py <url>")

url = sys.argv[1]
response = get(url)
html = response.text
    
soup = BeautifulSoup(html, 'html.parser')
img_tags = soup.find_all('img')

print("Num imgs found: {}".format(len(img_tags)))
print(img_tags)


