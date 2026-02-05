from app.api.db_models import *
import json


def fill_db_1():
    """

    :return:
    """
    with open('../data/takeoff_full.json', "r",encoding='utf-8') as f:
        data = json.load(f)

    for dic in data:
        country = Country.query.filter_by(country_name=dic['country']).first()
        if not country:
            country = Country(country_name = dic['country'],
                              country_code = dic['country_code'])
            db.session.add(country)
            db.session.flush()

        city = City.query.filter_by(city_name=dic['city']).first()
        if not city and dic['city']:
            city = City(city_name = dic['city'],
                        city_postal_code = dic['postal_code'])
            db.session.add(city)
            db.session.flush()

        street = Street.query.filter_by(street_name=dic['street']).first()
        if not street and dic['street']:
            street = Street(street_name = dic['street'])
            db.session.add(street)
            db.session.flush()

        address = Address(address_street_id = street.street_id if street else None,
                          address_city_id= city.city_id,
                          address_country_id = country.country_id)

        db.session.add(address)
        db.session.flush()

        takeoff = Takeoff(takeoff_name=dic['Name'],
                          takeoff_latitude=dic['Latitude'],
                          takeoff_longitude=dic['Longitude'],
                          takeoff_type=dic['Type'],
                          takeoff_address_id=address.address_id
                          )
        db.session.add(takeoff)

    db.session.commit()

with app.app_context():
    db.create_all()
    fill_db_1()
