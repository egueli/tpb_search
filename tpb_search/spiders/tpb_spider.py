from scrapy.contrib.spiders import CrawlSpider
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from tpb_search.items import TpbSearchItem

import re

class TpbSpider(CrawlSpider):
    name = "tpb"
    allowed_domains = ["thepiratebay.sx"]
    rules = [Rule(SgmlLinkExtractor(allow=['/torrent/\d+']), 'parse_torrent')]
    start_urls = [ ]
    torrent = None
    unique_magnets = []

    def __init__(self, query='big bang theory s06e10', *args, **kwargs):
        super(TpbSpider, self).__init__()
        self.start_urls = [ "http://thepiratebay.sx/search/%s/0/7/0" % query ]

    def parse_torrent(self, response):
        x = HtmlXPathSelector(response)

        id_search = re.search('/torrent/(\d+)', response.url)
        if id_search:
          torrent_id = id_search.group(1)
        else:
          self.log("can't find torrent ID")
          return []

        self.torrent = TpbSearchItem()
        self.torrent['id'] = torrent_id
        
        url = x.select("//a[@title='Get this torrent']/@href").extract()[0]
        if url in self.unique_magnets:
          self.log("ignored duplicate magnet URL")
          return []
        self.unique_magnets.append(url)
        self.torrent['magnetUrl'] = url
        
        self.torrent['title'] = x.select("//div[@id='title']/text()").extract()[0].strip()
        self.torrent['seeders'] = int(x.select("//dt[text()='Seeders:']/following::dd[1]/text()").extract()[0].strip())
        return FormRequest(
          url="http://thepiratebay.sx/ajax_details_filelist.php?id=%s" % torrent_id,
          formdata={'id':torrent_id},
          callback=self.parse_file_list
          )

    def parse_file_list(self, response):
        x = HtmlXPathSelector(response)
        file_names = x.select("//tr/td[1]/text()").extract()
        file_sizes = x.select("//tr/td[2]/text()").extract()
        files_arr = zip(file_names, file_sizes)
        files = [{"name": f[0], "size": human2bytes(f[1].encode('ascii','ignore'))} 
                 for f in files_arr]
        self.torrent['files'] = files
        return self.torrent



def human2bytes(s):
    if s[-1] == "B":
        return int(human2bytes(s[:-1]))
    elif s[-2:] == "Ki":
        return int(human2bytes(s[:-2])*1024)
    elif s[-2:] == "Mi":
        return int(human2bytes(s[:-2])*1048576)
    elif s[-2:] == "Gi":
        return int(human2bytes(s[:-2])*1073741824)
    else:
        return float(s.strip())

        
    	
