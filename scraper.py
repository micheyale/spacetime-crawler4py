import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import tokenizer
from datetime import datetime
import sys
import pickle
with open('all_links.txt', 'rb') as f:
    path_dict = pickle.load(f) #path_dict is every link we actually scraped from
with open('ics_sub.txt', 'rb') as f:
    ics_subdomain_dict = pickle.load(f)
with open('word_freq.txt', 'rb') as f:
    word_frequencies = pickle.load(f)
with open('longest_page.txt', 'rb') as f:
    longest_page = pickle.load(f)
with open('ev_link.txt', 'rb') as f:
    every_link = pickle.load(f) #every_link is every link we found that was valid

low_count = [] #will collect low content links (we will only consider links with a query

#allows us to get correct content fron html
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']: #these are the tags we want
        return False
    if isinstance(element, Comment):
        return False
    return True
#here we use beautiful soup to parse the html based on the tags specified above and join it together in a string
def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)


def scraper(url, resp):
    links = extract_next_links(url, resp)                              
    return [link for link in links if is_valid(link)]

#we will not crawl links that end in y-m-d ex) 2020-12-31
#the reasoning for this is these links contain information that can be found through alternate links.
def validate(date_text1):
    try:
        if date_text1 != datetime.strptime(date_text1, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
        
    except ValueError:
        return False
#we will not crawl links that end in y-m- ex) 2020-12
def validate2(date_text1):
    try:
        if date_text1 != datetime.strptime(date_text1, "%Y-%m").strftime('%Y-%m'):
            raise ValueError
        return True
    except ValueError:
        return False

#this function ensures every link we add to our frontier is within our given domains
def in_domain(url):
    for i in ['.ics.uci.edu','.cs.uci.edu','.informatics.uci.edu','.stat.uci.edu','today.uci.edu/department/information_computer_sciences']:
        if i in url:
            return True
    return False
#this function will not scrape a link for webpages if it's domain/path (not including query) is in low_count
def low_content_link(url):
    for l in low_count:
        if l in url:
            return True
    return False
def extract_next_links(url, resp):
    lst = [] #links we will add to the frontier
    tokenDict = {} #we will tokenize each webpage
    global longest_page
    global word_frequencies

    if resp.status == 200 and not low_content_link(url) and url not in path_dict:
        try:
            html = urllib.request.urlopen(url).read()	  
            bodyText = text_from_html(html)	       
            tokenizer.updateTokenCounts(tokenDict, bodyText)
        except urllib.error.HTTPError: #in cases where a permanent redirect error occurs when we try and read a pages html
            print("This URL: " + str(url) + " cannot be scraped for content.")
            return lst

        page = requests.get(url)
        bSoup = BeautifulSoup(page.content,'html.parser')
        links_lst = bSoup.find_all('a') #puts all hyperlinks in a lst
        
        parsed_uri = urlparse(url)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri) #this allows us to keep track of a out parent domain in case we need to reconnect the path

        word_count = sum(tokenDict[d] for d in tokenDict if d.isalpha()) #counts words on a webpage
        print("WORD COUNT: ",word_count)
        if word_count > longest_page[1]:
            longest_page = (url,word_count)
            pickle.dump(longest_page,open('longest_page.txt','wb'))

        # Update word_frequencies with the new tokenDict from each page
        for key, value in tokenDict.items():
            if key in word_frequencies:
                word_frequencies[key] += value
            else:
                word_frequencies[key] = value
        pickle.dump(word_frequencies,open('word_freq.txt','wb'))
                
        if word_count > 200:
            print("BEGIN PARSING LINK: ",url)
            path_dict[url] = 1 #we are adding link to path_dict when we begin crawling that webpage NOT when we initially scrape the link
            pickle.dump(path_dict,open('all_links.txt','wb'))
            no_path = url.rsplit('/') #grabs 'https://mswe.ics.uci.edu' from 'https://mswe.ics.uci.edu/faq/' for ics dict
            no_path = 'http:/' + ['/'.join(no_path[1:3])][0]

            if '.ics.uci.edu' in no_path:
                if no_path not in ics_subdomain_dict:
                    ics_subdomain_dict[no_path] = 1 #adds ics subdomain to dict with one occurance
                else:
                    if ics_subdomain_dict[no_path] > 65 and no_path != 'http://www.ics.uci.edu':
                        low_count.append(no_path)
                    ics_subdomain_dict[no_path] += 1 #increments the occurance of the ic subdomain that has appeared at least once
                pickle.dump(ics_subdomain_dict,open('ics_sub.txt','wb'))
            for link in links_lst:
 
                if 'href' in link.attrs:
                    current_link = link.attrs['href']
                    if len(link.attrs['href']) >= 1 and link.attrs['href'][0] == '/': #adding the parent domain to keys that only equal the path
                        missing_domain_check = result + link.attrs['href']  
                        current_link = missing_domain_check
                        
                    
                    current_link = current_link.split('#')[0] #defragments our URL

                    if current_link and current_link[-1] == '/':     #uniformly strips / to every link that ends in '/' so we don't mistakening double count
                        current_link = current_link[:-1]

                    http_adder = current_link.rsplit('/') 
                    current_link = 'http:/' + ['/'.join(http_adder[1:])][0] #uniformly adds http:/ to every link so we don't mistakening double count
                    if in_domain(current_link) and is_valid(current_link) and current_link not in every_link:
                        print("link we're downloading: ",current_link)
                        every_link[current_link] = 1
                        pickle.dump(every_link,open('ev_link.txt','wb'))
                        lst.append(current_link)
                                             

    print("PATH DICT: ",len(path_dict))
    print("ICS DICT: ", ics_subdomain_dict)                
    print("LONGEST PAGE: ",longest_page)
    if len(lst) < 5:  
        if len(lst) == 1: #if a webpage only had one URL then it has low information and it is possible it is a trap link so we discard it
            lst = []
        if '?' in url:
            url = url.split('?')[0] #if a webpage contains a query and only scraped five links we deem it as only content and add the url stripped on the query to the low_content lst
            low_count.append(url)
    return lst

def is_valid(url):

    try:
        parsed = urlparse(url)
        check = requests.get(url)
        content_type = check.headers.get('content-type')
        if parsed.scheme not in set(["http", "https"]):
            return False
        if url:
            c = url
            if c[-1] == '/':
                c = c.rstrip('/')  
            date_text = c.rsplit('/')
            date_text1 = date_text[-1]
            date_text2 = str('-'.join(date_text[-2:]))
            date_text3 = str('-'.join(date_text[-3:]))

            if validate(date_text1):
                return False
            if  validate2(date_text1):
                return False         
            if validate2(date_text2):
                return False
            if validate1(date_text3):
                return False
        if url.rsplit('?')[1:] and 'share' in url.rsplit('?')[1:][0]: #returns False for URLs like: 'http://wics.ics.uci.edu/?share=twitter
            return False
        if url.rsplit('?')[1:] and 'replytocom' in url.rsplit('?')[1:][0]: #return false for links that are just comments on an article
            return False
        if check.status_code != 200: 
            return False   
        if content_type and 'text' not in content_type: #return False for webpages that do not contain text ie pdf or None
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
    except requests.ConnectionError:
        print(url, " is not a valid website.")
    except requests.exceptions.InvalidURL:
        print(url, " is not a valid website: no host specified.")
    except TypeError:
        print ("TypeError for ", parsed)
        raise


def printTopTokens(tokenDict):

    sortedList = sorted(tokenDict.items(), key=lambda x: x[1], reverse=True)

    count = 0
    for entry in sortedList:
        if count >= 50:
            break

        print(entry[0] + " = " + str(entry[1]))
        count += 1

def printLongest(url):
    print("The URL with the most text was: " + str(url[0]))
    print("The total length of this page is: " + str(url[1]))

def printUniqueUrlCount(count):
    print("Number of unique URLs found: " + str(count))

def subdomainCount(icsSubs):
    if 'https://www.ics.uci.edu' in ics_uci_subdomain:
        del ics_uci_subdomain['https://www.ics.uci.edu']
    print("ICS subdomains: " ,sorted((key,value) for key,value in ics_uci_subdomain.items()))
