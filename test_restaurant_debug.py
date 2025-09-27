#!/usr/bin/env python3
"""
Test script to debug restaurant search functionality
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to Python path
import sys
sys.path.append('/Users/kyleprice/Desktop/shell_hacks/src')

async def test_restaurant_search():
    """Test the restaurant search functionality"""
    
    # Import the travel APIs
    try:
        from travel_apis import travel_apis
        print("✅ Successfully imported travel_apis")
    except Exception as e:
        print(f"❌ Failed to import travel_apis: {e}")
        return
    
    # Test Google Places API key
    google_key = os.getenv("GOOGLE_PLACES_API_KEY")
    print(f"Google Places API Key: {'✅ Found' if google_key else '❌ Not Found'}")
    if google_key:
        print(f"Key starts with: {google_key[:20]}...")
    
    # Test restaurant search
    print("\n🍽️ Testing restaurant search...")
    try:
        # Test with a specific destination
        destination = "Paris"
        max_budget = 50.0
        
        result = await travel_apis.search_restaurants(
            destination=destination,
            max_budget_per_meal=max_budget,
            cuisine_preferences=["fine dining", "local cuisine"]
        )
        
        print(f"Restaurant search result type: {type(result)}")
        print(f"Restaurant search result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict) and "restaurants" in result:
            restaurants = result["restaurants"]
            print(f"Number of restaurants found: {len(restaurants)}")
            
            for i, restaurant in enumerate(restaurants[:2]):  # Show first 2
                print(f"\nRestaurant {i+1}:")
                print(f"  Name: {restaurant.get('name', 'N/A')}")
                print(f"  Rating: {restaurant.get('rating', 'N/A')}")
                print(f"  Address: {restaurant.get('address', 'N/A')}")
                print(f"  Cost: ${restaurant.get('estimated_cost', 'N/A')}")
        else:
            print("❌ No restaurants found or invalid result format")
            print(f"Raw result: {result}")
            
    except Exception as e:
        print(f"❌ Restaurant search failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_restaurant_search())
