# Cognitus Chatbot

## Installation and usage

To start the bot you have to scrape the data from Cognitus website which can be done by using

```
python3 -m venv env
pip install -r requirements.txt
python3 scrape.py
```

**Note:** This is the only part of the entire project that is not dockerised as it needs selenium to 
1. Get the browser cookies to prevent being detected as a bot 
2. Solve the captcha if needed 
    - happens very rarely but does happen
    - this part can be automated using services like deathbycaptcha, but it occurs too rarely (1 out of 1088 crawls) that it can be ignored for now and be automated in production during deployment.

This create a database of with 2 tables
1. urls table - has links to all pages and their last updated date according to the sitemap and its last scraped date
2. sitemaps table - has links to all sitemaps and their last updated date according to the sitemap and its last scraped date

When `scrape.py` is run for the first time it scrapes all the sitemaps and all the pages in the website, once this is done and the database is built, whenever the script is run again it checks the main sitemap and then only when a sitemap's last modified date is greater than the database's value for that url's last scraped date it scrapes and page and check which page was updated in that sitemap and then only crawls the website and updates the crawled_html data.

### Starting the frontend and backend 

To start the chatbot run
```
docker-compose up
```

This builds 2 docker images one for frontend with node and the other for backend (built using fastapi), the frontend docker container has the backend as a dependency to start

**Note:** The first message after the docker containers start running takes a bit longer as it would be setting up ollama


## Technical info
Model used - Microsoft phi 3 
Microsoft phi 3 is an open source LLM which is capable of running on machines/servers with lower specs reducing the cost of deployment.

Vector DB for RAG - ChromaDB
It is an open source vector database, which maintains the performance when scaled for heavy workloads.

Backend - FastAPI

## Further improvements

1. Retrieval Optimisation:
    - Query Rewriting: Use LLMs to rephrase user queries for better alignment with the indexed data.
    - Multi-Query Retrieval: Generate multiple queries from different perspectives to address complex problems.
2. Contextual Compression: 
    - Compress retrieved documents to reduce noise and highlight pivotal paragraphs.
3. Utilize previous chat history: 
    - Append the current user's chat history to the prompt. This provides important context that can help the chatbot better understand the user's intent and generate more coherent and relevant responses.




