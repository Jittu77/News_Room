from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import re
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
import psycopg2
from newspaper import Article
from urllib.parse import urljoin
from nltk.corpus import stopwords
from authlib.integrations.flask_client import OAuth
from urllib.error import HTTPError


app = Flask(__name__)
app.secret_key = 'prayarth'  # Set a secret key for flashing messages

oauth = OAuth(app)

# github requirements

app.config['SECRET_KEY'] = "Prayarth"
app.config['GITHUB_CLIENT_ID'] = "1cf0eb8e8fe5e8c4fded"
app.config['GITHUB_CLIENT_SECRET'] = "cda97cce384677d43d3a2db689d895c845f30fcc"

github = oauth.register(
    name='github',
    client_id=app.config["GITHUB_CLIENT_ID"],
    client_secret=app.config["GITHUB_CLIENT_SECRET"],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Github login route
@app.route('/login/github')
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)

# Github authorize route
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    session['github_token'] = token
    resp = github.get('user').json()
    print(f"\n{resp}\n")
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM news_data")
    data = cursor.fetchall()

    connection.close()

    return render_template('history.html', data=data)
    # Redirect to a template or another route after successful authorization

# Logout route for GitHub
@app.route('/logout/github')
def github_logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))


# Function to analyze text
def analyze_text(text):
    num_sentences = len(sent_tokenize(text))
    words = word_tokenize(text)
    num_words = len(words)
    pos_tags = pos_tag(words)
    # Other relevant analysis can be added here
    
    return num_sentences, num_words, pos_tags

# Function to connect to PostgreSQL database
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="news_data",
            user="news_data_user",
            password="sXcoxhccPPon1HLU6L2MaYLYGvUxmL9T",
            host="dpg-cnm8730cmk4c73agff4g-a",
            port="5432",
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    
    # SQL query to create the 'news_data' table
    
    
    cursor.execute( "CREATE TABLE IF NOT EXISTS news_data (id SERIAL PRIMARY KEY,url VARCHAR(255) NOT NULL,text TEXT NOT NULL,summary TEXT)")
    conn.commit()
    conn.close()


import requests
from bs4 import BeautifulSoup

# extracting main image from the hindus news website on basis of its highest dimension

def get_largest_image(url):
    agent = {"User-Agent": "Mozilla/5.0"}
    source = requests.get(url, headers=agent)
    soup = BeautifulSoup(source.content, "html.parser")

    # Find all 'source' and 'img' tags within the 'picture' tag
    source_tags = soup.select('picture source')
    img_tag = soup.select('picture img')

    # Extract image links from 'source' tags
    image_links = [source['srcset'] for source in source_tags]

    # Extract image link from 'img' tag
    img_link = img_tag[0]['src']

    # Combine all image links (including the one from 'img' tag)
    all_image_links = image_links + [img_link]

    # Find the image with the largest area
    largest_image = max(all_image_links, key=lambda link: get_image_area(link))

    return largest_image

def get_image_area(image_link):
    # Extract width and height from the image link
    parts = image_link.split(' ')
    if len(parts) >= 2:
        size = parts[1].split('x')
        if len(size) == 2:
            width = int(size[0])
            height = int(size[1])
            return width * height
    return 0  # Return 0 if unable to extract dimensions

# extracting main image from news website (eg: india today, aaj tak, india exppress and etc) on basis of its highest dimension

def extract_main_image(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all image tags on the page
        img_tags = soup.find_all('img')
        
        # Filter images based on size, alt text, CSS classes, etc. to identify the main image
        main_image = None
        max_area = 0
        for img in img_tags:
            src = img.get('src')
            if src:
                # Handle relative URLs
                src = urljoin(url, src)
                
                # Get the image dimensions
                width = img.get('width')
                height = img.get('height')
                area = 0
                if width and height:
                    area = int(width) * int(height)
                
                # Additional filtering criteria can be added here
                
                # Update main image if current image has a larger area
                if area > max_area:
                    main_image = src
                    max_area = area
        
        return main_image
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# scraping latest headlines and Url from India today
def scrape_links_from_india_today(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    main = soup.find_all('h2', class_="")
    scrap_links_hindu = []

    for article in main:
        link = "https://www.indiatoday.in"+article.find('a')['href']
        title = article.find('a').text.replace('\n', '')
        scrap_links_hindu.append((title,link))

    return scrap_links_hindu

# scraping latest headlines and Url from India today

def scrape_links_from_the_hindu(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    main = soup.find_all('h3', class_="title big")
    scrap_links_hindu = []

    for article in main:
        link = article.find('a')['href']
        title = article.find('a').text.replace('\n', '')
        scrap_links_hindu.append((title,link))

    return scrap_links_hindu

# scraping latest headlines and Url from India today

def scrape_links_from_the_bbc_news(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    links_and_headlines = []
    for link in soup.find_all('a', class_='ssrcss-9haqql-LinkPostLink'):
        href = "https://www.bbc.com/"+link.get('href')
        headline = link.find('span', class_='ssrcss-1fq6dkj-LinkPostHeadline').text
        links_and_headlines.append((headline,href))

    return links_and_headlines

# scraping latest headlines and Url from times of India

def scrape_links_from_toi(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    links_info = []

    # Extract links and titles
    for link in soup.find_all('a', href=True)[-17:-1]:
        # links_info.append(link.get("href"))
        links_info.append((link.get_text(strip=True),link.get("href")))
        # links_info[link_title]=link_url

    return links_info


# Function to store URL, news text, and analysis summary in PostgreSQL
def store_data(url, text, summary):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO news_data (url, text, summary) VALUES (%s, %s, %s)", (url, text, summary))
            conn.commit()
            flash("Data stored successfully!", "success")
        except psycopg2.Error as e:
            conn.rollback()
            print("Error storing data:", e)
            flash("Failed to store data in the database!", "error")
        finally:
            conn.close()

# Function to retrieve stored data from PostgreSQL
def retrieve_data():
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM news_data")
            data = cursor.fetchall()
            return data
        except psycopg2.Error as e:
            print("Error retrieving data:", e)
        finally:
            conn.close()
    return []

# Route for home page
@app.route('/')
def index():    
    return render_template('index.html')

# Route for submitting URL
@app.route('/submit', methods=['POST'])
def submit():

    # url = request.form['url']
    if request.form['submit'] == "url":
        url = request.form['url']
        if not url.startswith(('http://', 'https://')):
            flash("Invalid URL! Please enter a valid URL starting with http:// or https://", "error")
            return redirect(url_for('index'))
        
        try:
            # response = requests.get(url)
            # response.raise_for_status()  # Raise an error for invalid HTTP response
            # soup = BeautifulSoup(response.text, 'html.parser')
            # news_text = soup.get_text()
            # cleaned_text = clean_text(news_text)
            # num_sentences, num_words, pos_tags = analyze_text(cleaned_text)
            article = Article(url)
            article.download()
            article.parse()
            # y=article.text
            num_sentences, num_words, pos_tags = analyze_text(article.text)

            
            article.nlp()
            word_list1 =nltk.word_tokenize(article.text)
            words_pos=nltk.pos_tag(word_list1, tagset="universal")

            pos=[]
            numbers=[]
            summary_main={}

            for i in words_pos: 
                if i[1] not in pos:
                    pos.append(i[1])
            count=1
            for i in range(len(pos)):
                for j in words_pos:
                    if j[1]==pos[i]:
                        count+=1
                numbers.append(count)
                summary_main[pos[i]]=count


            summary = {
                'num_sentences': num_sentences,
                'num_words': num_words,
                'pos_tags': summary_main
            }


            create_table()
            # store_data(url, article.text, str(summary))
        except requests.RequestException as e:
            flash(f"Failed to fetch data from URL: {e}", "error")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")

        # extracting Image url and storing in image_url
        main_image_url = extract_main_image(url)
        try:
            if url.startswith(('https://www.thehindu.com')) and get_largest_image(url):
                main_image_url = get_largest_image(url)
                
            if extract_main_image(url):
                main_image_url = extract_main_image(url)
        except:
            main_image_url=None
                    
        if article.authors:
            author=article.authors
        else:
            author=None

        return render_template('index.html', image_url=main_image_url, article_text=article.text,content12=["Author", "Publish date", "Num_Sentences", " Num_Words" ], sum="Summary of Article",page= "More About The page", article_summary= article.summary)
        # return redirect(url_for('index')) 
    elif request.form['submit'] == "news_website":
        selected_option = None        
        selected_option = request.form.get('news_website')

        try:
            headers=["Title of News","URL of News", "Copy URL"]

            if selected_option == 'The Hindu':
                url = "https://www.thehindu.com/news/national/"
                latest_headlines = scrape_links_from_the_hindu(url)
                
                return render_template('index.html', latest_headlines=latest_headlines,headers=headers)

            elif selected_option == 'BBC':
                url = "https://www.bbc.com/news/world/asia"
                latest_headlines=scrape_links_from_the_bbc_news(url)
                return render_template('index.html', latest_headlines=latest_headlines,headers=headers)

            elif selected_option == 'India Today':
                url = "https://www.indiatoday.in/india"
                latest_headlines=scrape_links_from_india_today(url)
                
                return render_template('index.html', latest_headlines=latest_headlines,headers=headers)

            elif selected_option == 'Times Of India':
                url_to_scrape = "https://timesofindia.indiatimes.com/"
                latest_headlines=scrape_links_from_toi(url_to_scrape)
                return render_template('index.html', latest_headlines=latest_headlines,headers=headers)

            else:
                url_to_scrape = "https://timesofindia.indiatimes.com/"
                latest_headlines=scrape_links_from_toi(url_to_scrape)
                return render_template('index.html', latest_headlines=latest_headlines,headers=headers)
        except:
            return render_template('index.html')
            
    else:
        return render_template('index.html')

@app.route('/history')
def history():
    data = retrieve_data()
    return render_template('history.html', data=data)

@app.route('/iframe')
def iframe():
    return render_template('iframe.html')

if __name__ == '__main__':
    app.run(debug=True)
