import requests
import json
import uuid
from bs4 import BeautifulSoup

BASE_URL = 'https://help.appeq.ai/en'
IGNORE_URLS = [
    'https://help.appeq.ai/en/collections/4065352-release-notes'
]
CHUNK_SIZE = 300
OVERLAP = 50

def get_all_collection_urls(base_url):
    res = requests.get(base_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.select('a[data-testid="collection-card-classic"]')
    return [BASE_URL.rstrip('/') + link['href'] for link in links]

def get_article_links(collection_url):
    res = requests.get(collection_url)
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
    all_articles_content = []
    collection_urls = get_all_collection_urls(base_url=BASE_URL)

    for collection_url in collection_urls:
        print(f'Processing collection: {collection_url}')
        article_urls = get_article_links(collection_url)

        for article_url in article_urls:
            try:
                article_content = get_article_content(article_url)
                all_articles_content.append(article_content)
            except Exception as e:
                print(f'Error processing {article_url}: {e}')

    write_articles_to_file(all_articles_content)

    chunk_articles(all_articles_content, chunk_size=CHUNK_SIZE, overlap=OVERLAP, filename='appeq_chunks.json')

if __name__ == '__main__':
    main()
