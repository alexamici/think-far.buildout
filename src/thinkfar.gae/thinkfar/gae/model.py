
from google.appengine.ext import db


class Account(db.Model):
    name = db.StringProperty(required=True)
    parent = SelfReferenceProperty()
    order_number = db.FloatProperty()

class Asset(db.Model):
    owner = db.UserProperty(required=True)
    name = db.StringProperty(required=True)
    purcase_price = db.FloatProperty()
    purcase_date = db.DateProperty()
    sell_price = db.FloatProperty()
    sell_date = db.DateProperty()

class AssetValues(db.model):
    estimated_market_ask = db.FloatProperty()
    estimated_market_bid = db.FloatProperty()

class Liability(db.Model):
    name = db.StringProperty(required=True)
    parent = SelfReferenceProperty()
    outstanding_debt = db.FloatProperty()
    market_price = db.FloatProperty()
    owner = db.UserProperty()


assets = db.GqlQuery("SELECT * FROM Asset WHERE owner = :owner", 'ale')
liabilities = db.GqlQuery("SELECT * FROM Liability WHERE owner = :owner", 'ale')

assets_market_total = sum(a.market_price for a in assets)
assets_repurcase_total = sum(a.repurcase_price for a in assets)
liabilities_outstanding_total = sum(l.outstanding_debt for l in liabilities)

print assets_market_total - liabilities_outstanding_total
