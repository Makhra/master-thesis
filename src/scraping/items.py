# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
from scrapy.contrib.djangoitem import DjangoItem
from stamps.models import Stamp, StampInCatalog

class ColnectItem(DjangoItem):
    django_model = Stamp
    catalogs = Field()
    cat_id = Field()
    image_urls = Field()
    image_paths = Field()
    ident = Field()

class CatalogItem(DjangoItem):
	django_model = StampInCatalog

class UrlItem(Item):
    url = Field()