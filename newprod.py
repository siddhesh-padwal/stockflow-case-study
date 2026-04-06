from decimal import Decimal
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    try:
        price = Decimal(str(data['price']))
        if price < 0:
            return jsonify({"error": "Price must be non-negative"}), 400
    except:
        return jsonify({"error": "Invalid price format"}), 400

    if int(data['initial_quantity']) < 0:
        return jsonify({"error": "Initial quantity cannot be negative"}), 400

  
    warehouse = Warehouse.query.get(data['warehouse_id'])
    if not warehouse:
        return jsonify({"error": "Warehouse not found"}), 404

    try:
        with db.session.begin():  # Atomic transaction

           
            existing = Product.query.filter_by(sku=data['sku']).first()
            if existing:
                return jsonify({"error": "SKU already exists"}), 409

            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=price
            )
            db.session.add(product)
            db.session.flush()  # Get product.id without commit

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=data['warehouse_id'],
                quantity=int(data['initial_quantity'])
            )
            db.session.add(inventory)

        return jsonify({
            "message": "Product created successfully",
            "product_id": product.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 500
