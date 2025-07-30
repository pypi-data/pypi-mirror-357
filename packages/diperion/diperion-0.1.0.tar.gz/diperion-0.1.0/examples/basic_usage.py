#!/usr/bin/env python3
"""
Diperion SDK - Basic Usage Example

This example demonstrates the basic functionality of the Diperion Python SDK.
"""

import diperion

def main():
    """Basic usage example."""
    
    print("🚀 Diperion SDK - Basic Usage Example")
    print("=" * 40)
    
    # 1. Connect to the Diperion server
    print("\n1. Connecting to Diperion server...")
    try:
        client = diperion.connect_local(8080)  # or diperion.connect("http://localhost:8080")
        print("✅ Connected successfully!")
    except diperion.ConnectionError as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure your Diperion server is running on localhost:8080")
        return
    
    # 2. List existing businesses
    print("\n2. Listing existing businesses...")
    try:
        businesses = client.list_businesses()
        if businesses:
            print(f"📊 Found {len(businesses)} businesses:")
            for business in businesses:
                print(f"  • {business.name} ({business.industry}) - ID: {business.id}")
        else:
            print("📂 No businesses found.")
    except Exception as e:
        print(f"❌ Error listing businesses: {e}")
    
    # 3. Create a new business
    print("\n3. Creating a new business...")
    business_id = "demo_store"
    try:
        business = client.create_business(business_id, "A demo electronics store")
        print(f"✅ Created business: {business.name}")
    except Exception as e:
        print(f"⚠️  Business might already exist: {e}")
    
    # 4. Get business capabilities
    print("\n4. Getting business capabilities...")
    try:
        capabilities = client.get_business(business_id)
        print(f"📈 Business: {capabilities.name}")
        print(f"🏭 Industry: {capabilities.industry}")
        print(f"📊 Entity types: {capabilities.get_entity_types()}")
        
        if capabilities.example_commands:
            print("💡 Example commands:")
            for cmd in capabilities.example_commands[:3]:  # Show first 3
                print(f"  • {cmd}")
    except Exception as e:
        print(f"❌ Error getting capabilities: {e}")
    
    # 5. Create some products
    print("\n5. Creating products...")
    products_to_create = [
        {
            "name": "iPhone 15 Pro",
            "attributes": {
                "price": 999.99,
                "brand": "Apple",
                "category": "Smartphone",
                "available": True
            }
        },
        {
            "name": "AirPods Pro",
            "attributes": {
                "price": 249.99,
                "brand": "Apple",
                "category": "Audio",
                "available": True
            }
        },
        {
            "name": "Samsung Galaxy S24",
            "attributes": {
                "price": 899.99,
                "brand": "Samsung",
                "category": "Smartphone",
                "available": False
            }
        }
    ]
    
    created_products = []
    for product_data in products_to_create:
        try:
            product = client.create_node(
                business_id=business_id,
                name=product_data["name"],
                node_type="Product",
                attributes=product_data["attributes"]
            )
            created_products.append(product)
            print(f"✅ Created: {product.name}")
        except Exception as e:
            print(f"⚠️  Product might already exist: {product_data['name']} - {e}")
    
    # 6. Query products
    print("\n6. Querying products...")
    
    # Query all products
    try:
        all_products = client.query(business_id, "LIST Product")
        print(f"📱 All products ({len(all_products)} found):")
        for product in all_products:
            price = product.get_attribute('price', 'Unknown')
            available = product.get_attribute('available', 'Unknown')
            print(f"  • {product.name}: ${price} ({'Available' if available else 'Out of stock'})")
    except Exception as e:
        print(f"❌ Error querying all products: {e}")
    
    # Query with conditions
    try:
        apple_products = client.query(business_id, 'FIND Product WHERE brand = "Apple"')
        print(f"\n🍎 Apple products ({len(apple_products)} found):")
        for product in apple_products:
            print(f"  • {product.name}: ${product.get_attribute('price')}")
    except Exception as e:
        print(f"❌ Error querying Apple products: {e}")
    
    # Query with price filter
    try:
        cheap_products = client.query(business_id, "FIND Product WHERE price < 500")
        print(f"\n💰 Products under $500 ({len(cheap_products)} found):")
        for product in cheap_products:
            print(f"  • {product.name}: ${product.get_attribute('price')}")
    except Exception as e:
        print(f"❌ Error querying cheap products: {e}")
    
    # 7. Create relationships
    print("\n7. Creating relationships...")
    try:
        # Create compatibility relationship
        success = client.create_relationship(
            business_id=business_id,
            from_node_name="AirPods Pro",
            to_node_name="iPhone 15 Pro", 
            relationship_type="compatible_with"
        )
        if success:
            print("✅ Created compatibility relationship: AirPods Pro ↔ iPhone 15 Pro")
        
        # Create category relationship
        success = client.create_relationship(
            business_id=business_id,
            from_node_name="iPhone 15 Pro",
            to_node_name="Premium Category",
            relationship_type="classified_as"
        )
        if success:
            print("✅ Created category relationship: iPhone 15 Pro → Premium Category")
            
    except Exception as e:
        print(f"⚠️  Error creating relationships: {e}")
    
    # 8. Explore relationships
    print("\n8. Exploring relationships...")
    try:
        relationships = client.get_relationships(business_id)
        if relationships:
            print(f"🔗 Found {len(relationships)} relationship types:")
            for rel in relationships:
                print(f"  • {rel.relationship_type}: {rel.count} connections")
        else:
            print("🔗 No relationships found")
    except Exception as e:
        print(f"❌ Error getting relationships: {e}")
    
    # 9. Get graph visualization data
    print("\n9. Getting graph visualization...")
    try:
        graph = client.get_graph_visualization(business_id, max_nodes=20)
        print(f"📊 Graph overview:")
        print(f"  • Nodes: {graph.node_count()}")
        print(f"  • Edges: {graph.edge_count()}")
        print(f"  • Node types: {', '.join(graph.get_node_types())}")
        print(f"  • Processing time: {graph.processing_time_ms}ms")
    except Exception as e:
        print(f"❌ Error getting graph visualization: {e}")
    
    print("\n🎉 Basic usage example completed!")
    print("\n💡 Next steps:")
    print("  • Try modifying the queries")
    print("  • Create more complex relationships")
    print("  • Explore the graph visualization data")


if __name__ == "__main__":
    main() 