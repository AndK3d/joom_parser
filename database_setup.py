import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    # look like '1509000350026007581-17-1-26193-3818161962'
    site_item_id = Column(String(80), nullable=False)
    category_id = Column(String(80))


class ItemsSpecification(Base):
    __tablename__ = 'ItemsSpecification'

    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'))
    category_id = Column(Integer)
    raiting = Column(String(10))
    #
    items = relationship(Items)


class Reviews(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    createdTimeMs = Column(Integer)
    updatedTimeMs = Column(Integer)
    review_id = Column(String(80),  nullable=False)
    product_id = Column(String(80))
    product_variant_id = Column(String(80))
    likesCount = Column(Integer)
    user_id = Column(String(80))
    user_fullName = Column(String(80))
    user_avatar = Column(String(255))
    text = Column(String(255))
    starRating = Column(String(10))


class ReviewsImages(Base):
    __tablename__ = 'reviews_images'

    id = Column(Integer, primary_key=True)
    review_id = Column(String(80),  nullable=False)
    url_pic_size0 = Column(String(255))
    url_pic_size1 = Column(String(255))
    url_pic_size2 = Column(String(255))
    url_pic_size3 = Column(String(255))
    url_pic_size4 = Column(String(255))


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    category_id = Column(String(80),  nullable=False)
    category_name = Column(String(255))
    hasPublicChildren = Column(Boolean)
    parent_id = Column(String(80))
    # main_image_mdpi = Column(String(255))
    # main_image_hdpi = Column(String(255))
    # main_image_xhdpi = Column(String(255))
    # main_image_xxhdpi = Column(String(255))
    # main_image_xxxhdpi = Column(String(255))



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