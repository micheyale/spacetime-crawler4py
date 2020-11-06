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
path_dict = { 'http://www.stat.uci.edu/news/page/9':1,
'http://www.stat.uci.edu/news/page/7':1,
'http://www.stat.uci.edu/news/page/5':1,
'http://www.stat.uci.edu/news/page/4':1,
'http://www.stat.uci.edu/senior-spotlight-james-purpura-goes-from-watching-moneyball-to-earning-data-science-degree':1,
'http://www.informatics.uci.edu/explore/faculty-profiles/cristina-lopes':1,
'http://mswe.ics.uci.edu/career/internships':1,
'http://mswe.ics.uci.edu/faq':1,
'http://mswe.ics.uci.edu': 1,
'http://mse.ics.uci.edu//faq':1,
'http://mse.ics.uci.edu/%20':1,
'http://www.informatics.uci.edu/explore/faculty-profiles/sam-malek':1,
'http://mswe.ics.uci.edu/career':1,
'https://www.stat.uci.edu':1,
'http://www.stat.uci.edu///www.stat.uci.edu/news':1,
'http://www.informatics.uci.edu/support/become-a-mentor':1,
'http://www.informatics.uci.edu/menu-very-top/contact':1,
'http://www.ics.uci.edu/community/events/competition':1,
'http://mswe.ics.uci.edu/career/personal-branding-networking':1,
'http://mswe.ics.uci.edu//faq':1,
'http://www.stat.uci.edu/professor-guindani-named-incoming-editor-in-chief-of-bayesian-analysis':1,
'http://www.informatics.uci.edu/explore/books-we-have-written':1,
'http://www.informatics.uci.edu/explore/department-seminars':1,
'http://www.stat.uci.edu/trio-of-ics-professors-preview-tech-trends-for-2019':1,
'http://www.stat.uci.edu/a-campus-gem-ucis-statistical-consulting-services':1,
'http://www.ics.uci.edu/~babaks/index.html':1,
'http://www.ics.uci.edu/community/news/view_news?id=1595':1,
'http://www.ics.uci.edu/about/about_contact.php':1,
'http://www.ics.uci.edu/about':1,
'http://www.ics.uci.edu/about/about_safety.php':1,
'http://www.ics.uci.edu/accessibility':1,
'http://www.ics.uci.edu/about/visit/index.php':1,
'http://www.ics.uci.edu/about/visit':1,
'http://www.ics.uci.edu/about/facilities/index.php':1,
'http://www.ics.uci.edu/about/facilities':1,
'http://www.ics.uci.edu/about/kfflab/index.php':1,
'http://www.ics.uci.edu/about/kfflab':1,
'http://www.ics.uci.edu/employment':1,
'http://www.ics.uci.edu/about/search/index.php':1,
'http://www.ics.uci.edu//faculty/faculty_dept?department=Statistics':1,
'http://www.ics.uci.edu//faculty/profiles/view_faculty.php?ucinetid=zhaoxia':1,
'http://www.ics.uci.edu/~zhaoxia':1,
'http://www.ics.uci.edu/~yamingy':1,
'http://www.ics.uci.edu/~yamingy/npmle.c':1,
'http://www.ics.uci.edu/statistics/faculty':1,
'http://www.ics.uci.edu/faculty/profiles/view_faculty.php?ucinetid=jutts':1,
'http://www.ics.uci.edu/~sudderth':1,
'http://www.ics.uci.edu/~ihler':1,
'http://cml.ics.uci.edu/?page=events&subPage=aiml':1,
'http://cml.ics.uci.edu/?cat=4':1,
'http://cml.ics.uci.edu/category/news/page/2':1,
'http://www.ics.uci.edu/community/news/view_news?id=1817':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1818':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1819':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1820':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1821':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1822':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1823':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1824':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1825':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1826':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1827':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1828':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1829':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1830':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1831':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1832':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1833':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1834':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1835':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1836':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1837':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1838':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1839':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1840':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1841':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1842':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1843':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1844':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1845':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1846':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1847':1,
'http://www.ics.uci.edu//community/news/view_news.php?id=1848':1,
'http://www.ics.uci.edu/~iftekha':1,
'http://www.ics.uci.edu/~iftekha/publication/does-the-choice-of-mutation-tool-mattertr':1,
'http://www.ics.uci.edu/~iftekha/publication/how-hard-does-mutation-analysis-have-to-be-anyway':1,
'http://www.ics.uci.edu/~iftekha/publication/understanding-code-smells-in-android-applications':1,
'http://www.ics.uci.edu/~iftekha/publication/can-testedness-be-effectively-measured':1,
'http://www.ics.uci.edu/~iftekha/publication/an-empirical-examination-of-the-relationship-between-code-smells-and-merge-conflicts':1,
'http://www.ics.uci.edu/~iftekha/publication/understanding-development-process-of-machine-learning-systems-challenges-and-solutions':1,
'http://www.ics.uci.edu/~iftekha/publication/land-of-lost-knowledge-an-initial-investigation-into-projects-lost-knowledge':1,
'http://www.ics.uci.edu/~iftekha/publication/a-multiple-case-study-of-artificial-intelligent-system-development-in-industry':1,
'http://www.ics.uci.edu//~iftekha/publication':1,
'http://www.ics.uci.edu//~iftekha':1,
'http://www.ics.uci.edu/community/news/view_news?id=1626':1,
'http://wics.ics.uci.edu':1}
ics_subdomain_dict = {'http://mse.ics.uci.edu': 2, 'http://mswe.ics.uci.edu': 5, 'http://www.ics.uci.edu': 68, 'http://cml.ics.uci.edu': 2, 'http://wics.ics.uci.edu': 1}

common_word = {}
every_link = {}
longest_page = ("",0)
word_frequencies = {}
low_count = [] 

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
    # top50Word()                               
    return [link for link in links if is_valid(link)]
#################################################################################################
def validate(date_text1):
    try:
        if date_text1 != datetime.strptime(date_text1, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
        
    except ValueError:
        return False
def validate2(date_text1):
    try:
        if date_text1 != datetime.strptime(date_text1, "%Y-%m").strftime('%Y-%m'):
            raise ValueError
        return True
    except ValueError:
        return False
def validate3(date_text2):
    try:
        if date_text2 != datetime.strptime(date_text2, "%Y-%m").strftime('%Y-%m'):
            raise ValueError
        return True
    except ValueError:
        return False
def validate4(date_text3):
    try:
        if date_text3 != datetime.strptime(date_text3, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False
######################################################################################################
def in_domain(url):
    for i in ['.ics.uci.edu','.cs.uci.edu','.informatics.uci.edu','.stat.uci.edu','today.uci.edu/department/information_computer_sciences']:
        if i in url:
            return True
    return False

def low_content_link(url):
    for l in low_count:
        if l in url:
            return True
    return False
def extract_next_links(url, resp):
    lst = []
    tokenDict = {}
    global longest_page
    global word_frequencies

    if resp.status == 200 and not low_content_link(url) and url not in path_dict:
        try:
            html = urllib.request.urlopen(url).read()	  
            bodyText = text_from_html(html)	       
            tokenizer.updateTokenCounts(tokenDict, bodyText)
        except urllib.error.HTTPError:
            print("This URL: " + str(url) + " cannot be scraped for content.")
            return lst
        page = requests.get(url,auth=('user', 'pass'))
        bSoup = BeautifulSoup(page.content,'html.parser')
        links_lst = bSoup.find_all('a') #puts all hyperlinks in a lst
        
        parsed_uri = urlparse(url)
        result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri) #this allows us to keep track of a out parent domain in case we need to reconnect the path

        word_count = sum(tokenDict[d] for d in tokenDict if d.isalpha()) #only counting words on a page rn 
        print("WORD COUNT: ",word_count)
        if word_count > longest_page[1]:
            longest_page = (url,word_count)
            pickle.dump(longest_page,open('longest_page.txt','w'))

        # Update word_frequencies with the new tokenDict from each page
        for key, value in tokenDict.items():
            if key in word_frequencies:
                word_frequencies[key] += value
            else:
                word_frequencies[key] = value
        pickle.dump(word_frequencies,open('word_freq.txt','w'))
                
        if word_count > 200:
            print("BEGIN PARSING LINK: ",url)
            path_dict[url] = 1 #we are adding link to path_dict when we begin crawling that webpage NOT when we initially scrape the link
            no_path = url.rsplit('/') #grabs 'https://mswe.ics.uci.edu' from 'https://mswe.ics.uci.edu/faq/' for ics dict
            no_path = 'http:/' + ['/'.join(no_path[1:3])][0]

            if '.ics.uci.edu' in no_path:
                if no_path not in ics_subdomain_dict:
                    ics_subdomain_dict[no_path] = 1 #adds ics subdomain to dict with one occurance
                else:
                    if ics_subdomain_dict[no_path] > 65 and no_path != 'http://www.ics.uci.edu':
                        low_count.append(no_path)
                    ics_subdomain_dict[no_path] += 1 #increments the occurance of the ic subdomain that has appeared at least once
                pickle.dump(ics_subdomain_dict,open('ics_sub.txt','w'))
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
                    if in_domain(current_link) and is_valid(current_link) and current_link not in path_dict and current_link not in every_link:
                        print("link we're downloading: ",current_link)
                        every_link[current_link] = 1
                        pickle.dump(every_link,open('ev_link.txt','w'))
                        lst.append(current_link)
                                             

    print("PATH DICT: ",len(path_dict))
    print("ICS DICT: ", ics_subdomain_dict)                
    print("LONGEST PAGE: ",longest_page)
    if len(lst) < 5:
        if len(lst) == 1:
            lst = []
        if '?' in url:
            url = url.split('?')[0] 
            low_count.append(url)
    return lst
####################################################################################
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
         
            if validate3(date_text2):
                return False
            if validate4(date_text3):
                return False
        if url.rsplit('?')[1:] and 'share' in url.rsplit('?')[1:][0]: #returns False for URLs like: 'http://wics.ics.uci.edu/?share=twitter
            return False
        if check.status_code != 200: 
            return False   
        if content_type and 'text' not in content_type: #return False for webpages that do not contain text ie pdf or None
            return False
   ###############################################################################################     

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
