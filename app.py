import requests
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import math
import time
import streamlit as st
import tempfile
import urllib.robotparser
import pandas as pd
import io

# Download NLTK resources
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    st.error(f"Failed to download NLTK resources: {str(e)}")

# Streamlit app configuration
st.set_page_config(page_title="New York Times Scraper", page_icon="📰", layout="wide")
st.title("📰 New York Times Scraper")
st.subheader("Extract articles and analyze topics from The New York Times")

# Display crawlability rules
with st.expander("📜 Crawlability Rules", expanded=True):
    with st.container():
        st.subheader("Summary of Crawlability Rules for nytimes.com")
        st.write("**Date of Analysis**: May 20, 2025")
        st.write("**Content URL**: [https://www.nytimes.com/robots.txt](https://www.nytimes.com/robots.txt)")
        st.subheader("Crawlability Rules")
        st.write("The `robots.txt` file includes a legal notice with the following key points:")
        st.markdown("""
        - **Personal, Non-Commercial Use**: Content is for personal, non-commercial use under the [Terms of Service](https://www.nytimes.com/content/help/rights/terms/terms-of-service.html).
        - **Prohibition on Automated Scraping/Data Mining**: "Use of any device, tool, or process designed to data mine or scrape the content using automated means is prohibited without prior written permission from The New York Times Company."
        - **Specifically Prohibited Uses**:
          - Text and data mining activities (e.g., under EU Copyright Directive Art. 4).
          - Development of software, machine learning, artificial intelligence (AI), or large language models (LLMs).
          - Creating or providing archived or cached data sets containing their content.
          - Any commercial purposes.
        """)
        st.subheader("Specific User-Agent Directives")
        st.write("### Googlebot")
        st.markdown("""
        Googlebot is permitted to crawl for indexing but has restrictions:
        - **Disallowed Paths**: Includes `/ads/`, `/adx/bin/`, various `/athletic/` paths (e.g., `wp-admin` except `admin-ajax.php`, `checkout`, `login`, `report`, `discuss`, `register`, API/GraphQL endpoints), `/card/panel/`, `/panel/`, `/puzzles/leaderboards/invite/*`, most `/svc` except games and crosswords, `/video/embedded/*`, `/search`, `/multiproduct/`, `/hd/`, `/inyt/`, query parameters (e.g., `*?*query=`, `*?*login=`), and `*.pdf$`.
        - **Specific Disallows**: `/athletic*` URLs with `adgroupid`, `campaignid`, `ad_id`, `access_token`, `amp_reader_id`, `source=`, `embed=1`.
        - **Allowed Paths**: Includes `/athletic/wp/wp-admin/admin-ajax.php`, `/athletic/search/$`, `/athletic/login/$`, `/svc/crosswords`, `/svc/games`, `/svc/letter-boxed`, `/svc/spelling-bee`, `/svc/vertex`, `/svc/wordle`, `/ads/public/`.
        """)
        st.write("### AI and Data Collection Bots")
        st.markdown("""
        Many bots, especially for AI training or data collection, are **completely disallowed** (`Disallow: /`).
        """)
        with st.container():
            show_bots = st.checkbox("Show Disallowed Bots")
            if show_bots:
                st.markdown("""
                - anthropic-ai
                - Applebot-Extended
                - Bytespider
                - CCBot (Common Crawl)
                - ChatGPT-User (OpenAI)
                - ClaudeBot, Claude-Web (Anthropic)
                - cohere-ai
                - Google-Extended (Google AI)
                - GPTBot (OpenAI)
                - OAI-SearchBot
                - PerplexityBot
                - Others: Amazonbot, DataForSeoBot, Diffbot, FacebookBot, FriendlyCrawler, ImagesiftBot, magpie-crawler, Meta-ExternalAgent, NewsNow, news-please, omgili, omgilibot, peer39_crawler, Quora-Bot, Timpibot, TurnitinBot, YouBot
                """)
        st.write("### Scrapy")
        st.markdown("""
        - **Disallow: /**  
        Using the Scrapy framework with its default user agent is **explicitly prohibited** from crawling any part of nytimes.com.
        """)
        st.write("### Other Specific Bots")
        st.markdown("""
        - **Google-CloudVertexBot**: Disallowed (`Disallow: /`) except for `/wirecutter/`.
        - **facebookexternalhit, Twitterbot**: Allowed for URLs with `smid=` query parameter (for social media previews).
        - **AwarioRssBot**: No explicit `Disallow`, allowed by default but subject to Terms of Service.
        - **AwarioSmartBot**: Disallowed (`Disallow: /`).
        """)
        st.subheader("Crawl-delay Directive")
        st.markdown("""
        No `Crawl-delay` directive is specified. However, rapid crawling is not permitted due to prohibitions on automated scraping. Responsible crawling requires self-imposed delays.
        """)
        st.subheader("Sitemaps")
        st.markdown("""
        The site provides multiple sitemap files for structured access to content. These can help discover article URLs, but scraping must comply with the Terms of Service.
        """)
        with st.container():
            show_sitemaps = st.checkbox("Show Sitemap URLs")
            if show_sitemaps:
                st.markdown("""
                - https://www.nytimes.com/sitemaps/new/news.xml.gz
                - https://www.nytimes.com/sitemaps/new/sitemap.xml.gz
                - https://www.nytimes.com/sitemaps/new/collections.xml.gz
                - https://www.nytimes.com/sitemaps/new/video.xml.gz
                - https://www.nytimes.com/sitemaps/new/cooking.xml.gz
                - https://www.nytimes.com/sitemaps/new/recipe-collects.xml.gz
                - https://www.nytimes.com/sitemaps/new/regions.xml
                - https://www.nytimes.com/sitemaps/new/best-sellers.xml
                - https://www.nytimes.com/sitemaps/new/weather.xml.gz
                - https://www.nytimes.com/sitemaps/new/espanol.xml.gz
                - https://www.nytimes.com/sitemaps/new/espanol-collects.xml.gz
                - https://www.nytimes.com/wirecutter/sitemapindex.xml
                - https://www.nytimes.com/athletic/sitemap-authors.xml
                - https://www.nytimes.com/athletic/sitemap-verticals.xml
                - https://www.nytimes.com/athletic/sitemap-teams.xml
                - https://www.nytimes.com/athletic/sitemap-cities.xml
                - https://www.nytimes.com/athletic/sitemap.xml
                - https://www.nytimes.com/games-assets/v2/assets/sitemap/games.xml
                """)
        st.subheader("Conclusion on Crawlability")
        st.markdown("""
        Some paths are crawlable for user agents like Googlebot, but general automated tools, especially for data extraction or AI purposes (e.g., Scrapy, ChatGPT-User, GPTBot), face strict restrictions via `robots.txt` and the [Terms of Service](https://www.nytimes.com/content/help/rights/terms/terms-of-service.html). Sitemaps provide content discovery, but automated scraping is broadly prohibited. For compliant access, use the [NYT Developer API](https://developer.nytimes.com/).
        """)
        st.info("These rules are enforced automatically to ensure responsible scraping.")

# Define constants for web scraping and API
NYT_URL = "https://www.nytimes.com/"
ROBOTS_URL = "https://www.nytimes.com/robots.txt"
NYT_API_KEY = 'tTO8EfnrGsUovwLNDCUY0rQyNuDoNFnA'  # Replace with your actual NYT API key
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}
TARGET_ARTICLES_TO_SAVE = 100
URL_COLLECTION_TARGET = TARGET_ARTICLES_TO_SAVE + 100
MAX_SECTIONS_TO_PROCESS = 25

# Create temporary directory for output
output_dir = tempfile.mkdtemp()
st.write(f"Articles will be saved temporarily in: {output_dir}")

# Initialize robots.txt parser
rp = urllib.robotparser.RobotFileParser()
rp.set_url(ROBOTS_URL)
try:
    rp.read()
except Exception as e:
    st.warning(f"Failed to read robots.txt from {ROBOTS_URL}: {str(e)}. Assuming restrictive crawling policy.")

# Function to check if URL is crawlable
def is_crawl_allowed(url, user_agent=HEADERS['User-Agent']):
    try:
        allowed = rp.can_fetch(user_agent, url)
        if not allowed:
            st.warning(f"Crawling not permitted for {url} by robots.txt.")
        return allowed
    except Exception as e:
        st.error(f"Error checking robots.txt for {url}: {str(e)}. Assuming not allowed.")
        return False

# Function to fetch a page with retries and exponential backoff
def fetch_page(url, max_retries=3, delay_base=2):
    if not is_crawl_allowed(url):
        st.error(f"Skipping {url}: Crawling not permitted by robots.txt.")
        raise ValueError("Crawling not permitted by robots.txt")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            st.warning(f"Attempt {attempt+1}/{max_retries} failed for {url}: {str(e)}")
            if attempt < max_retries - 1:
                delay = delay_base * (2 ** attempt)
                st.write(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                st.error(f"Failed to fetch {url} after {max_retries} attempts.")
                raise
        except Exception as e:
            st.error(f"Unexpected error during fetch attempt {attempt+1} for {url}: {str(e)}")
            if attempt < max_retries - 1:
                delay = delay_base * (2 ** attempt)
                st.write(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                st.error(f"Failed to fetch {url} due to unexpected error after {max_retries} attempts.")
                raise

# Preprocessing and TF-IDF functions
def preprocess_document(document):
    stop_words_set = set(stopwords.words('english'))
    wordnet_lemmatizer = WordNetLemmatizer()
    words = word_tokenize(document)
    words = [word.lower() for word in words if word.isalpha()]
    words = [word for word in words if word not in stop_words_set]
    words = [wordnet_lemmatizer.lemmatize(word) for word in words]
    return words

def evaluate_term_frequency(document):
    term_frequency = {}
    processed_document = preprocess_document(document)
    for word in processed_document:
        term_frequency[word] = term_frequency.get(word, 0) + 1
    doc_length = len(processed_document)
    if doc_length == 0:
        return {}
    for word in term_frequency:
        term_frequency[word] /= doc_length
    return term_frequency

def evaluate_inverse_document_frequency(documents_list):
    inverse_document_frequency = {}
    total_documents = len(documents_list)
    if total_documents == 0:
        return {}
    all_words_in_docs = {}
    for document_content in documents_list:
        processed_doc = preprocess_document(document_content)
        unique_words_in_doc = set(processed_doc)
        for word in unique_words_in_doc:
            all_words_in_docs[word] = all_words_in_docs.get(word, 0) + 1
    for word, count in all_words_in_docs.items():
        inverse_document_frequency[word] = math.log(total_documents / (1 + count))
    return inverse_document_frequency

def evaluate_tf_idf(documents_list):
    tf_idf_scores_list = []
    if not documents_list:
        return tf_idf_scores_list
    idf_scores = evaluate_inverse_document_frequency(documents_list)
    for document_content in documents_list:
        tf_scores = evaluate_term_frequency(document_content)
        current_tf_idf = {word: tf_scores.get(word, 0) * idf_scores.get(word, 0) for word in tf_scores}
        tf_idf_scores_list.append(current_tf_idf)
    return tf_idf_scores_list

# Main web scraping function
def scrape_nyt():
    article_links_set = set()
    section_links_to_visit = []
    processed_section_links = set()
    successfully_saved_files = []
    saved_articles_count = 0

    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Starting article link collection...")

    try:
        status_text.text(f"Fetching homepage: {NYT_URL}")
        home_page_text = fetch_page(NYT_URL)
        soup = BeautifulSoup(home_page_text, 'html.parser')

        for a in soup.find_all('a', href=True):
            if len(article_links_set) >= URL_COLLECTION_TARGET:
                break
            href = a['href']
            if href.startswith(('https://www.nytimes.com/20', '/20')) and \
               not href.endswith(('.jpg', '.png', '/interactive/', '/video/', '.json', '.xml', '.rss')):
                if href.startswith('/'):
                    href = 'https://www.nytimes.com' + href
                if is_crawl_allowed(href):
                    article_links_set.add(href)

        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('/section/', 'https://www.nytimes.com/section/')):
                if href.startswith('/'):
                    href = 'https://www.nytimes.com' + href
                if href not in processed_section_links and href not in section_links_to_visit and is_crawl_allowed(href):
                    section_links_to_visit.append(href)
        status_text.text(f"Found {len(section_links_to_visit)} sections to explore.")
    except Exception as e:
        st.error(f"Failed to scrape homepage: {str(e)}")
        return [], []

    sections_processed_count = 0
    while len(article_links_set) < URL_COLLECTION_TARGET and section_links_to_visit and sections_processed_count < MAX_SECTIONS_TO_PROCESS:
        section_link = section_links_to_visit.pop(0)
        if section_link in processed_section_links:
            continue
        processed_section_links.add(section_link)
        sections_processed_count += 1
        status_text.text(f"Processing section {sections_processed_count}/{MAX_SECTIONS_TO_PROCESS}: {section_link}")
        progress = min(len(article_links_set) / URL_COLLECTION_TARGET, 1.0)
        progress_bar.progress(progress)

        try:
            section_page_text = fetch_page(section_link)
            section_soup = BeautifulSoup(section_page_text, 'html.parser')
            for a in section_soup.find_all('a', href=True):
                if len(article_links_set) >= URL_COLLECTION_TARGET:
                    break
                href = a['href']
                if href.startswith(('https://www.nytimes.com/20', '/20')) and \
                   not href.endswith(('.jpg', '.png', '/interactive/', '/video/', '.json', '.xml', '.rss')):
                    if href.startswith('/'):
                        href = 'https://www.nytimes.com' + href
                    if is_crawl_allowed(href):
                        article_links_set.add(href)
        except Exception as e:
            st.warning(f"Failed to scrape section {section_link}: {str(e)}")

    status_text.text(f"Collected {len(article_links_set)} article links.")

    candidate_article_links = list(article_links_set)
    for link_idx, link in enumerate(candidate_article_links):
        if saved_articles_count >= TARGET_ARTICLES_TO_SAVE:
            break
        status_text.text(f"Scraping article {link_idx + 1}/{len(candidate_article_links)}: {link}")
        progress = min((link_idx + 1) / len(candidate_article_links), 1.0)
        progress_bar.progress(progress)

        try:
            article_page_text = fetch_page(link)
            article_soup = BeautifulSoup(article_page_text, 'html.parser')
            paragraphs = article_soup.find_all('p', class_=re.compile('css-.*'))
            content = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            if not content:
                story_body = article_soup.find('section', attrs={'name': 'articleBody'})
                if story_body:
                    paragraphs = story_body.find_all('p')
                else:
                    paragraphs = article_soup.find_all('p')
                content = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            if not content:
                st.warning(f"No content extracted from {link}. Skipping.")
                continue

            file_content = f"URL: {link}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{content}"
            filename = f"article_{saved_articles_count + 1}.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            successfully_saved_files.append(filepath)
            saved_articles_count += 1
            st.success(f"Saved: {filename}")
        except Exception as e:
            st.warning(f"Failed to scrape {link}: {str(e)}")

    status_text.text(f"Saved {saved_articles_count} articles.")
    progress_bar.progress(1.0)
    return successfully_saved_files, candidate_article_links

# Updated API-based article fetching function
def fetch_articles_from_api(num_articles):
    API_ENDPOINT = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    successfully_saved_files = []
    saved_articles_count = 0
    page = 0
    articles = []
    MIN_CONTENT_WORDS = 20  # Minimum number of words to consider content valid

    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Starting API article fetching...")

    while len(articles) < num_articles:
        status_text.text(f"Fetching page {page + 1} from NYT API...")
        try:
            response = requests.get(
                API_ENDPOINT,
                params={'q': 'news', 'page': page, 'api-key': NYT_API_KEY}
            )
            response.raise_for_status()
            data = response.json()
            docs = data.get('response', {}).get('docs', [])
            if not docs:
                status_text.text("No more articles available from API.")
                break
            for doc in docs:
                if len(articles) >= num_articles:
                    break
                # Combine multiple fields for richer content
                headline = doc.get('headline', {}).get('main', '')
                snippet = doc.get('snippet', '')
                abstract = doc.get('abstract', '')
                lead_paragraph = doc.get('lead_paragraph', '')
                byline = doc.get('byline', {}).get('original', '')
                # Combine fields, avoiding duplicates
                content_parts = set()
                for part in [headline, snippet, abstract, lead_paragraph, byline]:
                    if part and part not in content_parts:
                        content_parts.add(part)
                content = ' '.join(content_parts).strip()
                # Validate content length
                word_count = len(word_tokenize(content))
                if not content or word_count < MIN_CONTENT_WORDS:
                    st.warning(f"Skipping article with insufficient content ({word_count} words): {doc.get('web_url', 'Unknown URL')}")
                    continue
                articles.append({
                    'url': doc.get('web_url', ''),
                    'content': content
                })
            page += 1
            progress = min(len(articles) / num_articles, 1.0)
            progress_bar.progress(progress)
            time.sleep(1)  # Respect API rate limits
        except requests.exceptions.HTTPError as e:
            st.error(f"API request failed: {str(e)}")
            if e.response.status_code == 401:
                st.error("Invalid API key. Please check the NYT_API_KEY constant in the code.")
            elif e.response.status_code == 429:
                st.error("API rate limit exceeded. Please wait and try again.")
            break
        except Exception as e:
            st.error(f"Unexpected error during API fetch: {str(e)}")
            break

    # Save articles to files
    for i, article in enumerate(articles):
        if saved_articles_count >= num_articles:
            break
        file_content = f"URL: {article['url']}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{article['content']}"
        filename = f"api_article_{saved_articles_count + 1}.txt"
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            successfully_saved_files.append(filepath)
            saved_articles_count += 1
            st.success(f"Saved: {filename}")
        except Exception as e:
            st.warning(f"Failed to save article {filename}: {str(e)}")

    status_text.text(f"Saved {saved_articles_count} articles via API.")
    progress_bar.progress(1.0)
    return successfully_saved_files

# Modified TF-IDF analysis and display with CSV generation
def analyze_and_display_tf_idf(successfully_saved_files):
    if not successfully_saved_files:
        st.error("No articles saved for TF-IDF analysis.")
        return

    documents_content_list = []
    file_urls = []
    for filepath in successfully_saved_files:
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()
                lines = content.splitlines()
                try:
                    url_line = next(line for line in lines if line.startswith('URL: '))
                    url = url_line.replace('URL: ', '').strip()
                    try:
                        first_newline_idx = content.index('\n')
                        second_newline_idx = content.index('\n', first_newline_idx + 1)
                        content_part = content[second_newline_idx+1:].strip()
                    except ValueError:
                        content_part = content
                    documents_content_list.append(content_part)
                    file_urls.append(url)
                except StopIteration:
                    st.warning(f"No URL found in {filepath}. Skipping.")
                    continue
        except Exception as e:
            st.warning(f"Error reading {filepath}: {str(e)}")
            continue

    if not documents_content_list:
        st.error("No content read for TF-IDF analysis.")
        return

    tf_idf_results = evaluate_tf_idf(documents_content_list)
    
    # Prepare CSV data
    csv_data = []
    st.subheader("TF-IDF Analysis Results")
    for i, tf_idf_score_map in enumerate(tf_idf_results):
        sorted_terms = sorted(tf_idf_score_map.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, score in sorted_terms[:4]]
        topic = " ".join(top_words).title()
        filename = os.path.basename(successfully_saved_files[i])
        article_content = documents_content_list[i].replace('\n', ' ')  # Replace newlines to avoid CSV formatting issues
        csv_data.append({
            'Article Data': article_content,
            'Article URL': file_urls[i] if i < len(file_urls) else 'Unknown',
            'Most Probable Topic': topic
        })
        
        with st.expander(f"Article: {filename}"):
            st.write(f"**Most Probable Topic**: {topic}")
            st.write(f"**URL**: {file_urls[i] if i < len(file_urls) else 'Unknown'}")
            st.write("**Top Words and Scores**:")
            st.table({word: round(score, 4) for word, score in sorted_terms[:4]})

    # Generate CSV
    if csv_data:
        df = pd.DataFrame(csv_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()
        
        # Display CSV as a table
        st.subheader("Generated CSV File")
        st.write("Below is the content of the generated CSV file containing article data, URLs, and topics:")
        st.dataframe(df)
        
        # Provide download button
        st.download_button(
            label="Download CSV",
            data=csv_content,
            file_name="nyt_articles_with_topics.csv",
            mime="text/csv"
        )
    else:
        st.error("No data available to generate CSV.")

# Streamlit UI
st.subheader("Web Scraping")
st.write("Click the button below to start scraping articles and analyzing their topics using TF-IDF.")
if st.button("Start Web Scraping"):
    with st.spinner("Scraping in progress..."):
        saved_files, article_links = scrape_nyt()
        if saved_files:
            analyze_and_display_tf_idf(saved_files)
        else:
            st.error("No articles were successfully saved.")

st.subheader("NYT API Fetching")
st.warning("Note: The NYT API provides article metadata (headline, abstract, lead paragraph) rather than full article text, which may result in less accurate TF-IDF analysis compared to web scraping. For full articles, consider requesting permission from NYT.")
st.write("Enter the number of articles to fetch, then click the button below to retrieve articles using the NYT API.")
api_num_articles = st.number_input("Number of articles to fetch via API", min_value=1, value=10, step=1)
if st.button("Start API Fetching"):
    with st.spinner("Fetching articles from NYT API..."):
        saved_files = fetch_articles_from_api(api_num_articles)
        if saved_files:
            analyze_and_display_tf_idf(saved_files)
        else:
            st.error("No articles were successfully fetched.")