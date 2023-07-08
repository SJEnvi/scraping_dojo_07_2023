# json library will help save the results, os and dotenv will help extract initial settings from env file
import json
import os
from dotenv import load_dotenv

# importing playwright for handling web communication, bs4 for searching through website's html code
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


# Definition of Scraper class
class Scraper:
    # Definition of default variables, the values are extracted from env file
    def __init__(self):
        self.quotes_url = os.getenv('INPUT_URL')
        self.output_file = os.getenv('OUTPUT_FILE')
        self.proxy_server = os.getenv("PROXY_SERVER")

    # Logic of scrapping process
    def scrape(self):
        # Starting browser with playwright, then adding proxy settings to the session
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(proxy=self.proxy_server)
            page = context.new_page()
            # Opening first page the scraper will scrap
            page.goto(self.quotes_url)

            # Loop which will execute until there will be no more pages with quotes
            while True:
                # As there is delay in JS, we are waiting for the quote elements to load before proceeding
                page.wait_for_selector('div.quote')
                html = page.inner_html('#quotesPlaceholder')
                # Parsing a part of websites html with bs4
                soup = BeautifulSoup(html, 'html.parser')
                quotes = soup.find_all('div', class_='quote')
                with open(self.output_file, 'a') as f:
                    # taping into each quote to find relevant data
                    for quote in quotes:
                        spans = quote.find_all('span')
                        text = spans[0].text
                        author = spans[1].small.text
                        tags = [tag.text for tag in quote.find_all('a')]
                        # saving in key-values pairs
                        data = {'text': text, 'by': author, 'tags': tags}
                        # and saving each quote to json file
                        json.dump(data, f, indent=4)
                        f.write('\n')

                # Checking if there is a next page
                next_button = page.query_selector('li.next a')
                if not next_button:
                    break

                # Getting the URL to the next page
                next_url = "http://quotes.toscrape.com"+next_button.get_attribute('href')

                # Moving on to the next page, then the loop repeats
                page.goto(next_url)
            # Closing the file when loop is finished
            f.close()


if __name__ == '__main__':
    # loading dotenv to extract settings from env file, then creating Scraper object and running scrape method
    load_dotenv()
    scraper = Scraper()
    scraper.scrape()

