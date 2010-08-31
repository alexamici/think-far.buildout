
from google.appengine.ext.db import Model, FloatProperty, StringProperty, BooleanProperty
from google.appengine.ext.db import TextProperty, DateProperty
from google.appengine.ext.db import UserProperty, ReferenceProperty, SelfReferenceProperty


class Portfolio(Model):
    owner = UserProperty(required=True)
    name = StringProperty(required=True, default=u'Default Portfolio')

    def __repr__(self):
        return u'<%s object name=%r owner=%r>' % \
            (self.__class__.__name__, self.name, self.owner.nickname())

class Account(Model):
    name = StringProperty(required=True)
    group_under = SelfReferenceProperty()
    order_number = FloatProperty()

class AssetModel(Model):
    name = StringProperty(required=True)
    description = StringProperty()
    long_description = TextProperty()

    def __repr__(self):
        return u'<%s object name=%r description=%r>' % \
            (self.__class__.__name__, self.name, self.description)

class Asset(Model):
    """Base asset class"""
    portfolio = ReferenceProperty(Portfolio, required=True, collection_name='assets')
    asset_model = ReferenceProperty(AssetModel, required=True)
    name = StringProperty(required=True)
    identity = StringProperty()
    long_identity = TextProperty()

    @property
    def has_identity(self):
        return self.identity is not None

    def __repr__(self):
        if self.has_identity:
            identification = u'identity=%r' % self.identity
        else:
            identification = u''
        return u'<%s object name=%r %s portfolio=%r owner=%r>' % \
            (self.__class__.__name__, self.name, identification,
                self.portfolio.name, self.portfolio.owner.nickname())

class Trade(Model):
    """Asset trade"""
    trade_asset = ReferenceProperty(Asset, required=True, collection_name='trades')
    trade_ammount = FloatProperty(required=True)
    trade_date = DateProperty(required=True)
    trade_price = FloatProperty(required=True)
    trade_cost = FloatProperty(default=0.)

class EstimatedValue(Model):
    """Estimated value including ask/bid spread"""
    estimated_value_date = DateProperty()
    estimated_value_ask = FloatProperty()
    estimated_value_bid = FloatProperty()

class Liability(Model):
    owner = UserProperty()
    name = StringProperty(required=True)
    group_under = SelfReferenceProperty()
    outstanding_debt = FloatProperty()
    market_price = FloatProperty()

    def __repr__(self):
        return u'<%s object name="%s" owner="%s">' % \
            (self.__class__.__name__, self.name, self.owner.nickname())
