import requests
from bs4 import BeautifulSoup
import csv
import pdb
import time
import sqlite3
from datetime import datetime, timezone
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By

from utils.misc import csv_init, generate_hash

# basic init
DATABASE_FILE = "data.sqlite3"
chrome_options = Options()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(10) 
main_sitemap_url = "https://cognitus.com/sitemap.xml"
conn = sqlite3.connect(DATABASE_FILE)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS sitemaps (
             id INTEGER PRIMARY KEY,
             link TEXT,
             datemod TEXT,
             dateadded TEXT,
             hash TEXT
         )""")

c.execute("""CREATE TABLE IF NOT EXISTS urls (
             id INTEGER PRIMARY KEY,
             link TEXT,
             datemod TEXT,
             dateadded TEXT,
             hash TEXT
         )""")


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

current_datetime = datetime.now(timezone.utc)
formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S+00:00")

sub_sitemaps = []
sub_sitemaps_to_scrape = []
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

c.execute("SELECT hash FROM sitemaps")
existing_hashes = set([row["hash"] for row in c.fetchall()])

# add new entries of missing sitemaps
for sitemap in sub_sitemaps:
    c.execute("SELECT * From sitemaps where hash= ?", (sitemap["hash"],))
    db_row = c.fetchone()
    if sitemap['hash'] not in existing_hashes:
        c.execute("INSERT INTO sitemaps (link, datemod, dateadded, hash) VALUES (?, ?, ?, ?)", 
                  (sitemap['link'], sitemap['datemod'], sitemap['dateadded'], sitemap['hash']))
        conn.commit()
        sub_sitemaps_to_scrape.append(sitemap)
    elif db_row and db_row['dateadded'] < sitemap['datemod']:
        c.execute("UPDATE sitemaps SET dateadded = ? WHERE hash = ?", (current_datetime,sitemap["hash"],))
        conn.commit()
        sub_sitemaps_to_scrape.append(sitemap)

urls = []
for sitemap in tqdm(sub_sitemaps_to_scrape):
    response = requests.get(sitemap["link"], headers=header)
    sitemap_soup = BeautifulSoup(response.text, "xml")
    for url_data in sitemap_soup.find_all('url'):
        link = url_data.find('loc').text
        datemod = url_data.find('lastmod').text
        node = {
            "link": link,
            "datemod": datemod,
            "dateadded": formatted_datetime,
            "hash": generate_hash(link)
        }
        urls.append(node)

c.execute("SELECT hash FROM urls")
urls_hashes = set([row[0] for row in c.fetchall()])

urls_to_scrape = []
for url in urls:
    c.execute("SELECT * From urls where hash= ?", (url["hash"],))
    db_row = c.fetchone()
    if url['hash'] not in urls_hashes:
        c.execute("INSERT INTO urls (link, datemod, dateadded, hash) VALUES (?, ?, ?, ?)",
                  (url['link'], url['datemod'], url['dateadded'], url['hash']))
        conn.commit()
        urls_to_scrape.append(url)
    elif db_row and db_row['dateadded'] < url['datemod']:
        c.execute("UPDATE urls SET dateadded = ? WHERE hash = ?", (current_datetime,url["hash"],))
        conn.commit()
        urls_to_scrape.append(url)

for url in urls_to_scrape:
    driver.get(url["link"])
    ps = driver.page_source
    bot_detected = "Checking the site connection security"
    if bot_detected in ps:
        pdb.set_trace()
    with open(f"data/crawled_html/{url['hash']}.html", "w", encoding="utf-8") as file:
        file.write(ps)
driver.quit()
