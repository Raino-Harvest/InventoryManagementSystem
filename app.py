from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from datetime import datetime


app = Flask(__name__)
app.secret_key = "Secret Key"
app.url_map.strict_slashes = False


#SqlAlchemy Database Configuration With Mysql (Used while development using localhost server)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:<password>@localhost/inventorydatabase'

#SqlAlchemy Database Configuration With Sqlite3
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///inventoryDatabase.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#Creating model table for our CRUD database
class Products(db.Model):
    productID = db.Column(db.String(100), primary_key = True)
    productName = db.Column(db.String(100))

    def __init__(self, productID, productName):

        self.productID = productID
        self.productName = productName

class Locations(db.Model):
    locationID = db.Column(db.String(100), primary_key = True, nullable = True)
    location = db.Column(db.String(100))

    def __init__(self, locationID, location):

        self.locationID = locationID
        self.location = location

class Movements(db.Model):

    movementID = db.Column(db.Integer, primary_key = True)
    timeStamp = db.Column(db.String(100))
    fromLocation = db.Column(db.String(100))
    toLocation = db.Column(db.String(100))
    productID  = db.Column(db.String(100))
    quantity = db.Column(db.Integer)

    def __init__(self, movementID, timeStamp, fromLocation, toLocation, productID, quantity):

        self.movementID = movementID
        self.timeStamp = timeStamp
        self.fromLocation = fromLocation
        self.toLocation = toLocation
        self.productID = productID
        self.quantity = quantity


##############################################################################
##############################################################################


#HEADER
@app.route("/")
def home():
    return render_template("header.html")



#PRODUCTS
@app.route("/products", methods=['GET', 'POST', 'PUT'])
def products():
    if request.method == 'POST':

        productID = request.form['productID']
        productName = request.form['productName']

        newProduct = Products(productID,productName)

        db.session.add(newProduct)
        db.session.commit()
        addedProduct = Products.query.get_or_404(newProduct.productID)
        productsDetails = Products.query.all()
        return redirect(url_for('products'))
        #return {"locationID": addedLocation.locationID, "location": addedLocation.location} #,"product": added_location.product_id, "available_quantity": added_location.available_quantity}
    
    productsDetails = Products.query.all()
    return render_template('products.html', productsDetails = productsDetails)



#EDIT PRODUCTS
@app.route("/editproduct", methods = ['GET', 'POST'])
def editProduct():

    if request.method == 'POST':
        myData = Products.query.get(request.form.get('productID'))

        myData.productID = request.form['productID']
        myData.productName = request.form['productName']

        db.session.commit()

        return redirect(url_for('products'))
 


#LOCATIONS
@app.route("/locations", methods=['GET', 'POST', 'PUT'])
def locations():
    if request.method == 'POST':

        locationId = request.form['locationID']
        location = request.form['location']

        newLocation = Locations(locationId,location)

        db.session.add(newLocation)
        db.session.commit()
        locationsDetails = Locations.query.all()
        return redirect(url_for('locations'))
        
    locationsDetails = Locations.query.all()
    return render_template('locations.html', locationsDetails = locationsDetails)



#EDIT LOCATIONS
@app.route("/editlocation", methods = ['GET', 'POST'])
def editLocation():

    if request.method == 'POST':
        myData = Locations.query.get(request.form.get('locationID'))

        myData.locationID = request.form['locationID']
        myData.location = request.form['location']

        db.session.commit()

        return redirect(url_for('locations'))



#MOVEMENTS
@app.route("/movements", methods=['GET', 'POST', 'PUT'])
def movements():
    
    if request.method == 'POST':

        movementID = request.form['movementID']
        timeStamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        fromLocation = request.form['fromLocation']
        toLocation = request.form['toLocation']
        productID = request.form['productID']
        quantity = request.form['quantity']

        newmovement = Movements(movementID,timeStamp,fromLocation,toLocation,productID,quantity)

        db.session.add(newmovement)
        db.session.commit()
        movementsDetails = Movements.query.all()
        return redirect(url_for('movements'))
    
    movementsDetails = Movements.query.all()
    return render_template('movements.html', movementsDetails = movementsDetails)



#EDIT MOVEMENTS
@app.route("/editmovement", methods = ['GET', 'POST'])
def editMovement():

    if request.method == 'POST':
        myData = Movements.query.get(request.form.get('movementID'))

        myData.movementID = request.form['movementID']
        myData.timeStamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        myData.fromLocation = request.form['fromLocation']
        myData.toLocation = request.form['toLocation']
        myData.productID = request.form['productID']
        myData.quantity = request.form['quantity']

        db.session.commit()

        return redirect(url_for('movements'))



#BALANCE REPORT
@app.route("/home", methods=["POST", "GET"])
def report():
    movs = Movements.query.\
        join(Products, Movements.productID == Products.productID).\
        add_columns(
            Products.productID, 
            Movements.quantity,
            Movements.fromLocation,
            Movements.toLocation,
            Movements.timeStamp).\
            order_by(Movements.toLocation).\
            order_by(Movements.movementID).\
        all()
    
    balancedDict = defaultdict(lambda: defaultdict(dict))

    for mov in movs:
        productID = mov.productID
        quantity = mov.quantity
        fromLocation = mov.fromLocation
        toLocation = mov.toLocation

        if fromLocation:
            if "quantity" not in balancedDict[productID][fromLocation]:
                balancedDict[productID][fromLocation]["quantity"] = 0
            balancedDict[productID][fromLocation]["quantity"] -= quantity

        if toLocation:
            if "quantity" not in balancedDict[productID][toLocation]:
                balancedDict[productID][toLocation]["quantity"] = 0
            balancedDict[productID][toLocation]["quantity"] += quantity

    print(movements)

    return render_template("report.html", movements=balancedDict)


#MAIN
if __name__ == "__main__" :
    app.run(debug = True)