# News Aggregator & Analyzer Application

This is a Flask-based web application designed to scrape, summarize, and analyze news articles. Users can input a URL to retrieve the main content, extract and analyze text, summarize articles, and fetch the latest headlines from major news websites.

---

## Features

### 1. **News Article Analysis**
- Extracts the main content from a provided URL using `newspaper3k`.
- Summarizes the article and performs text analysis:
  - Counts sentences and words.
  - Identifies parts of speech (POS) using `nltk`.
- Displays article details including title, publication date, authors, and main image.

### 2. **Headline Scraping**
- Fetches the latest headlines and links from popular news sites:
  - **The Hindu**
  - **BBC News**
  - **India Today**
  - **Times of India**
  - **Indian Express**

### 3. **Data Persistence**
- Stores URL, article text, and analysis summary in a PostgreSQL database.
- Provides a "History" page to view previously analyzed articles.

### 4. **GitHub OAuth Login**
- Users can log in using their GitHub accounts.
- Session-based authentication.

### 5. **Web Scraping**
- Retrieves the largest image or main image from articles based on dimensions.
- Extracts headlines and URLs from supported news websites.

---

## Prerequisites

### 1. **Python Dependencies**
Install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

Dependencies include:
- Flask
- requests
- BeautifulSoup4
- psycopg2
- newspaper3k
- nltk
- authlib

### 2. **Database Setup**
- PostgreSQL is used for data storage.
- Create a database with the following details:
  - **Database Name:** `news_data`
  - **User:** `news_data_user`
  - **Password:** `_______`
  - **Host:** `_________`
  - **Port:** `5432`

Execute the following SQL to create the required table:

```sql
CREATE TABLE IF NOT EXISTS news_data (
    id SERIAL PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    summary TEXT
);
```

---

## File Structure

- **`app.py`**: Main application logic.
- **Templates**:
  - **`index.html`**: Homepage with form for inputting URLs and selecting news sources.
  - **`history.html`**: Displays stored article data.
  - **`iframe.html`**: Renders content within an iframe.

---

## Environment Configuration

1. **GitHub OAuth Setup**
   - Register the application on GitHub and set the following environment variables:
     - `GITHUB_CLIENT_ID`
     - `GITHUB_CLIENT_SECRET`
   - Update `authorize_url` and `access_token_url` in `app.py` as needed.

2. **Flask App**
   - Set the secret key in `app.secret_key` and `app.config['SECRET_KEY']`.

---

## How to Run the Application

1. Clone the repository.
2. Install dependencies with `pip install -r requirements.txt`.
3. Set up the PostgreSQL database and table.
4. Run the Flask app:

   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://127.0.0.1:5000`.

---

## Usage

1. **Analyze Article by URL**:
   - Paste the article's URL in the input field and submit.
   - View the extracted content, image, and summary.

2. **Fetch Latest News**:
   - Select a news source from the dropdown and click submit.
   - See the latest headlines with links.

3. **View Analysis History**:
   - Access previously analyzed articles via the "History" page.

---

## Notes

- Ensure network access to scrape external websites.
- Configure GitHub OAuth correctly for user login functionality.
- Update database credentials and connection details as per your setup.

---

## License

This project is licensed under the MIT License.
