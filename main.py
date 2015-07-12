from urllib.request import urlopen
from urllib.error import HTTPError
from urllib import parse
from bs4 import BeautifulSoup
import datetime
import random 
import re
import ssl
import json
import sys

random.seed(datetime.datetime.now())
gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

def getLinks(article_url):
	html = urlopen("http://en.wikipedia.org"+article_url, context=gcontext)
	bsObj = BeautifulSoup(html, "html.parser")
	return bsObj.find("div", {"id":"bodyContent"}).findAll("a",
		href=re.compile("^(/wiki/)((?!:).)*$"))

def getHistoryIPs(page_url, max_retrieve, time_offset='', item_limit='100'):
	addressList = {}

	while True and len(addressList) < max_retrieve:
		page_url = page_url.replace("/wiki/", "")
		history_url = "http://en.wikipedia.org/w/index.php?" \
			+ "title=" + page_url \
			+ "&offset=" + time_offset \
			+ "&limit=" + str(item_limit) \
			+ "&action=history"

		html = urlopen(history_url, context=gcontext)
		bsObj = BeautifulSoup(html, "html.parser")

		ipAddresses = bsObj.findAll("a", {"class": "mw-anonuserlink"})
		for ipAddress in ipAddresses:
			if ipAddress.get_text() in addressList:
				addressList[ipAddress.get_text()] += 1
			else:
				addressList[ipAddress.get_text()] = 1

		nextLink = bsObj.find("a", {"class": "mw-nextlink"})
		if nextLink:
			next_page_url = nextLink.attrs["href"]
			parsed_next_page_url = parse.urlparse(next_page_url)
			query_string = parse.parse_qs(parsed_next_page_url.query)

			time_offset = query_string['offset'][0]
			print(str(len(addressList)) + "...", end='')
			sys.stdout.flush()
		else:
			break;

	print('!')
	return addressList

				
def getCountry(ip_address):
	try:
		response = urlopen("http://freegeoip.net/json/" + str(ip_address)).read().decode('utf-8')
	except HTTPError:
		return None;

	print('.', end='')
	sys.stdout.flush()

	return json.loads(response)['country_name']


#links = getLinks("/wiki/Python_(programming_language)")

#for link in links:
#	print(link.attrs["href"])

if len(sys.argv) != 2:
	print("Usage: $python3 main.py Russo-Georgian_War")
	sys.exit()

wiki_article_name = sys.argv[1]

print("Getting IPs")
historyIPs = getHistoryIPs("Russo-Georgian_War", 100, item_limit=1000)
countryDict = {}

print("Getting locations")
for ip in historyIPs:
	country = getCountry(ip)
	if country in countryDict:
		countryDict[country] += 1
	else:
		countryDict[country] = 1
print('!')

sortedCountry = sorted(countryDict, key=countryDict.get, reverse=True)
for key in sortedCountry:
	print(key + ": " + countryDict[key])