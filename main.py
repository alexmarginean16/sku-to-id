from flask import Flask, request
import os
from dotenv import load_dotenv
import shopify
from flask_cors import CORS, cross_origin
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app)

load_dotenv()

SHOPIFY_STORE_URL =  os.environ.get("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_API_VERSION = os.environ.get("SHOPIFY_API_VERSION")

session = shopify.Session(SHOPIFY_STORE_URL, SHOPIFY_API_VERSION, SHOPIFY_ACCESS_TOKEN)

app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = os.environ.get("MYSQL_CURSORCLASS")

mysql = MySQL(app)

@app.route('/')
def index():
	return "Hello World"

@app.route('/addproducts')
def addProducts():
	cur = mysql.connection.cursor()
	cur.execute('''SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = "BASE TABLE" AND TABLE_NAME = "Variants"''')
	result = cur.fetchall()

	if len(result) != 0:
		print("Variants table already exists, deleting the current one.")
		cur.execute('''DROP TABLE Variants''')
		mysql.connection.commit()

	print("Creating a new empty Variants table")
	cur.execute('''CREATE TABLE Variants (variant_sku VARCHAR(100), variant_id VARCHAR(100))''')

	shopify.ShopifyResource.activate_session(session)

	iterator = shopify.Variant.find()
	for variant in iterator:
		print("Inserting into table Product: {}".format(variant.title))
		cur.execute('''INSERT INTO Variants VALUES ("%s", "%s")''' % (variant.sku, variant.id))
		mysql.connection.commit()

	while iterator.has_next_page():
		for variant in iterator:
			print("Inserting into table Product: {}".format(variant.title))
			cur.execute('''INSERT INTO Variants VALUES ("%s", "%s")''' % (variant.sku, variant.id))
			mysql.connection.commit()

		iterator = iterator.next_page()

	shopify.ShopifyResource.clear_session()

	return "Created an empty Variants Table"

@app.route('/skutoid/')
def skuToId():
	try:
		sku = request.args['sku']
	except:
		return "The URL provided doesn't have the right format."

	cur = mysql.connection.cursor()
	cur.execute('''SELECT * FROM Variants WHERE variant_sku = "%s"''' % (sku))
	result = cur.fetchall()

	if len(result) != 0:
		response = {
			"item": {
				"Name": "No name available for now",
				"Sku": result[0]['variant_sku'],
				"ShopifyID": result[0]['variant_id']
			}
		}
		return response
	else:
		response = "Product with this SKU doesn't exist"

	return response

if __name__=='__main__':
	app.run(debug=True)