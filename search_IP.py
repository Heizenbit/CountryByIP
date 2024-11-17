from models import CountryIP, Session


def give_country_by_ip(x, y):
    session = Session()
    countries = session.query(CountryIP).filter_by(x=x, y=y).all()

    if countries:
        for country in countries:
            print(country.country_link.country)


give_country_by_ip(80, 65)
