# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from colnect.items import ColnectItem, CatalogItem
from stamps.models import StampInCatalog, Stamp
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request

class ColnectPipeline(object):
    def process_item(self, item, spider):
        
        item['issue_year'] = int(item['issue_year'])        

        choice = ['engraving','typography','lithography','offset','recess','letterset','laserprint','mezzotint','photogravure','collotype','embossed','other']
        a = str(item['printing_method']).lower()
        item['printing_method'] = ""
        for i in range(0,11):
            if choice[i] in a:
                item['printing_method'] = item['printing_method'] + str(i) + ','
        item['printing_method'] = item['printing_method'][:-1]

        authorized = ["Yt:", "Mi:", "WAD:", "Sg:", "Sn:"]
        catalogs = []
        id_catalogs = []
        for i in range(0, len(item['catalogs'])):
            if str(item['catalogs'][i]) in authorized:
                id_catalogs.append(item['cat_id'][i])
                catalogs.append(item['catalogs'][i])
        
        if item['name'] != None and item['issue_country'] != None and item['issue_year'] != None and item['face_value'] != None:
            stamp=Stamp(
                name=item['name'],
                issue_country=str(item['issue_country']),
                issue_year=int(item['issue_year']),
                face_value=item['face_value'],
                currency=item['currency'],
                paper_type=item['paper_type'],
                printing_method=item['printing_method'],
                series=item['series'],
                color=item['color'],
                perforation=item['perforation'],
                
            )

            stamp.save()
            item['ident'] = stamp.id
            for i in range(0, len(catalogs)):
                if str(id_catalogs[i])[-2:] == ", ":
                    id_catalogs[i] = str(id_catalogs[i])[:-2]

                item_cat = StampInCatalog(
                    catalog_name=str(catalogs[i]).upper()[:2], 
                    stampcat_id=str(id_catalogs[i]),
                    trustability="SC",
                    stamp=stamp
                )
                try:
                    item_cat.save()
                except:
                    pass
        return item
#this class allows to create a waiting list of pictures to download in parallel with the scraping 
class MyImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            image_url = image_url.replace("/t/", "/f/")
            print item.get('image_urls', [])
            yield Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        
        stampy = Stamp.objects.get(id=item['ident'])

        stampy.picture = str(image_paths[0])
        stampy.save()
        return item