from scrapy.spider import BaseSpider
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from colnect.items import ColnectItem

class ColnectSpider(CrawlSpider):
    name = "colnectscrap"
    f = open('urlfinal.txt', 'r')
    start_urls = [url.strip() for url in f.readlines()]
    rules = [
        Rule(SgmlLinkExtractor(allow=[r'/en/stamps/list/page/\d+/country/\d+\-\w+']), follow=True, callback='parse_old'),
    ]
    def parse_old(self, response):
        hxs = HtmlXPathSelector(response)
        countries = hxs.select("//ul[@id='pl_items']/li/div[@itemtype='http://schema.org/Product']")
        items = []
        for coun in countries:
            item = ColnectItem()
            try:
                item['name'] = coun.select("h2/a/text()").extract()[0].strip()
            except:
                item['name'] = "Unknown"
            try:
                item['issue_country'] = coun.select("//div[@class='filter_box']/p/a[1]/text()").extract()[0].strip()            
            except:
                item['issue_country'] = "Unknown"
            try:
                item['issue_year'] = coun.select("div[@class='i_d']/dl/dt[.='Issued on:']/following-sibling::dd[1]/a/text()").extract()[0].strip()
            except:
                item['issue_year'] = 0000
            try:
                item['face_value'] = coun.select("div[@class='i_d']/dl/dt[.='Face value:']/following-sibling::dd[1]/text()").extract()[0].strip()
            except:
                item['face_value'] = "N/A"
            try:
                item['currency'] = coun.select("div[@class='i_d']/dl/dt[.='Face value:']/following-sibling::dd[1]/span/text()").extract()[0].strip()
            except:
                item['currency'] = ""
            try:
                item['series'] = coun.select("div[@class='i_d']/dl/dt[.='Series:']/following-sibling::dd[1]/a/text()").extract()[0].strip()
            except:
                item['series'] = ""
            try:
                item['color'] = coun.select("div[@class='i_d']/dl/dt[.='Colors:']/following-sibling::dd[1]/a/text()").extract()[0].strip()
            except:
                item['color'] = ""
            try:
                item['printing_method'] = coun.select("div[@class='i_d']/dl/dt[.='Printing:']/following-sibling::dd[1]/text()").extract()[0].strip()
            except:
                item['printing_method'] = ""
            try:
                item['catalogs'] = coun.select("div[@class='i_d']/dl/dt[.='Catalog codes:']/following-sibling::dd[1]/strong/text()").extract()
            except:
                item['catalogs'] = ""    
            try: 
                item['cat_id'] = coun.select("div[@class='i_d']/dl/dt[.='Catalog codes:']/following-sibling::dd[1]/text()").extract()
            except: 
                item['cat_id'] = ""
            try:
                item['paper_type'] = coun.select("div[@class='i_d']/dl/dt[.='Paper:']/following-sibling::dd[1]/text()").extract()[0].strip()
            except:
                item['paper_type'] = ""
            try:
                item['perforation'] = coun.select("div[@class='i_d']/dl/dt[.='Perforation:']/following-sibling::dd[1]/text()").extract()[0].strip()
            except:
                item['perforation'] = ""
            try:
                item['image_urls'] = [coun.select("div[@class='item_thumb']/a/img/@src").extract()[0].strip()]
            except:
                item['image_urls'] = ""
            if item['issue_country'] != "Unknown" or item['issue_year'] != 0000:
                items.append(item)
        return items

    def parse_new(self, response):
        hxs = HtmlXPathSelector(response)
        coun = hxs.select("//div[@class='i_d']")
        item = ColnectItem()
        item['name'] = coun.select("dl/dt[.='Country:']/following-sibling::dd[1]/a/text()").extract()            
        item['issue_country'] = coun.select("dl/dt[.='Country:']/following-sibling::dd[1]/a/text()").extract()            
        item['issue_year'] = coun.select("dl/dt[.='Issued on:']/following-sibling::dd[1]/a/text()").extract()
        item['face_value'] = coun.select("dl/dt[.='Face value:']/following-sibling::dd[1]/text()").extract()
        return item
                
