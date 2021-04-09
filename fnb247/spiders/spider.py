import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import Ffnb247Item
from itemloaders.processors import TakeFirst
from scrapy.http import FormRequest
pattern = r'(\xa0)?'

class Ffnb247Spider(scrapy.Spider):
	name = 'fnb247'
	start_urls = ['https://www.fnb247.com/education-center/news/press-releases/']

	def parse(self, response):
		post_links = response.xpath('//ul[@class="list blog_feed clearfix"]//h4/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="page-next"]/a').get()
		if next_page:
			yield FormRequest.from_response(response, formdata={
				"__EVENTTARGET": 'ctl00$cph_main_content$uclBlogList$pgPaging$btnNext'}, callback=self.parse)


	def parse_post(self, response):
		date = response.xpath('//p[@class="date_author_category"]/text()').get()
		date = re.findall(r'\w+\s\d+\,\s\d+', date)
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="group_3of4 last"]//text()[not (ancestor::h1 or ancestor::p[@class="date_author_category"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=Ffnb247Item(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
