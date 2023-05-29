import json
import subprocess
from flask import Flask, render_template

app = Flask(__name__)

app.config['SERVER_NAME'] = ['3.134.238.10', '3.129.111.220', '52.15.118.168']


@app.route('/')
def index():
    # Your code logic goes here
    # Render an HTML template and pass data to it

    SALE_URL = "https://www.uniqlo.com/ca/api/commerce/v3/en/products?path=384&flagCodes=discount%2Cdiscount&sort=2&limit=500&offset=0"
    PROD_URL = 'https://www.uniqlo.com/ca/api/commerce/v3/en/products/' #need to add id 
    SALE_RESP = "response.html"
    PROD_RESP = 'product.html'
    SALES_PATH = 'sales.json'

    def scrape_product(product_url,sales):
        subprocess.call(["bash", "scrapy.sh", product_url, PROD_RESP])
        
        # Read HTML from a file
        with open('product.html', 'r') as file:
            prod_content = file.read()
            # Parse the JSON data
            prod_data = json.loads(prod_content)
        
        for product in prod_data['result']['items']:
            for x in product['l2s']:
                if x['prices']['promo'] is not None and x['stock']['statusCode']!='STOCK_OUT':

                    if product['productId'] in sales:
                        
                        if x['color']['code'] in sales[product['productId']]['avail']:
                            #add only size
                            sales[product['productId']]['avail'][x['color']['code']][x['color']['name']].append( (x['size']['name'], x['stock']['quantity']))
                        
                        else:
                            avail = { x['color']['name'] : [(x['size']['name'], x['stock']['quantity'])],
                                'link' : "https://www.uniqlo.com/ca/en/products/{}?colorCode={}".format(product['productId'], x['color']['code']),
                                'img_link': get_image_url(product['images'],x['color']['displayCode'])
                                }
                            sales[product['productId']]['avail'][x['color']['code']] = avail
                            
        
                    else:
                        avail = {'avail'  :{x['color']['code'] : { x['color']['name'] : [(x['size']['name'], x['stock']['quantity'])],
                                'link' : "https://www.uniqlo.com/ca/en/products/{}?colorCode={}".format(product['productId'], x['color']['code']),
                                'img_link': get_image_url(product['images'],x['color']['displayCode'])
                                }},
                                'price' : x['prices']['promo']['value'] }
                        sales[product['productId']] = avail
                        
                        
        return sales  

    def get_image_url(x,display_code):
        result = next((d for d in x['main'] if d.get("colorCode") == display_code), None)

        if result is not None:
            return result['url']
        else:
            return None
        
    # Call the Bash script and pass the variable as an argument
    subprocess.call(["bash", "scrapy.sh", SALE_URL, SALE_RESP])

    # Read HTML from a file
    with open(SALE_RESP, 'r') as file:
        html_content = file.read()

    # Parse the JSON data
    parsed_data = json.loads(html_content)

    items = parsed_data['result']['items']

    sales = {}
    item_Ids = [item['productId'] for item in items]
    for item_id in item_Ids:
        item_url = PROD_URL + item_id
        sales = scrape_product(item_url, sales)
        
    with open(SALES_PATH, "w") as json_file:
        json.dump(sales, json_file, indent=2 )
    
    return render_template('index.html')

@app.route('/sales.json')
def get_data():
    with open('sales.json', 'r') as file:
        data = file.read()
    return data

if __name__ == '__main__':
    app.run()