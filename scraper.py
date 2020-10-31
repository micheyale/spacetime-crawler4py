import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import tokenizer

domain_set = set() # len of set would be the answer
path_dict = {}
ics_subdomain_dict = dict()
tokenDict = {}

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body, soup):
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    extractedLinks = []

    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.text,'html.parser')
        bodyText = text_from_html(resp.raw_response.text, soup)
        tokenizer.updateTokenCounts(tokenDict, bodyText)
        #print(str(tokenDict["department"]))

        allTags = soup.find_all('a')

        for tag in allTags:
            if 'href'in tag.attrs and 'uci.edu' in tag.attrs['href']:

                extractedLink = tag.attrs['href']
                extractedLinks.append(extractedLink)

    #print("SUBDOMAINS: " + str(ics_subdomain_dict))
    print(" ")
    return extractedLinks

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
