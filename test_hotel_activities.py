#!/usr/bin/env python3
"""
Test script for hotel and activities APIs
"""

import asyncio
from datetime import date, timedelta
from decimal import Decimal
import sys
import os

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from travel_apis import HotelBookingAPI, ActivityBookingAPI, HotelSearchParams

async def test_hotels():
    """Test hotel booking API"""
    print("🏨 Testing Hotel Booking API...")
    print("=" * 50)
    
    hotel_api = HotelBookingAPI()
    
    # Test parameters
    test_params = HotelSearchParams(
        destination="Paris",
        check_in=date.today() + timedelta(days=30),
        check_out=date.today() + timedelta(days=35),
        guests=2,
        max_price_per_night=Decimal("150")
    )
    
    print(f"🔍 Searching hotels in: {test_params.destination}")
    print(f"📅 Check-in: {test_params.check_in}, Check-out: {test_params.check_out}")
    print(f"👥 Guests: {test_params.guests}")
    print(f"💰 Max per night: ${test_params.max_price_per_night}")
    print()
    
    try:
        hotels = await hotel_api.search_hotels(test_params)
        
        if hotels:
            print(f"✅ Found {len(hotels)} hotels:")
            for i, hotel in enumerate(hotels[:3], 1):
                print(f"\n🏨 Hotel {i}:")
                print(f"   Name: {hotel.get('name', 'N/A')}")
                print(f"   Rating: {hotel.get('rating', 'N/A')} stars")
                print(f"   Price/night: ${hotel.get('price_per_night', 'N/A')}")
                print(f"   Total: ${hotel.get('total_price', 'N/A')}")
                print(f"   Location: {hotel.get('location', 'N/A')}")
                print(f"   Amenities: {', '.join(hotel.get('amenities', [])[:3])}")
        else:
            print("❌ No hotels found")
            return False
            
    except Exception as e:
        print(f"❌ Hotel API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_activities():
    """Test activities booking API"""
    print("\n🎯 Testing Activities Booking API...")
    print("=" * 50)
    
    activity_api = ActivityBookingAPI()
    
    # Test parameters
    destination = "Paris"
    max_budget = Decimal("200")
    preferences = ["cultural", "sightseeing"]
    
    print(f"🔍 Searching activities in: {destination}")
    print(f"💰 Max budget: ${max_budget}")
    print(f"🎯 Preferences: {', '.join(preferences)}")
    print()
    
    try:
        activities = await activity_api.search_activities(destination, max_budget, preferences)
        
        if activities:
            print(f"✅ Found {len(activities)} activities:")
            
            # Separate sights and activities for better display
            sights = [a for a in activities if 'sight' in a.get('category', '')]
            experiences = [a for a in activities if 'sight' not in a.get('category', '')]
            
            if sights:
                print("\n👁️  SIGHTS TO SEE:")
                for i, sight in enumerate(sights[:3], 1):
                    price_text = f"${sight.get('price', 'N/A')}" if sight.get('price', 0) > 0 else "Free"
                    print(f"   {i}. {sight.get('name', 'N/A')} - {price_text}")
                    print(f"      Type: {sight.get('type', 'N/A')} | Duration: {sight.get('duration', 'N/A')} | Rating: {sight.get('rating', 'N/A')}")
                    print(f"      {sight.get('description', 'N/A')[:100]}...")
            
            if experiences:
                print("\n🎪 ACTIVITIES TO DO:")
                for i, activity in enumerate(experiences[:3], 1):
                    print(f"   {i}. {activity.get('name', 'N/A')} - ${activity.get('price', 'N/A')}")
                    print(f"      Type: {activity.get('type', 'N/A')} | Duration: {activity.get('duration', 'N/A')} | Rating: {activity.get('rating', 'N/A')}")
                    print(f"      {activity.get('description', 'N/A')[:100]}...")
        else:
            print("❌ No activities found")
            return False
            
    except Exception as e:
        print(f"❌ Activities API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_api_integration():
    """Test the full API integration"""
    print("\n🔄 Testing Full API Integration...")
    print("=" * 50)
    
    try:
        from travel_apis import travel_apis
        
        # Test search_all method
        result = await travel_apis.search_all(
            destination="Barcelona",
            departure_location="New York",
            start_date=date.today() + timedelta(days=45),
            end_date=date.today() + timedelta(days=50),
            travelers=2,
            budget=Decimal("2500"),
            preferences=["cultural", "adventure"]
        )
        
        print("✅ API Integration results:")
        print(f"   Flights found: {len(result.get('flights', []))}")
        print(f"   Hotels found: {len(result.get('hotels', []))}")
        print(f"   Activities found: {len(result.get('activities', []))}")
        
        # Show sample data
        if result.get('hotels'):
            hotel = result['hotels'][0]
            print(f"\n🏨 Sample hotel: {hotel.get('name', 'N/A')} - ${hotel.get('price_per_night', 'N/A')}/night")
        
        if result.get('activities'):
            activity = result['activities'][0]
            print(f"🎯 Sample activity: {activity.get('name', 'N/A')} - ${activity.get('price', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_environment_setup():
    """Test if environment variables are properly configured"""
    print("⚙️  Testing Environment Setup...")
    print("=" * 50)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for API keys
        amadeus_key = os.getenv("AMADEUS_API_KEY")
        amadeus_secret = os.getenv("AMADEUS_API_SECRET")
        tripadvisor_key = os.getenv("TRIPADVISOR_API_KEY")
        
        print(f"🔑 Amadeus API Key: {'✅ Found' if amadeus_key else '❌ Missing'}")
        print(f"🔑 Amadeus Secret: {'✅ Found' if amadeus_secret else '❌ Missing'}")
        print(f"🔑 TripAdvisor Key: {'✅ Found' if tripadvisor_key else '❌ Missing'}")
        
        if amadeus_key and amadeus_secret:
            print("✅ Hotel API can use Amadeus")
        else:
            print("⚠️  Hotel API will use mock data")
            
        if tripadvisor_key:
            print("✅ Activities API can use TripAdvisor")
        else:
            print("⚠️  Activities API will use mock data")
            
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 Starting Hotel & Activities API Tests")
    print("=" * 60)
    
    # Test environment setup first
    env_ok = await test_environment_setup()
    
    # Test individual APIs
    hotel_ok = await test_hotels()
    activities_ok = await test_activities()
    
    # Test integration
    integration_ok = await test_api_integration()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Environment Setup: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"Hotel API: {'✅ PASS' if hotel_ok else '❌ FAIL'}")
    print(f"Activities API: {'✅ PASS' if activities_ok else '❌ FAIL'}")
    print(f"API Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    if all([env_ok, hotel_ok, activities_ok, integration_ok]):
        print("\n🎉 All tests PASSED! Hotel and Activities APIs are working correctly.")
    else:
        print("\n⚠️  Some tests FAILED. Check the output above for details.")
        
        # Provide troubleshooting tips
        if not env_ok:
            print("\n🔧 Environment Issues:")
            print("   - Check your .env file has AMADEUS_API_KEY and AMADEUS_API_SECRET")
            print("   - Add TRIPADVISOR_API_KEY for real activities data")
        
        if not hotel_ok:
            print("\n🔧 Hotel API Issues:")
            print("   - Verify Amadeus credentials are valid")
            print("   - Check network connectivity")
            print("   - Hotel API may be using mock data (which is OK for testing)")
        
        if not activities_ok:
            print("\n🔧 Activities API Issues:")
            print("   - Verify TripAdvisor API key is valid")
            print("   - Check network connectivity") 
            print("   - Activities API may be using mock data (which is OK for testing)")


if __name__ == "__main__":
    asyncio.run(main())
