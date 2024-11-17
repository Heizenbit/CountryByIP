from bs4 import BeautifulSoup
from models import session, CountryIP, CountryLink, CountryIPLog
from fetch_and_save_countries import request_page_with_selenium


# Function to extract the IP ranges from the page
def extract_ip_ranges(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')

    # Find all the table rows containing IP ranges (assuming they are in <tr> tags)
    rows = soup.find_all('tr')

    ip_ranges = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            ip_start = cells[0].text.strip()
            ip_end = cells[1].text.strip()

            ip_ranges.append(ip_start)
            ip_ranges.append(ip_end)

    return ip_ranges


def log_ip(country_obj, country_db_ips, updated_ips):
    # This function delete previous IPs of country that changes and logs the changes
    if country_db_ips:
        for country_ip in country_db_ips.values():
            session.delete(country_ip)
        session.commit()

        old_ip = ",".join([f"{k[0]}.{k[1]}" for k in country_db_ips.keys()])
        new_ip = ",".join([f"{ip[0]}.{ip[1]}" for ip in updated_ips])
        operation = 'Update'

        log_entry = CountryIPLog(
            country_name=country_obj.country, operation=operation, old_ip=old_ip, new_ip=new_ip
        )
        session.add(log_entry)
        session.commit()


def country_ip_process(response_text, country_obj):
    # Process and update country IPs
    country_db_ips = {(ip.x, ip.y): ip for ip in session.query(CountryIP).filter_by(country_id=country_obj.id).all()}
    ip_ranges = extract_ip_ranges(response_text)

    unique_ips = list(set([(ip.split('.')[0], ip.split('.')[1]) for ip in ip_ranges]))
    updated_ips = []

    for ip in unique_ips:
        if ip not in country_db_ips.keys():
            ip_obj = CountryIP(country_id=country_obj.id, x=ip[0], y=ip[1])
            session.add(ip_obj)
            session.commit()
            updated_ips.append((ip[0], ip[1]))

        else:
            # Remove from current IPs if it exists
            country_db_ips.pop(ip, None)

    # Log the IP changes
    log_ip(country_obj, country_db_ips, updated_ips)


def request_country_links():
    countries = country_from_db()
    failed_countries = []

    for country in countries:
        print(f'Start saving IPs of {country.country}.')
        url = 'https://lite.ip2location.com' + country.link

        # Fetch page content
        response_text = request_page_with_selenium(url)
        if response_text:
            try:
                country_ip_process(response_text, country)
                print(f'Successfully saved IPs of {country.country}.')
            except Exception as e:
                print(f"Error processing IPs for {country.country}: {e}")
                failed_countries.append(country)
        else:
            print(f"Failed to fetch data for {country.country}. Adding to retry list.")
            failed_countries.append(country)

    # Retry failed countries
    retry_failed_countries(failed_countries)


def retry_failed_countries(failed_countries):
    print("\nRetrying failed countries...")
    for country in failed_countries:
        url = 'https://lite.ip2location.com' + country.link
        response_text = request_page_with_selenium(url)
        if response_text:
            try:
                country_ip_process(response_text, country)
                print(f"Retry successful for {country.country}.")
            except Exception as e:
                print(f"Retry error for {country.country}: {e}")
        else:
            print(f"Retry failed for {country.country}.")


def country_from_db():
    country_links = session.query(CountryLink).all()

    return country_links
