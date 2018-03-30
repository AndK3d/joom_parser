import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    # look like '1509000350026007581-17-1-26193-3818161962'
    site_item_id = Column(String(80), nullable=False)


class ItemsSpecification(Base):
    __tablename__ = 'ItemsSpecification'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    category_id = Column(Integer)
    raiting = Column(String(10))
    #
    items = relationship(Items)



# class MenuItem(Base):
#     __tablename__ = 'menu_item'
#
#     name = Column(String(80), nullable=False)
#     id = Column(Integer, primary_key=True)
#     course = Column(String(250))
#     description = Column(String(250))
#     price = Column(String(8))
#     restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
#     restaurant = relationship(Restaurant)
#
#     @property
#     def serialize(self):
#         #
#         return {
#             'name': self.name,
#             'description': self.description,
#             'id': self.id,
#             'price': self.price,
#             'course': self.course,
#         }
### insert at end of file ###

engine = create_engine('sqlite:///joom.db') # echo=True
Base.metadata.create_all(engine)