import os
import hashlib
import re
import csv
import requests as r
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor as te,as_completed 
from concurrent.futures import ThreadPoolExecutor as te
from urllib.parse import urlparse

# Create folder if it doesn't exist in current working directory
CACHE_DIR = "cached_pages"
os.makedirs(CACHE_DIR, exist_ok=True)

def sanitize_filename(url):
    """
    Create a readable filename from a URL (e.g., franchisebazar.com_industry_food.html)
    """
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    path = parsed.path.strip('/').replace('/', '_')
    filename = f"{domain}_{path}.html"
    # Remove illegal characters (Windows safe)
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    return filename

def cache_url(url, refresh=False, retries=3, delay=2):
    filename = sanitize_filename(url)
    filepath = os.path.join(CACHE_DIR, filename)

    if os.path.exists(filepath) and not refresh:
        with open(filepath, 'r', encoding='utf-8') as file:
            print(f"[CACHE] Using cached: {filepath}")
            return file.read()

    print(f"[LIVE] Fetching and caching: {url}")

    attempt = 0
    while attempt < retries:
        try:
            response = r.get(url, timeout=20)  #  timeout increased to 20s
            response.raise_for_status()        #  catches HTTP errors like 403/404
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(response.text)
            return response.text
        except r.exceptions.Timeout:           #  retry on timeout
            attempt += 1
            print(f"[TIMEOUT] Attempt {attempt} failed for {url}")
            time.sleep(delay)
        except r.exceptions.RequestException as e:  #  handles all other request failures
            print(f"[ERROR] Failed to fetch {url}: {e}")
            break

    return ""  # graceful fallback on final failure



# this function gets the franchise details like name of franchise city and link for further data fetching
def get_industries(name,link):
    try:
        industry_type=name
        url = 'https://www.franchisebazar.com/'
        response = cache_url(link)
        soup = bs(response,'html.parser')
        cards = soup.find('div',class_="row karya")
        #if no output from above code then empty dictionary will be returned
        if not cards:
            return (name,{})
            
        industry_link = cards.find_all('div',class_='investor-card-wrapper')
        
        franchise_details = {}
        for div in industry_link:
            link_tag=div.find('a')
            location_tag=div.find('div',class_='col-lg-8 col-xs-8 text-right')
            name_tag = div.find('div',class_='main-title')
            
            if name_tag and link_tag and location_tag:
                franchise_name = name_tag.get_text(strip=True)
                link = link_tag['href']
                city = location_tag.get_text(strip=True)
                franchise_details[franchise_name]=[url+link,city]
        return industry_type,franchise_details
        
    except Exception as e:
        return (name,{"error":str(e)})
            
industry_franchies = []
with te(max_workers=10) as executor:
    futures=[executor.submit(get_industries,name,link) for name,link in industries.items()]
for future in as_completed(futures):
    industry_franchies.append((future.result()))


#below code calls the function get_industry_details and write output into csv file

output_file=r"C:\Users\91994\Downloads\Franchise_analysis\DATA_EXTRACTION\industry_initial_details.txt"
with open(output_file, mode='w', newline='', encoding='utf-8') as file:
    writer=csv.writer(file)
    writer.writerow(["INDUSTRY_NAME","franchise_name","city",'space','investment','no_of_outlets'])
    
    for iname,idict in industry_franchies:
        with te(max_workers=10) as executor:
            futures=[executor.submit(get_industry_details,fname,flist[0],flist[1]) for fname,flist in idict.items()]
        for future in as_completed(futures):
            result = future.result()
            writer.writerow([iname,result[0],result[1],result[2],result[3],result[4]])

# This function gets franchise details like investment, space , number of outlets 

def get_industry_details(name,link,city):
    response=cache_url(link)
    soup = bs(response,'html.parser')
    box = soup.find('div',class_='head-list')
    if not box:
        return([name,city,'','',''])
    industry_details = [name,city]
    franchise_details_tag=box.find_all('div',class_='head-item')
    for div in franchise_details_tag:
        head_tags=div.find_all('div',class_='head-title')
        desc_tags=div.find_all('div',class_='head-desc')
        
        for tag in desc_tags:
            industry_details.append(tag.get_text(strip=True))
    return industry_details
                                    
        
    

'''
    below code executes and gets the first page of our url
'''

url = 'https://www.franchisebazar.com/'
response = cache_url(url)

soup = bs(response,'html.parser')
cards = soup.find("ul", class_="franchise-container open")

industry_links = cards.find_all('li')

industries = {}
for li in industry_links:
    a_tag = li.find('a')
    if a_tag:
        link = a_tag['href']
        industry = a_tag.get_text(strip=True)
        industries[industry]=url+link
# print(industries)

