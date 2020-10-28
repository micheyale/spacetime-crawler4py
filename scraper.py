import re
from urllib.parse import urlparse
import requests
import validators
from bs4 import BeautifulSoup

def scraper(url, resp):

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    lst = []
    page = requests.get(url)
    bSoup = BeautifulSoup(page.content,'html.parser')
    links_lst = bSoup.find_all('a')
    for link in links_lst:
        if 'href' in link.attrs and is_valid(url):
            lst.append(link.attrs['href'])
    return lst

#checks to see if the website is active and exists ie 200 status code
#need to "pip install validators" for it to work
def web_exists(url): 
    check = validators.url(url)
    if(check == False):
        return False;
    return True;
def is_valid(url):

    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not web_exists(url):
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
