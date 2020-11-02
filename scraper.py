import re
from urllib.parse import urlparse
import requests
import validators
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import tokenizer

path_dict = {}
ics_subdomain_dict = dict()
common_word = {}
tokenDict = {}
trap_url = []




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

def extract_next_links(url, resp):
    lst = []
    check_trap = []
    
    if resp.status == 200:
        html = urllib.request.urlopen(url).read()
        bodyText = text_from_html(html)
        tokenizer.updateTokenCounts(tokenDict, bodyText)

        page = requests.get(url,auth=('user', 'pass'))
        bSoup = BeautifulSoup(page.content,'html.parser')
        links_lst = bSoup.find_all('a')
        parsed_uri = urlparse(url)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        

        for link in links_lst:
        
            if 'href' in link.attrs:
                missing_domain_check = result + link.attrs['href']
                
                    
                
                in_domain = re.search('https?://([a-z0-9]+[.])*uci[.]edu((\/\w+)*\/)?',link.attrs['href'])
                also_in_domain = re.search('https?://([a-z0-9]+[.])*uci[.]edu((\/\w+)*\/)?',missing_domain_check)
                current_link = link.attrs['href']

                if also_in_domain and not in_domain:
                    if link.attrs['href'][0] == '/':
                        current_link = missing_domain_check
        
                
                if in_domain or also_in_domain and is_valid(current_link) and current_link.rsplit('/',1)[0] in trap_url:
                    
                       
                    if '#' in current_link:
                        current_link = current_link.split('#')[0]
                        print("LINK HAS BEEN DEFRAGGED: ",current_link)
                    try:
                        check = requests.get(current_link)                    
                        if current_link not in path_dict and check.status_code == 200:
                            print(current_link)
                            lst.append(current_link)
                            path_dict[current_link] = 1
                            
                            ct = current_link.rsplit('/',1)

                            if ct[-1].isdigit():
                                check_trap.append(ct[-1])
                                if len(check_trap) == 2 and abs(int(check_trap[0]) - int(check_trap[1])) == 1:
                                    trap_url.append(ct[0])
                                    check_trap = []
                                    
                                elif len(check_trap) == 2 and abs(int(check_trap[0]) - int(check_trap[1])) != 1:
                                    check_trap = []  
                            else:
                                check_trap = []

                            if '.ics.uci.edu' in result and result not in ics_subdomain_dict:
                                ics_subdomain_dict[result] = 1 # so far there has been one occurance of it
                                       
                            elif '.ics.uci.edu' in result and result in ics_subdomain_dict: # it is in there so we need to figure out if we have to increment its page
                                ics_subdomain_dict[result] += 1                                 
            

                    except requests.ConnectionError:
                        print(current_link, " is not a valid website.")
                            

    return lst
def web_exists(url): 
    check = validators.url(url)
    if(check == False):
        return False;
    else:
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
