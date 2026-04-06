# stockflow-case-study

Part 1: Code Review & Debugging
1. Issues found

While reviewing the given API code, I noticed the following issues:

• No Input Validation

The API directly uses values from the request without checking:

Whether required fields exist
Whether values are of correct type (e.g., price, quantity)
Whether fields are valid (like negative values)
• Multiple Database Commits

The code commits twice:

Once after creating the product
Once after creating inventory
• No Transaction Handling

Both operations (product + inventory) are not wrapped in a single transaction.

• SKU Uniqueness Not Checked

The code does not check if the SKU already exists, even though it must be unique across the platform.

• Incorrect Product-Warehouse Relationship

The product is directly linked to a warehouse_id, but based on requirements:

A product can exist in multiple warehouses
So this design is incorrect.
• Price Handling Not Proper

The price is taken as-is:

No validation
No guarantee it's a decimal
Could lead to precision issues
• No Error Handling

There is no exception handling:

If DB fails, API crashes
No rollback is handled
• Warehouse Not Validated

The API assumes that the warehouse exists.

• Initial Quantity Not Validated

The quantity:

Could be missing
Could be negative
Could be invalid type
2. Impact of These Issues
• Data Inconsistency

If product is created but inventory creation fails:

Product exists without inventory
This creates incomplete and unreliable data.
• Duplicate SKUs

Without uniqueness check:

Same SKU can exist multiple times
This breaks inventory tracking and integrations.
• Application Crashes

Missing fields or invalid data can cause runtime errors, leading to API failures.

• Financial Errors

Improper handling of price can cause:

Incorrect calculations
Precision issues in billing
• Incorrect Business Logic

Linking product to a single warehouse:

Prevents storing product in multiple warehouses
Violates core requirement
• Invalid Inventory Data

Negative or incorrect quantity:

Leads to wrong stock levels
Affects reporting and alerts
3. Fix Approach (Explanation)

To fix the issues, I would improve the API in the following way:

• Add Input Validation
Check required fields
Validate types (price as decimal, quantity as integer)
Handle optional fields properly
• Use Single Transaction
Wrap product and inventory creation in one transaction
Either both succeed or both fail
• Enforce SKU Uniqueness
Check before inserting
Also enforce at database level
• Correct Data Modeling
Remove warehouse_id from product
Use inventory table to map products to warehouses
• Add Error Handling
Use try-catch
Rollback on failure
Return meaningful error messages
• Validate Warehouse
Ensure warehouse exists before inserting inventory
• Validate Quantity and Price
Prevent negative values
Ensure correct formats
Part 2: Database Design
1. Schema Design 

Based on the requirements, I designed the system with the following entities:

• Companies

Stores company-level information.

• Warehouses
Each warehouse belongs to a company
A company can have multiple warehouses
• Products
Belong to a company
Contain general info (name, SKU, price, type)
SKU is unique
• Inventory
Connects products and warehouses
Stores quantity per warehouse
One record per product per warehouse
• Inventory Movements
Tracks every stock change
Includes quantity change, reason, timestamp
• Suppliers
Stores supplier details
Linked to companies
• Product-Supplier Mapping
Many-to-many relationship
A product can have multiple suppliers
• Product Bundles
Allows products to contain other products
Used for combo or kit products
2. Missing Requirements / Questions

While designing, I found some unclear areas:

• SKU Scope
Is SKU unique globally or per company?
• Threshold Definition
Is low-stock threshold per product or product type?
• Sales Activity
What defines "recent sales"?
7 days? 30 days?
• Bundle Behavior
Does bundle have its own stock or depend on components?
• Supplier Relationships
Can suppliers be shared across companies?
• Inventory Updates
Should all changes be logged (even small ones)?
• Multi-Warehouse Rules
Can same product have different thresholds in different warehouses?
3. Design Decisions Explanation
• Separation of Product and Inventory

Products are independent:

Inventory manages stock per warehouse
This supports scalability and flexibility.
• Use of Unique Constraints
SKU must be unique
Inventory has unique (product_id, warehouse_id)
• Indexing

Indexes are needed on:

product_id
warehouse_id
company_id
To improve query performance.
• Inventory Movement Tracking

Instead of directly updating stock:

Track all changes
Helps in debugging and auditing
• Support for Bundles

Using self-relation:

Allows complex product structures
Useful for real-world scenarios
Part 3: API Implementation (Low Stock Alerts)
2. Edge Cases Considered

While designing the API, I considered the following edge cases:

• No Recent Sales
Products with no recent sales should not trigger alerts
• Division by Zero
If average sales is zero, stockout calculation fails
Must handle safely
• Missing Supplier
Some products may not have suppliers
Should return null or default values
• Invalid Company ID
If company does not exist → return error
• Multiple Warehouses
Same product in different warehouses must be handled separately
• Negative or Incorrect Inventory
If data is corrupted, avoid incorrect alerts
• Large Data Volume
Too many products may slow response
Needs optimization (future improvement)
3. Approach Explanation

My approach to implementing the low-stock alert API is:

• Step 1: Validate Input
Check if company exists
• Step 2: Fetch Product + Inventory Data
Join product, inventory, and warehouse tables
Filter by company
• Step 3: Filter Based on Sales Activity
Only consider products with recent sales
Assumed last 30 days
• Step 4: Calculate Sales Rate
Compute average daily sales
• Step 5: Calculate Stockout Time
Estimate how many days stock will last
• Step 6: Compare with Threshold
Each product has a threshold
If stock ≤ threshold → alert
• Step 7: Add Supplier Info
Fetch supplier details for reordering
• Step 8: Format Response
Return structured response as required
Assumptions Made
Recent sales = last 30 days
Threshold is based on product type
Each product has at least one supplier
Inventory is maintained per warehouse
Possible Improvements
Use aggregation queries instead of loops
Add caching for performance
Add pagination for large responses
Precompute sales metrics
