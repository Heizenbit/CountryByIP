from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from models import CountryLink, session


def request_page_with_selenium(url="https://lite.ip2location.com/ip-address-ranges-by-country"):
    print(f"Fetching the page: {url}")

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--proxy-server=socks5://localhost:9996')

    # Initialize Selenium WebDriver
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)

        # Wait for content to load
        WebDriverWait(driver, 15).until(
            ec.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Extract HTML
        page_html = driver.page_source
        driver.quit()
        print("Page fetched successfully!")
        return page_html

    except WebDriverException as e:
        print(f"Selenium Error: {e}")
        return None


def catch_country_links():
    print('Catching country links...')
    response_text = request_page_with_selenium()

    if not response_text:
        print("Failed to fetch page content.")

    soup = BeautifulSoup(response_text, 'html.parser')
    cards = soup.find_all('div', class_='card')

    for card in cards:
        try:
            country_name = card.find('a').text.strip()
            country_link = card.find('a')['href']

            CountryLink.add(session, country_name=country_name, country_link=country_link)

        except AttributeError as e:
            print(f"Error parsing card: {e}")


catch_country_links()
