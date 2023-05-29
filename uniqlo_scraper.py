import scrapy
import sys

URL = sys.argv[3]
FILENAME = sys.argv[5]

class MySpider(scrapy.Spider):
    name = 'my_spider'
    start_urls = [URL[4:]]
    
    def parse(self, response):
        # Save the response as an HTML file
        filename = FILENAME[4:]
        with open(filename, 'wb') as file:
            file.write(response.body)

        self.log(f'Saved file {filename}')