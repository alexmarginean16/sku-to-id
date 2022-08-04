from flask import Flask, request
import os
from dotenv import load_dotenv
import shopify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

load_dotenv()

SHOPIFY_STORE_URL =  os.environ.get("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_API_VERSION = os.environ.get("SHOPIFY_API_VERSION")

session = shopify.Session(SHOPIFY_STORE_URL, SHOPIFY_API_VERSION, SHOPIFY_ACCESS_TOKEN)

@app.route('/')
def index():
	return "Hello World"

@app.route('/skutoid/')
def skuToId():
	try:
		sku = request.args['sku']
	except:
		return "The URL provided doesn't have the right format."

	shopify.ShopifyResource.activate_session(session)

	iterator = shopify.Variant.find()
	for variant in iterator:
		if str(variant.sku) == str(sku):
			return str(variant.id)

	while iterator.has_next_page():
		for variant in iterator:
			if str(variant.sku) == str(sku):
				return str(variant.id)

		iterator = iterator.next_page()

	shopify.ShopifyResource.clear_session()

	return "Product with this SKU doesn't exist"

if __name__=='__main__':
	app.run(debug=True)