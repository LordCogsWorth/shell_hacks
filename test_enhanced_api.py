#!/usr/bin/env python3

import requests
import json
import sys

def test_enhanced_activities():
    """Test the enhanced TripAdvisor integration"""
    
    # Test data for Rome
    test_data = {
        "destination": "Rome",
        "departure_location": "New York",
        "budget": 1200,
        "duration_days": 3,
        "start_date": "2024-06-01",
        "end_date": "2024-06-04",
        "preferences": ["cultural"],
        "travelers": 1
    }
    
    print("🚀 Testing Enhanced TripAdvisor Integration...")
    print(f"📍 Destination: {test_data['destination']}")
    print(f"💰 Budget: ${test_data['budget']}")
    print(f"📅 Duration: {test_data['duration_days']} days")
    print()
    
    try:
        # Make API request
        response = requests.post(
            "http://localhost:8000/api/plan-trip",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Request Successful!")
            print()
            
            # Show activities the AI selected
            activities = result.get("activities", [])
            print(f"🎯 AI Agent Selected {len(activities)} Activities:")
            print("=" * 50)
            
            for i, activity in enumerate(activities, 1):
                print(f"{i}. {activity['name']}")
                print(f"   Type: {activity['type']}")
                print(f"   Price: ${activity['price']}")
                print(f"   Duration: {activity['duration']}")
                print(f"   Rating: {activity['rating']}/5")
                print(f"   Location: {activity['location']}")
                print(f"   Description: {activity['description']}")
                print()
            
            # Show detailed daily schedule
            schedule = result.get("daily_schedule", [])
            print("📅 Daily Schedule (Enhanced):")
            print("=" * 50)
            
            for day in schedule:
                print(f"Day {day['day_number']} - {day['date']}")
                day_activities = day.get('activities', [])
                
                if day_activities:
                    for activity in day_activities:
                        print(f"  • {activity['name']} (${activity['price']})")
                        print(f"    {activity['description']}")
                else:
                    print("  • Free day / Travel day")
                
                print(f"  💰 Estimated cost: ${day['estimated_cost']}")
                print()
            
            # Show budget breakdown
            breakdown = result.get("budget_breakdown", {})
            print("💰 Budget Breakdown:")
            print("=" * 30)
            for category, cost in breakdown.items():
                print(f"{category.title()}: ${cost}")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test Failed: {e}")

if __name__ == "__main__":
    test_enhanced_activities()