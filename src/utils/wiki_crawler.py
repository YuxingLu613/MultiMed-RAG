import sys
import time
import argparse
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

import collections
import collections.abc
collections.Callable = collections.abc.Callable

DEFAULT_INTERVAL = 5.0  # interval between requests (seconds)
DEFAULT_ARTICLES_LIMIT = 1  # total number articles to be extrated
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'

visited_urls = set()  # all urls already visited, to not visit twice
pending_urls = []  # queue


def load_urls(session_file):
    """Resume previous session if any, load visited URLs"""

    try:
        with open(session_file) as fin:
            for line in fin:
                visited_urls.add(line.strip())
    except FileNotFoundError:
        pass


def scrap_to_string(base_url, article):
    """Scrapes and returns article text as string instead of saving to file."""
    full_url = base_url + article
    try:
        r = requests.get(full_url, headers={'User-Agent': USER_AGENT})
    except requests.exceptions.ConnectionError:
        print("Check your Internet connection")
        return ""

    if r.status_code not in (200, 404):
        print("Failed to request page (code {})".format(r.status_code))
        return ""

    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find('div', {'id': 'mw-content-text'})

    parenthesis_regex = re.compile(r'\(.+?\)')  # remove parentheses
    citations_regex = re.compile(r'\[.+?\]')    # remove citations like [1]

    article_text = ""
    p_list = content.find_all('p')
    for p in p_list:
        text = p.get_text().strip()
        text = parenthesis_regex.sub('', text)
        text = citations_regex.sub('', text)
        if text:
            article_text += text + '\n\n'

    return article_text.strip()

def crawl_wikipedia(initial_url, articles_limit=1, interval=5.0):
    """Crawls Wikipedia articles starting from initial_url and returns extracted text."""
    from urllib.parse import urlparse
    import time

    visited_urls.clear()
    pending_urls.clear()

    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(initial_url))
    initial_path = initial_url[len(base_url):]
    pending_urls.append(initial_path)

    all_text = ""
    counter = 0

    while len(pending_urls) > 0:
        if counter >= articles_limit:
            break
        next_url = pending_urls.pop(0)
        if next_url in visited_urls:
            continue
        counter += 1
        time.sleep(interval)
        print(f"Crawling: {next_url}")
        article_text = scrap_to_string(base_url, next_url)
        if article_text:
            all_text += article_text + "\n\n"
            visited_urls.add(next_url)

        # Add new links
        try:
            r = requests.get(base_url + next_url, headers={'User-Agent': USER_AGENT})
            soup = BeautifulSoup(r.text, 'html.parser')
            content = soup.find('div', {'id': 'mw-content-text'})
            for a in content.find_all('a'):
                href = a.get('href')
                if not href or not href.startswith('/wiki/') or ':' in href:
                    continue
                if href in visited_urls or href in pending_urls:
                    continue
                pending_urls.append(href)
        except:
            continue

    return all_text.strip()

def crawl_wikipedia_entity(entity_name, articles_limit=1, interval=5.0):
    """Crawls Wikipedia articles given just an entity name like 'Biology'."""
    base_url = "https://en.wikipedia.org/wiki/"
    full_url = base_url + entity_name.replace(" ", "_")  # convert spaces to underscores
    return crawl_wikipedia(full_url, articles_limit, interval)