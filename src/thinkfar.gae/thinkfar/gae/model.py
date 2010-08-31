
from google.appengine.ext import db


class Portfolio(db.Model):
    owner = db.UserProperty() # required=True)
    name = db.StringProperty(required=True)

    def __repr__(self):
        return u'<%s object name="%s" owner="%s">' % \
            (self.__class__.__name__, self.name, self.owner)

class Account(db.Model):
    name = db.StringProperty(required=True)
    group_under = db.SelfReferenceProperty()
    order_number = db.FloatProperty()

class Asset(db.Model):
    """Base asset class"""
    owner = db.UserProperty(required=True)
    name = db.StringProperty(required=True)
    purcase_price = db.FloatProperty()
    purcase_date = db.DateProperty()
    sell_price = db.FloatProperty()
    sell_date = db.DateProperty()

    def __repr__(self):
        return u'<%s object name="%s" owner="%s">' % \
            (self.__class__.__name__, self.name, self.owner)

class EstimatedValue(db.Model):
    """Estimated value including ask/bid spread"""
    estimated_value_date = db.DateProperty()
    estimated_value_ask = db.FloatProperty()
    estimated_value_bid = db.FloatProperty()

class Liability(db.Model):
    owner = db.UserProperty()
    name = db.StringProperty(required=True)
    group_under = db.SelfReferenceProperty()
    outstanding_debt = db.FloatProperty()
    market_price = db.FloatProperty()

    def __repr__(self):
        return u'<%s object name="%s" owner="%s">' % \
            (self.__class__.__name__, self.name, self.owner)
