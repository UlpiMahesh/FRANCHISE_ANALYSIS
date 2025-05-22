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