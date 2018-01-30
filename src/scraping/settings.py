# Scrapy settings for colnect project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'colnect'
SPIDER_MODULES = ['colnect.spiders']
NEWSPIDER_MODULE = 'colnect.spiders'
ITEM_PIPELINES = ['colnect.pipelines.ColnectPipeline', 'colnect.pipelines.MyImagesPipeline',]
IMAGES_STORE = '/usr/local/www/myphilately/media/'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'colnect (+http://www.yourdomain.com)'

meta={'dont_redirect': True,"handle_httpstatus_list": [302, 301, 303]}
#meta={'dont_redirect': True,"handle_httpstatus_list": [301]}

DOWNLOADER_MIDDLEWARE = {
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': False,
}

def setup_django_env(path):
    import imp, os
    from django.core.management import setup_environ

    f, filename, desc = imp.find_module('settings', [path])
    project = imp.load_module('settings', f, filename, desc)

    setup_environ(project)

    # Add django project to sys.path
    import sys
    sys.path.append(os.path.abspath(os.path.join(path, os.path.pardir)))

setup_django_env('/usr/local/www/myphilately/')
