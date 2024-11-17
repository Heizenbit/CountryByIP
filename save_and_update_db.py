from fetch_and_save_IPs import request_country_links
from fetch_and_save_countries import catch_country_links


def save_and_update_db():
    # update country links in database
    catch_country_links()

    # # request and save IPs in database by link of each country
    request_country_links()


save_and_update_db()
