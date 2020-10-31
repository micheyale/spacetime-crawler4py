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
    lst = []
    #add 404 checking raw_respons
    # regex for "https?:// [any str of characters] ics.uci.edu"
    # if theres a match add it to ics_subdomain_dict then look at it's
    # path, if that path doesn't appear in path_dict increment the value of ics_subdomain_dict[match]
    # else do not add it 

    if resp.status == 200:
        page = requests.get(url)
        bSoup = BeautifulSoup(page.content,'html.parser')
        links_lst = bSoup.find_all('a')
        for link in links_lst:
            if 'href' in link.attrs and is_valid(url):
                check_pages = re.findall('^https?://[^#]+',link.attrs['href'])
                check_ics_subdomain =  re.findall('^https?://[https?:// [any str of characters] ics.uci.edu]',link.attrs['href'])
                print("ICS SUBDOMAIN: ",check_ics_subdomain)
                if check_ics_subdomain: # if there was a match
                    if check_ics_subdomain[0] not in ics_subdomain_dict:
                        ics_subdomain_dict[check_ics_subdomain[0]] = 1 # so far there has been one occurance of it
                        #add the entire link to path_dict
                    else: # it is in there so we need to figure out if we have to increment its page
                        if link.attrs['href'] not in path_dict:
                            path_dict[link.attrs['href']] = 1 
                            ics_subdomain_dict[check_ics_subdomain[0]] += 1                       
                    

                if check_pages:
                    domain_set.add(check_pages[0])
                              
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
