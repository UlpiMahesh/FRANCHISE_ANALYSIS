import requests as r
from bs4 import BeautifulSoup as bs

url = 'https://www.franchisebazar.com/'
response = r.get(url)

soup = bs(response.content,'html.parser')
cards = soup.find("ul", class_="franchise-container open")

industry_links = cards.find_all('li')

industries = {}
for li in industry_links:
    a_tag = li.find('a')
    if a_tag:
        link = a_tag['href']
        industry = a_tag.get_text(strip=True)
        industries[industry]=url+link

def get_industries(name,link):
    url = link
    response = r.get(url)
    soup = bs(response.content,'html.parser')
    cards = soup.find('div',class_="row karya")
    industry_link = cards.find_all('div',class_='investor-card-wrapper')
    franchise_details = {}
    for div in industry_link:
        link_tag=div.find('a')
        location_tag=div.find('div',class_='col-lg-8 col-xs-8 text-right')
        name_tag = div.find('div',class_='main-title')
        
        if name_tag and link_tag and location_tag:
            name = name_tag.get_text(strip=True)
            link = link_tag['href']
            city = location_tag.get_text(strip=True)
            franchise_details[name]=[url+link,city]
    return franchise_details
            
            
industry_franchies = []
for name,link in industries.items():
    industry_franchies.append((name,get_industries(name,link)))
# print(industry_franchies)

