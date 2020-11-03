import re
from urllib.parse import urlparse
import requests
import validators
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import tokenizer
from datetime import datetime

path_dict = {}
ics_subdomain_dict = dict()
common_word = {}

longest_page = ("",0)

#THIS ERROR NEEDS TO BE ACCOUNTED FOR
#https://password.ics.uci.edu
#error: urllib.error.HTTPError: HTTP Error 308: Permanent Redirect

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)



def scraper(url, resp):

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


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
    
def extract_next_links(url, resp):
    lst = []
    tokenDict = {}
    global longest_page
    if resp.status == 200:
        html = urllib.request.urlopen(url).read()
        bodyText = text_from_html(html)
        tokenizer.updateTokenCounts(tokenDict, bodyText)

        page = requests.get(url,auth=('user', 'pass'))
        bSoup = BeautifulSoup(page.content,'html.parser')
        links_lst = bSoup.find_all('a')
        parsed_uri = urlparse(url)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

        word_count = sum(tokenDict[d] for d in tokenDict if d.isalpha()) #only counting words on a page rn 
        print("WORD COUNT: ",word_count)
        if word_count > longest_page[1]:
            longest_page = (url,word_count)
        average.append(word_count)
        
        for link in links_lst:
            
            if 'href' in link.attrs:
                current_link = link.attrs['href']
                if len(link.attrs['href']) >= 1 and link.attrs['href'][0] == '/': #adding the parent domain to keys that only equal the path
                    print("ONLY PATH: ",link.attrs['href'])
                    missing_domain_check = result + link.attrs['href']
                    current_link = missing_domain_check
                
                in_domain = re.search('https?://([a-z0-9]+[.])*uci[.]edu((\/\w+)*\/)?',current_link)
                also_in_domain = re.search('https?://([a-z0-9]+[.])*uci[.]edu((\/\w+)*\/)?',current_link)
                                

                if '#' in current_link:
                    current_link = current_link.split('#')[0]
                    print("LINK HAS BEEN DEFRAGGED: ",current_link)
                #I INITIALLY HAD THIS TO AVOID A TRAP BUT I DON'T THINK WE'RE GETTING STUCK IN IT NOW
                #if '?' in current_link:
                #    current_link = current_link.split('?')[0] #this needs to be changed
                #    print("This link no longer has parameters ",current_link)
            
                #PATH_DICT NEEDS TO UNIFORMLY BE ADDING HTTP:// TO ALL LINK SO WE DON'T GET TWO VERSION OF THE SAME LINK           tentative value
                if (in_domain or also_in_domain) and is_valid(current_link) and current_link not in path_dict and if word_count > 150:
    
                    print(current_link)
                    lst.append(current_link)
                    path_dict[current_link] = 1

                    no_path = current_link.rsplit('/') #grabs 'https://mswe.ics.uci.edu' from 'https://mswe.ics.uci.edu/faq/' for ics dict
                    no_path = 'http:/' + ['/'.join(no_path[1:3])][0]

                    if '.ics.uci.edu' in no_path:
                        if no_path not in ics_subdomain_dict:
                            ics_subdomain_dict[no_path] = 1 
                        else:       
                            ics_subdomain_dict[no_path] += 1                                 
            

    
    print("ICS DICT: ", ics_subdomain_dict)                
    print("LONGEST PAGE: ",longest_page)
    return lst

def is_valid(url):

    try:
        parsed = urlparse(url)
        check = requests.get(url)
        content_type = check.headers.get('content-type')
        if parsed.scheme not in set(["http", "https"]):
            return False
        #if 'calendar' in url: #here for now just to get rid of obvious cases but want to change
        #    return False
        if validate(url):  
            return False
        if validate2(url):  
            return False
        if check.status_code != 200:
            return False
        if content_type and 'pdf' in content_type: #make then apply to more types that are getting in there
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

