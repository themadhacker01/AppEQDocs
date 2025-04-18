import requests
import json
import time
import uuid
from bs4 import BeautifulSoup

BASE_URL = 'https://help.appeq.ai'
COLLECTION_URL = f'{BASE_URL}/en/collections/4350326-features'
CHUNK_SIZE = 300
OVERLAP = 50

def get_article_links():
    res = requests.get(COLLECTION_URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Article links
    links = soup.select('a[data-testid="article-link"]')
    article_urls = [link['href'] for link in links]
    print(f'✅ Found {len(article_urls)} articles.')

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
    print(f'Scraping article {title}...')

    return {'title': title, 'url': url, 'content': content}

def write_articles_to_file(articles_data, filename='appeq_articles.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, indent=2, ensure_ascii=False)
    print(f'✅ Saved {len(articles_data)} articles to {filename}')

def chunk_articles(articles, chunk_size, overlap, filename):
    chunks = []
    for article in articles:
        words = article['content'].split()
        start = 0
        while start < len(words):
            end = start + chunk_size
            chunk_text = ' '.join(words[start:end])
            chunks.append({
                'chunk_id': str(uuid.uuid4()),
                'title': article['title'],
                'url': article['url'],
                'text': chunk_text
            })
            start += chunk_size - overlap

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f'✅ Saved {len(chunks)} chunks to {filename}')

def main():
    articles_content = []
    urls = get_article_links()

    for url in urls:
        try:
            data = get_article_content(url)
            articles_content.append(data)
            time.sleep(1)  # Polite delay
        except Exception as e:
            print(f'❌ Error processing {url}: {e}')

    write_articles_to_file(articles_content)

    chunk_articles(articles_content, chunk_size=CHUNK_SIZE, overlap=OVERLAP, filename='appeq_chunks.json')

if __name__ == '__main__':
    main()
