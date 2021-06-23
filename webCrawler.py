import requests
from sys import argv
from colorama import Fore, init 
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup

#setting color variables
init(convert=True)
GREEN = Fore.GREEN
GRAY = Fore.LIGHTCYAN_EX
RESET = Fore.RESET
YELLOW = Fore.YELLOW
MAGNETA = Fore.MAGENTA
RED = Fore.RED

#sets to contain unique internal and external domain links
int_links = set()
ext_links = set()

#Converting URL into a valid form and checking for redirections
def urlValidator(url):
    parsed = urlparse(url)
    while 1:
        try:
            response = requests.get(url)
        except requests.exceptions.MissingSchema:
            parsed = parsed._replace(scheme = 'https')
            url = urlunparse(parsed)
            if url.find(':///', 0, 9) >= 0: url = url.replace(':///', '://')
        except requests.exceptions.SSLError:
            parsed = parsed._replace(scheme = 'http')
            url = urlunparse(parsed)
            if url.find(':///', 0, 9) >= 0: url = url.replace(':///', '://')
        except Exception as e:
            print(e.__class__)
            break
        else:
            print()
            if url != response.url:
                print(f"{GRAY}[*] Redirecting Link to: {response.url}{RESET}")
            url = response.url
            parsed = urlparse(url)
            url = parsed.scheme + '://' + parsed.netloc + parsed.path
            url = url.rstrip('/')
            return(url)

#to check wheather the link is valid URL or not
def isValid(link):
    parsed = urlparse(link)
    return bool(parsed.netloc) and bool(parsed.scheme)

def getWebsitesFromUrl(url):
    global int_links
    global ext_links
    temSetOfIntLinks = int_links.copy()
    urls = set()
    domainName = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, 'html5lib')

    #find all the anchor tags from the webpage and then extract the href attributes
    #for redirects in soup.findAll('location.href')
    for a_tag in soup.findAll('a'):
        href = a_tag.attrs.get('href')
        if href == '' or href is None:
            #href empty tag
            continue
        
        #join the URL is it's relative (like /search)
        href = urljoin(url, href)

        parsed_href = urlparse(href)
        #remove all GET parameters from, URL fragments etc.
        href = parsed_href.scheme + '://' + parsed_href.netloc + parsed_href.path
        href = href.rstrip('/')
        if not isValid(href):
            #not a valid url
            continue

        if href in int_links:
            #already in the set
            continue

        if domainName not in href:
            #external link
            if href not in ext_links:
                print(f"{MAGNETA}[*] External Link: {href}{RESET}")
                ext_links.add(href)
            continue
        
        urls.add(href)
        print(f"{GREEN}[*] Internal Link: {href}{RESET}")
        int_links.add(href)
    
    #To remove already added links from the current urls set from internal links set
    urls = urls - temSetOfIntLinks
    return urls

#number of urls visited will be stored here
totalVisitedUrls = 0

#crawl the current webpage and extract links recursively
'''
maxUrls is set to 30 because if we don't keep it limited then it might take
a lot of time for big sites
'''
def crawlPage(url, maxUrls):
    global totalVisitedUrls
    totalVisitedUrls += 1

    print()
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    links = getWebsitesFromUrl(url)

    for link in links:
        if totalVisitedUrls >= maxUrls:
            break
        crawlPage(link, maxUrls)

if __name__ == "__main__":

    intLinkFile = open('InternalLinks.txt', 'w')
    extLinkFile = open('ExternalLinks.txt', 'w')

    url = ''
    maxUrls = 0
    if len(argv) > 1: 
        url = argv[1]
        maxUrls = int(argv[2])
    else: 
        url = input("Enter the base URL: ")
        while 1:
            try:
                maxUrls = int(input("Enter number of max links to Crawl: "))
                if maxUrls <= 0: raise
            except:
                print(f'{RED}[ERROR]: Please Enter Integer value greater than 0{RESET}')
            else: break

    url = urlValidator(url)    
    int_links.add(url)
    crawlPage(url, maxUrls)
    int_links.remove(url)

    for link in int_links:
        intLinkFile.write(link)
        intLinkFile.write('\n')

    for link in ext_links:
        extLinkFile.write(link)
        extLinkFile.write('\n')

    print()
    print('[*]Total Crawled URLS:', totalVisitedUrls)
    print('[*]Total Internal Links:', len(int_links))
    print('[*]Total External Links:', len(ext_links))
    print()
    input('Enter any key to Exit...')
