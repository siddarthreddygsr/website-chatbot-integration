import requests
from bs4 import BeautifulSoup
import csv
import pdb
import time
from datetime import datetime, timezone
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService


from utils.misc import csv_init, generate_hash

# basic init
SITEMAP_URLS_CSV = "data/sitemap.csv"
URLS_CSV = "data/urls.csv"
CSV_HEADERS = ["link", "datemod", "dateadded", "hash"]
csv_init(SITEMAP_URLS_CSV, CSV_HEADERS)
csv_init(URLS_CSV, CSV_HEADERS)
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)
main_sitemap_url = "https://cognitus.com/sitemap.xml"

driver.get(main_sitemap_url)
time.sleep(10)
cookie = driver.get_cookies()[0]['value']
user_agent = driver.execute_script("return navigator.userAgent;")
header = {
    "Cookie": f"_I_={cookie}",
    'User-Agent': user_agent,
}

response = requests.get(main_sitemap_url, headers=header)
main_sitemap_soup = BeautifulSoup(response.text, "xml")
sub_sitemaps = []

current_datetime = datetime.now(timezone.utc)
formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S+00:00")

for sitemap in main_sitemap_soup.find_all("sitemap"):
    link = sitemap.find("loc").text
    date = sitemap.find("lastmod").text
    node = {
        "link": link,
        "datemod": date,
        "dateadded": formatted_datetime,
        "hash": generate_hash(link)
    }
    sub_sitemaps.append(node)

existing_hashes = set()
with open('data/sitemap.csv', mode='r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        existing_hashes.add(row['hash'])

with open(SITEMAP_URLS_CSV, mode="a", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=CSV_HEADERS)
    for sitemap in sub_sitemaps:
        if sitemap['hash'] not in existing_hashes:
            writer.writerow(sitemap)

urls = []
for sitemap in tqdm(sub_sitemaps):
    response = requests.get(sitemap["link"], headers=header)
    sitemap_soup = BeautifulSoup(response.text, "xml")
    for url_data in sitemap_soup.find_all('url'):
        link = url_data.find('loc').text
        datemod = url_data.find('lastmod').text
        node = {
            "link": link,
            "datemod": date,
            "dateadded": formatted_datetime,
            "hash": generate_hash(link)
        }
        urls.append(node)

urls_hashes = set()
with open('data/urls.csv', mode='r', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        urls_hashes.add(row['hash'])

with open("data/urls.csv", mode="a", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["link", "datemod", "hash", "dateadded"])
    for url in urls:
        if url['hash'] not in urls_hashes:
            writer.writerow(url)



with open('data/urls.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if row[0] == "link":
            continue
        else:
            driver.get(row[0])
            ps = driver.page_source
            bot_detected = "Checking the site connection security"
            if bot_detected in ps:
                pdb.set_trace()
            text_elements = driver.find_elements(By.XPATH, "//*[not(self::script or self::style)]")
            text_content = "\n".join([element.text for element in text_elements])
            with open(f"data/crawled_data/{row[2]}.txt", "w", encoding="utf-8") as file:
                file.write(text_content) 
driver.quit()


