import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import tokenizer
import nltk
from nltk.corpus import stopwords
from datetime import datetime

domain_set = set() # len of set would be the answer
path_dict = {}
ics_subdomain_dict = dict()
tokenDict = {}
longestLength = 0
longestUrl = ""

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
    global longestLength
    global longestUrl

    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.text,'html.parser')

        bodyText = text_from_html(resp.raw_response.text, soup)
        bodyLength = len(bodyText)
        if bodyLength > longestLength:
            longestLength = bodyLength
            longestUrl = url

        tokenizer.updateTokenCounts(tokenDict, bodyText)

        allTags = soup.find_all('a')

        for tag in allTags:
            if 'href'in tag.attrs and 'uci.edu' in tag.attrs['href']:

                extractedLink = tag.attrs['href']
                extractedLink = extractedLink.split('#')[0]
                extractedLinks.append(extractedLink)

    #print("SUBDOMAINS: " + str(ics_subdomain_dict))
    #print(str(tokenDict))
    #print(" ")
    return extractedLinks

def validate(url):
    try:
        if url[-1] == '/':
            url = url.rstrip('/')
        date_text = url.rsplit('/')[-1]
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False

def validate2(url):
    try:
        if url[-1] == '/':
            url = url.rstrip('/')
        date_text = url.rsplit('/')[-1]
        if date_text != datetime.strptime(date_text, "%Y-%m").strftime('%Y-%m'):
           raise ValueError
        return True
    except ValueError:
        return False

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if "/pdf/" in url:
            return False

        if validate(url):  #returns False for URLs that end in /year-month-day
            return False

        if validate2(url): #returns False for URLs that end in /year-month
            return False

        if url.rsplit('?')[1:] and 'share' in url.rsplit('?')[1:][0]: #returns False for URLs like: 'http://wics.ics.uci.edu/?share=twitter
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|ps.z)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

def printTopTokens(tokenDict):
    stopwordList = {"ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while", "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"}

    for word in stopwordList:
        if word in tokenDict:
            tokenDict.pop(word)

    sortedList = sorted(tokenDict.items(), key=lambda x: x[1], reverse=True)

    count = 0
    for entry in sortedList:
        if count >= 50:
            break

        print(entry[0] + " = " + str(entry[1]))
        count += 1

def printLongest(url):
    print("The URL with the most text was: " + url)
