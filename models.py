from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class CountryLink(Base):
    __tablename__ = 'country_links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String, nullable=False)
    link = Column(String, nullable=False)

    country_ips = relationship('CountryIP', back_populates='country_link')

    @staticmethod
    def add(session, country_name, country_link):
        country_obj = session.query(CountryLink).filter_by(country=country_name).first()

        if not country_obj:
            country_obj = CountryLink(country=country_name, link=country_link)
            session.add(country_obj)
            session.commit()

            CountryLinkLog.add(session=session, country_link_id=country_obj.id, operation='Add')

        elif country_obj and country_obj.link != country_link:

            CountryLink.update(session, country_link_id=country_obj.id, link=country_link)

    @staticmethod
    def update(session, country_link_id, link):
        country_obj = session.query(CountryLink).filter_by(id=country_link_id).first()

        if country_obj:
            old_link = country_obj.link
            country_obj.link = link
            session.commit()
            CountryLinkLog.add(session=session, country_link_id=country_obj.id, operation='Update',
                               old_link=old_link, new_link=country_obj.link)


class CountryIP(Base):
    __tablename__ = 'country_ips'

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey('country_links.id'), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)

    country_link = relationship('CountryLink', back_populates='country_ips')

    @staticmethod
    def add(session, country_id, x, y):
        ip_obj = session.query(CountryIP).filter_by(country_id=country_id, x=x, y=y).first()

        if not ip_obj:
            ip_obj = CountryIP(country_id=country_id, x=x, y=y)
            session.add(ip_obj)
            session.commit()



class CountryLinkLog(Base):
    __tablename__ = 'country_link_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_link_id = Column(String, ForeignKey('country_links.id'), nullable=False)
    operation = Column(String, nullable=False)
    old_link = Column(String, nullable=False)
    new_link = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=False), default=func.now())

    @staticmethod
    def add(session, country_link_id, operation, old_link='', new_link=''):
        country_link_obj = session.query(CountryLink).filter_by(id=country_link_id).first()

        if country_link_obj:
            log_obj = CountryLinkLog(country_link_id=country_link_id, operation=operation, old_link=old_link,
                                     new_link=new_link)
            session.add(log_obj)
            session.commit()


class CountryIPLog(Base):
    __tablename__ = 'country_ip_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_name = Column(String, nullable=False)
    operation = Column(String, nullable=False)
    old_link = Column(String, nullable=False)
    new_link = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=False), default=func.now())





engine = create_engine('sqlite:///database.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
