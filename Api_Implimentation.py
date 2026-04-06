from datetime import datetime, timedelta
from sqlalchemy import func

@app.route('/api/companies/<int:company_id>/alerts/low-stock')
def low_stock_alerts(company_id):

 
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    recent_date = datetime.utcnow() - timedelta(days=30)

    alerts = []


    results = db.session.query(
        Product,
        Inventory,
        Warehouse
    ).join(Inventory).join(Warehouse)\
     .filter(Product.company_id == company_id).all()

    for product, inventory, warehouse in results:

      
        recent_sales = db.session.query(func.sum(Sale.quantity))\
            .filter(
                Sale.product_id == product.id,
                Sale.created_at >= recent_date
            ).scalar() or 0

        if recent_sales == 0:
            continue  # Only alert if recent activity

        avg_daily_sales = recent_sales / 30

        if avg_daily_sales == 0:
            continue

        days_until_stockout = inventory.quantity / avg_daily_sales

        threshold = get_threshold_for_product_type(product.product_type)

        if inventory.quantity <= threshold:

            supplier = Supplier.query.join(ProductSupplier)\
                .filter(ProductSupplier.product_id == product.id)\
                .first()

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "sku": product.sku,
                "warehouse_id": warehouse.id,
                "warehouse_name": warehouse.name,
                "current_stock": inventory.quantity,
                "threshold": threshold,
                "days_until_stockout": int(days_until_stockout),
                "supplier": {
                    "id": supplier.id if supplier else None,
                    "name": supplier.name if supplier else None,
                    "contact_email": supplier.contact_email if supplier else None
                }
            })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    })
