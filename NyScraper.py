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

# Define the URL for The New York Times homepage
NYT_URL = "https://www.nytimes.com/"

# Headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Create the text_files directory if it doesn't exist
output_dir = "text_files"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Function to fetch a page with retries and exponential backoff
def fetch_page(url, max_retries=5, delay_base=2):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15) # Increased timeout
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e: # Catch specific request exceptions
            print(f"Attempt {attempt+1}/{max_retries} failed for {url}: {str(e)}")
            if attempt < max_retries - 1:
                delay = delay_base * (2 ** attempt) # Exponential backoff
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} after {max_retries} attempts.")
                raise # Re-raise the exception to be caught by the caller
        except Exception as e: # Catch other unexpected errors during fetch
            print(f"An unexpected error occurred during fetch attempt {attempt+1} for {url}: {str(e)}")
            if attempt < max_retries - 1:
                delay = delay_base * (2 ** attempt)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to fetch {url} due to unexpected error after {max_retries} attempts.")
                raise


# --- Game Plan ---
TARGET_ARTICLES_TO_SAVE = 100
URL_COLLECTION_TARGET = TARGET_ARTICLES_TO_SAVE + 50 
MAX_SECTIONS_TO_PROCESS = 35 # Safety limit for processing sections

article_links_set = set()
section_links_to_visit = []
processed_section_links = set()

print(f"Starting article link collection. Target: {URL_COLLECTION_TARGET} unique URLs.")

# Scrape the homepage for initial article and section links
try:
    print(f"Fetching homepage: {NYT_URL}")
    home_page_text = fetch_page(NYT_URL)
    soup = BeautifulSoup(home_page_text, 'html.parser')

    # Find initial article links from homepage
    for a in soup.find_all('a', href=True):
        if len(article_links_set) >= URL_COLLECTION_TARGET:
            break
        href = a['href']
        if href.startswith(('https://www.nytimes.com/20', '/20')) and \
           not href.endswith(('.jpg', '.png', '/interactive/', '/video/', '.json', '.xml', '.rss')): # Added more exclusions
            if href.startswith('/'):
                href = 'https://www.nytimes.com' + href
            if href not in article_links_set: # Check before adding
                article_links_set.add(href)

    # Find section links from homepage
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith(('/section/', 'https://www.nytimes.com/section/')):
            if href.startswith('/'):
                href = 'https://www.nytimes.com' + href
            if href not in processed_section_links and href not in section_links_to_visit:
                section_links_to_visit.append(href)
    print(f"Found {len(section_links_to_visit)} initial sections to explore from homepage.")

except Exception as e:
    print(f"Failed to scrape homepage or extract initial links: {str(e)}")
    if not section_links_to_visit and len(article_links_set) < TARGET_ARTICLES_TO_SAVE:
        print("Critical error: No sections to visit and not enough articles from homepage. Exiting.")
        exit(1)


# Scrape section pages until we have enough unique article links or run out of sections
sections_processed_count = 0
while len(article_links_set) < URL_COLLECTION_TARGET and section_links_to_visit and sections_processed_count < MAX_SECTIONS_TO_PROCESS:
    section_link = section_links_to_visit.pop(0)
    if section_link in processed_section_links:
        continue
    
    processed_section_links.add(section_link)
    sections_processed_count += 1
    
    print(f"Processing section ({sections_processed_count}/{MAX_SECTIONS_TO_PROCESS}): {section_link}. Articles found: {len(article_links_set)}/{URL_COLLECTION_TARGET}")

    try:
        section_page_text = fetch_page(section_link)
        section_soup = BeautifulSoup(section_page_text, 'html.parser')
        
        new_links_from_section = 0
        for a in section_soup.find_all('a', href=True):
            if len(article_links_set) >= URL_COLLECTION_TARGET:
                break
            href = a['href']
            if href.startswith(('https://www.nytimes.com/20', '/20')) and \
               not href.endswith(('.jpg', '.png', '/interactive/', '/video/', '.json', '.xml', '.rss')):
                if href.startswith('/'):
                    href = 'https://www.nytimes.com' + href
                
                if href not in article_links_set:
                    article_links_set.add(href)
                    new_links_from_section +=1

        print(f"Found {new_links_from_section} new articles from {section_link}.")

    except Exception as e:
        print(f"Failed to scrape or process section {section_link}: {str(e)}")

if len(article_links_set) < TARGET_ARTICLES_TO_SAVE:
    print(f"Warning: Collected only {len(article_links_set)} unique articles. Target was {TARGET_ARTICLES_TO_SAVE} (with buffer up to {URL_COLLECTION_TARGET}). May not be able to save {TARGET_ARTICLES_TO_SAVE} files.")
elif len(article_links_set) < URL_COLLECTION_TARGET:
    print(f"Collected {len(article_links_set)} unique articles (target was {URL_COLLECTION_TARGET} with buffer). Proceeding to download.")
else:
    print(f"Successfully collected {len(article_links_set)} unique article links (target {URL_COLLECTION_TARGET} met or exceeded).")

candidate_article_links = list(article_links_set)

# --- Scrape and Save Articles ---
saved_articles_count = 0
successfully_saved_files = [] # For TF-IDF input

print(f"\nStarting to scrape and save articles. Target: {TARGET_ARTICLES_TO_SAVE} files.")
for link_idx, link in enumerate(candidate_article_links):
    if saved_articles_count >= TARGET_ARTICLES_TO_SAVE:
        print(f"Reached target of {TARGET_ARTICLES_TO_SAVE} saved articles. Stopping download process.")
        break

    print(f"Attempting to scrape article {link_idx + 1}/{len(candidate_article_links)} (saved so far: {saved_articles_count}): {link}")
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
            print(f"Warning: No content extracted from article {link}. Skipping.")
            continue

        file_content = f"URL: {link}\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{content}"
        filename = f"article_{saved_articles_count + 1}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Successfully saved: {filename}")
        successfully_saved_files.append(filepath)
        saved_articles_count += 1

    except Exception as e:
        print(f"Failed to scrape or save article {link}: {str(e)}")

print(f"\nScraping and saving complete.")
print(f"Total articles successfully saved: {saved_articles_count} in '{output_dir}' directory.")

if saved_articles_count < TARGET_ARTICLES_TO_SAVE:
    print(f"Warning: Saved {saved_articles_count} files, but the target was {TARGET_ARTICLES_TO_SAVE}.")

# --- NLTK and TF-IDF Analysis ---
try:
    try:
        stopwords.words('english')
        word_tokenize("test")
        WordNetLemmatizer().lemmatize("test")
        print("NLTK resources are already ready.")
    except LookupError:
        print("Downloading NLTK resources (stopwords, punkt, wordnet)...")
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        nltk.download("wordnet", quiet=True)
        print("NLTK resources downloaded successfully!\n")
    print('-'*40)
except Exception as e:
    print(f"Failed to download or verify NLTK resources: {str(e)}")

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
    for doc_idx, document_content in enumerate(documents_list):
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

documents_content_list = []

if not successfully_saved_files:
    print("No articles were successfully saved. Skipping TF-IDF analysis.")
else:
    print(f"\nStarting TF-IDF analysis for {len(successfully_saved_files)} saved articles...")
    for filepath in successfully_saved_files:
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()
                try:
                    first_newline_idx = ''.join(lines).index('\n')
                    second_newline_idx = ''.join(lines).index('\n', first_newline_idx + 1)
                    content_part = ''.join(lines)[second_newline_idx+1:]
                except ValueError:
                    print(f"Warning: Could not parse header for content in {filepath}. Using full content.")
                    content_part = ''.join(lines)

                documents_content_list.append(content_part.strip())
        except Exception as e:
            print(f"Error reading file {filepath} for TF-IDF: {str(e)}")

    if not documents_content_list:
        print("No content could be read from saved files for TF-IDF analysis.")
    else:
        tf_idf_results = evaluate_tf_idf(documents_content_list)
        print("\n--- TF-IDF Results ---")
        for i, tf_idf_score_map in enumerate(tf_idf_results):
            sorted_terms = sorted(tf_idf_score_map.items(), key=lambda x: x[1], reverse=True)
            top_words = [word for word, score in sorted_terms[:4]]
            topic = " ".join(top_words).title()
            current_filename = os.path.basename(successfully_saved_files[i])
            print(f"File: {current_filename}\nMost Probable Topic: {topic}\n{'-'*40}")

print("\nScript finished.")

