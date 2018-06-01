from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Vineyard, Sensor, Magnitude, Metric

def setup(email='admin@example.com', count=100):
    fake = Faker()
    u = User(email = email,
            password = 'password',
            confirmed = True,
            name = fake.name())
    db.session.add(u)
    db.session.commit()

    v = Vineyard(name = fake.name(),
            user_id = u.id)
    db.session.add(v)
    db.session.commit()

    s = Sensor(description = fake.sentence(nb_words=6, variable_nb_words=True),
            latitude=0,
            longitude=0,
            gateway = fake.sentence(nb_words=3, variable_nb_words=True),
            power_perc = 100,
            vineyard_id = v.id,
            user_id = u.id)
    db.session.add(s)
    db.session.commit()

    temp = Magnitude(layer='Surface',
            type='Temperature',
            sensor_id = s.id,
            user_id = u.id)
    db.session.add(temp)
    db.session.commit()

    hum = Magnitude(layer='Surface',
            type='Humidity',
            sensor_id = s.id,
            user_id = u.id)
    db.session.add(hum)
    db.session.commit()

    i = 0
    while i < count:
        m1 = Metric(timestamp=fake.date_time_this_month(),
                value=fake.pyfloat(left_digits=2, right_digits=3, positive=True),
                magnitude_id=temp.id)
        db.session.add(m1)
        m2 = Metric(timestamp=fake.date_time_this_month(),
                value=fake.pyfloat(left_digits=2, right_digits=3, positive=True),
                magnitude_id=hum.id)
        db.session.add(m2)

        try:
            db.session.commit()
            i += 1
        except IntegrityError as e:
            db.session.rollback()
            return


def generateFakeMetricsForMagnitude(magnitude_id, count=100):
    fake = Faker()
    i = 0
    while i < count:
        m = Metric(timestamp=fake.date_time_this_month(),
                value=fake.pyfloat(left_digits=2, right_digits=3, positive=True),
                magnitude_id=magnitude_id)
        db.session.add(m)

        db.session.commit()
        i += 1


