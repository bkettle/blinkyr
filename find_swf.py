import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin # for resolving relative links

FLASH_CONTENT_TYPE = 'application/x-shockwave-flash'

SWF_PATTERN = """(?<=["'])[^"']+\.swf(?=["'])"""

def find_swf(url):
    """
    finds the swf file at the given website

    """
    r = requests.get(url)
    file_list = set()
    matches = re.findall(SWF_PATTERN, r.text)
    print(matches)
    if matches:
        file_list = set(match for match in matches) # trim leading and trailing quotations
    print(file_list)

    swf_urls = [urljoin(url, filename) for filename in file_list]
    print("Unfiltered SWFs:", swf_urls)

    # get page title
    soup = BeautifulSoup(r.text, features="html.parser")
    title = soup.title.string

    # check to make sure all URLs are valid current SWF files
    filtered_swf_urls = []
    for url in swf_urls:
        r = requests.head(url)
        content_type = r.headers['content-type']
        if content_type == FLASH_CONTENT_TYPE:
            filtered_swf_urls.append(url)

    return title, filtered_swf_urls


# for testing
#find_swf("https://www1.udel.edu/biology/ketcham/microscope/scope.html")
#print(find_swf("https://learn.genetics.utah.edu/content/basics/oldtour/"))
