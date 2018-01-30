from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from colnect.items import UrlItem

class ColnectSpider(CrawlSpider):
    name = "colnect"
    allowed_domains = ["colnect.com"]
    f = open('starturls.txt', 'r')
    start_urls = [url.strip() for url in f.readlines()]
    
    rules = [
        Rule(SgmlLinkExtractor(allow=[r'/*/stamps/list/page/\d+/country/\d+\-\w+']), follow=True, callback='parse_new'),
        
    ]
    def parse_new(self, response):
        item = UrlItem()
        item['url'] = response.url
        return item
