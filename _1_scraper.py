import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = 'https://help.appeq.ai'
COLLECTION_URL = f'{BASE_URL}/en/collections/4350326-features'

def get_article_links():
    res = requests.get(COLLECTION_URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Article links
    links = soup.select('a[data-testid="article-link"]')
    article_urls = [link['href'] for link in links]
    print(f'✅ Found {len(article_urls)} articles.', '\n', article_urls)

    return article_urls

def get_article_content(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    title_tag = soup.select_one('h1')
    body_tag = soup.select_one('div.jsx-ef86202475c6562f ')

    if not title_tag or not body_tag:
        raise ValueError('Could not parse article structure.', url)

    title = title_tag.text.strip()
    content = body_tag.get_text(separator='\n').strip()

    return {'title': title, 'url': url, 'content': content}

def write_articles_to_file(articles_data, filename='appeq_articles.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, indent=2, ensure_ascii=False)
    print(f'✅ Saved {len(articles_data)} articles to {filename}')

def main():
    articles_data = []
    urls = get_article_links()

    for url in urls:
        try:
            data = get_article_content(url)
            articles_data.append(data)
            time.sleep(1)  # Polite delay
        except Exception as e:
            print(f'❌ Error processing {url}: {e}')

    write_articles_to_file(articles_data)

if __name__ == '__main__':
    main()
