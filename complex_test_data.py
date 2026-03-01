import json
import random
from datetime import datetime, timedelta

# Generate 1000 complex nested records
def generate_complex_data():
    categories = ["Electronics", "Clothing", "Food", "Books", "Sports", "Home", "Toys", "Health"]
    payment_methods = ["credit_card", "debit_card", "paypal", "cash", "crypto", "bank_transfer"]
    statuses = ["completed", "pending", "cancelled", "refunded", "processing"]
    regions = ["North", "South", "East", "West", "Central"]
    warehouses = ["WH-NY", "WH-LA", "WH-CHI", "WH-HOU", "WH-SEA"]
    
    # Currency options with symbols
    currencies = [
        ("$", "USD"), ("€", "EUR"), ("£", "GBP"), ("¥", "JPY"), ("₹", "INR")
    ]
    
    records = []
    base_date = datetime(2025, 1, 1)
    
    for i in range(1000):
        # Random selections
        currency_sym, currency_code = random.choice(currencies)
        category = random.choice(categories)
        region = random.choice(regions)
        warehouse = random.choice(warehouses)
        
        # Generate various nested structures
        record = {
            "id": f"ORD-{i+1:05d}",
            "order_date": (base_date + timedelta(days=random.randint(0, 400))).strftime("%Y-%m-%d"),
            "order_datetime": (base_date + timedelta(days=random.randint(0, 400), hours=random.randint(0, 23))).isoformat(),
            
            # Customer info - nested
            "customer": {
                "id": f"CUS-{random.randint(1000, 9999)}",
                "name": f"Customer {random.randint(1, 500)}",
                "email": f"user{random.randint(1, 500)}@example.com",
                "tier": random.choice(["bronze", "silver", "gold", "platinum"]),
                "location": {
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Seattle"]),
                    "state": random.choice(["NY", "CA", "IL", "TX", "WA"]),
                    "zip": f"{random.randint(10000, 99999)}",
                    "country": random.choice(["USA", "Canada", "UK", "Germany", "Japan"])
                }
            },
            
            # Financial - nested with currency
            "financials": {
                "subtotal": f"{currency_sym}{random.randint(10, 1000):,}",
                "tax": f"{currency_sym}{random.randint(1, 100):,}",
                "shipping": f"{currency_sym}{random.randint(5, 50)}",
                "discount": f"{currency_sym}{random.randint(0, 100)}",
                "total": f"{currency_sym}{random.randint(20, 1200):,}",
                "currency": currency_code,
                "exchange_rate": round(random.uniform(0.8, 150), 2)
            },
            
            # Items - array of nested objects
            "items": [
                {
                    "sku": f"SKU-{random.randint(1000, 9999)}",
                    "name": f"Product {random.randint(1, 100)}",
                    "category": category,
                    "quantity": random.randint(1, 10),
                    "unit_price": f"{currency_sym}{random.randint(5, 500)}",
                    "weight_kg": round(random.uniform(0.1, 25), 2)
                }
                for _ in range(random.randint(1, 5))
            ],
            
            # Shipping - nested
            "shipping": {
                "method": random.choice(["standard", "express", "overnight", "pickup"]),
                "carrier": random.choice(["FedEx", "UPS", "USPS", "DHL"]),
                "tracking": f"TRK{random.randint(100000, 999999)}",
                "warehouse": warehouse,
                "region": region,
                "estimated_delivery": (base_date + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
                "actual_delivery": (base_date + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d") if random.random() > 0.2 else None,
                "shipping_cost": f"{currency_sym}{random.randint(5, 50)}"
            },
            
            # Payment - nested
            "payment": {
                "method": random.choice(payment_methods),
                "status": random.choice(statuses),
                "transaction_id": f"TXN{random.randint(100000, 999999)}",
                "processed_at": (base_date + timedelta(days=random.randint(0, 400))).isoformat(),
                "auth_code": f"AUTH{random.randint(1000, 9999)}"
            },
            
            # Metadata - nested
            "metadata": {
                "source": random.choice(["web", "mobile", "api", "store"]),
                "referrer": f"ref_{random.randint(1, 20)}",
                "campaign": random.choice(["spring_sale", "black_friday", "summer_promo", "loyalty"]),
                "affiliate": f"aff_{random.randint(1, 10)}" if random.random() > 0.5 else None,
                "notes": f"Order note {i}" if random.random() > 0.7 else None,
                "internal_tags": [f"tag{random.randint(1, 5)}" for _ in range(random.randint(0, 3))]
            },
            
            # Analytics - nested
            "analytics": {
                "page_views": random.randint(1, 50),
                "session_duration_sec": random.randint(30, 1800),
                "device_type": random.choice(["desktop", "mobile", "tablet"]),
                "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                "traffic_source": random.choice(["organic", "paid", "social", "direct", "referral"])
            },
            
            # Status and flags
            "status": random.choice(statuses),
            "priority": random.choice(["low", "medium", "high", "urgent"]),
            "is_returned": random.random() > 0.9,
            "return_reason": f"Reason {random.randint(1, 10)}" if random.random() > 0.9 else None
        }
        
        records.append(record)
    
    return {"orders": records}

# Generate and save
data = generate_complex_data()

# Save to file
with open("complex_test_data.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Generated {len(data['orders'])} complex nested records")
print(f"File size: {len(json.dumps(data)) / 1024:.1f} KB")

# Show sample structure
print("\nSample record keys:")
print(list(data["orders"][0].keys()))

print("\nNested keys in 'customer':")
print(list(data["orders"][0]["customer"].keys()))

print("\nNested keys in 'financials':")
print(list(data["orders"][0]["financials"].keys()))

print("\nSample items array length:", len(data["orders"][0]["items"]))
