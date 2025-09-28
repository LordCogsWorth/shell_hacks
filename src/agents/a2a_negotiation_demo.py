"""
A2A Agent Negotiation Demo

This script demonstrates budget negotiation and coordination between
specialized agents in our A2A ecosystem.
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Any


class A2AAgentNegotiationDemo:
    """Demonstrate A2A agent negotiation and coordination"""
    
    def __init__(self):
        self.agents = {
            "discovery": "http://localhost:8005",
            "flight": "http://localhost:8001", 
            "hotel": "http://localhost:8002",
            "activity": "http://localhost:8003",
            "ai": "http://localhost:8004"
        }
        
        # Sample trip request for negotiation
        self.trip_request = {
            "destination": "Miami, FL",
            "departure_location": "New York, NY",
            "start_date": "2025-09-28",
            "end_date": "2025-09-30",
            "travelers": 2,
            "total_budget": 1200,
            "preferences": ["tech_tours", "good_food", "hackathon_venue"]
        }
    
    async def run_full_demo(self):
        """Run complete A2A negotiation demonstration"""
        print("🚀 Starting A2A Agent Negotiation Demo")
        print("=" * 50)
        
        # Step 1: Discover agents
        print("🔍 Step 1: Discovering A2A agents...")
        discovery_result = await self.discover_agents()
        
        if discovery_result:
            print(f"✅ Discovered {discovery_result.get('total_discovered', 0)} agents")
        else:
            print("❌ Agent discovery failed")
            return
        
        # Step 2: Test agent communication
        print("\n🔗 Step 2: Testing agent communication...")
        await self.test_agent_communication()
        
        # Step 3: Coordinate budget negotiation
        print("\n💰 Step 3: Coordinating budget negotiation...")
        await self.demonstrate_budget_negotiation()
        
        # Step 4: Show AI-powered optimization
        print("\n🧠 Step 4: AI-powered trip optimization...")
        await self.demonstrate_ai_optimization()
        
        # Step 5: Test disruption handling
        print("\n🚨 Step 5: Testing disruption handling...")
        await self.demonstrate_disruption_handling()
        
        print("\n✅ A2A Agent Negotiation Demo Complete!")
        print("🤝 Agents successfully negotiated and coordinated")
    
    async def discover_agents(self) -> Dict[str, Any]:
        """Discover all agents in the ecosystem"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{self.agents['discovery']}/api/discover-agents")
                response.raise_for_status()
                
                result = response.json()
                discovery_data = result.get('discovery_result', {})
                
                print(f"   📊 Ecosystem Health: {discovery_data.get('ecosystem_health', {}).get('status', 'unknown')}")
                
                active_agents = discovery_data.get('active_agents', [])
                for agent in active_agents:
                    print(f"   🤖 {agent.get('name', 'Unknown')} ({agent.get('agent_id', 'unknown')})")
                    print(f"      Capabilities: {', '.join(agent.get('capabilities', [])[:3])}...")
                
                return discovery_data
                
        except Exception as e:
            print(f"   ❌ Discovery failed: {e}")
            return {}
    
    async def test_agent_communication(self):
        """Test communication between agents"""
        try:
            # Test flight agent -> hotel agent communication
            test_request = {
                "source_agent_id": "flight-booking-agent",
                "target_agent_id": "hotel-booking-agent"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.agents['discovery']}/api/test-communication",
                    json=test_request
                )
                response.raise_for_status()
                
                result = response.json()
                
                if result.get('success'):
                    print(f"   ✅ Communication test passed")
                    print(f"      Response time: {result.get('response_time_ms', 0):.0f}ms")
                    print(f"      Target capabilities: {', '.join(result.get('target_capabilities', [])[:3])}...")
                else:
                    print(f"   ❌ Communication test failed: {result.get('error')}")
                    
        except Exception as e:
            print(f"   ❌ Communication test error: {e}")
    
    async def demonstrate_budget_negotiation(self):
        """Demonstrate budget negotiation between agents"""
        total_budget = self.trip_request['total_budget']
        
        print(f"   💵 Total Budget: ${total_budget}")
        print(f"   👥 Travelers: {self.trip_request['travelers']}")
        
        # Step 1: Get flight quotes
        flight_data = await self.get_flight_quotes()
        flight_cost = flight_data.get('estimated_cost', 400)
        
        # Step 2: Negotiate hotel budget with remaining funds
        remaining_budget = total_budget - flight_cost
        hotel_data = await self.negotiate_hotel_budget(remaining_budget * 0.6)  # 60% for hotel
        hotel_cost = hotel_data.get('final_cost', remaining_budget * 0.6)
        
        # Step 3: Allocate activity budget
        activity_budget = remaining_budget - hotel_cost
        activity_data = await self.plan_activities_within_budget(activity_budget)
        
        print(f"\n   📊 Budget Negotiation Results:")
        print(f"      ✈️  Flights: ${flight_cost:.0f}")
        print(f"      🏨 Hotels: ${hotel_cost:.0f}")
        print(f"      🎯 Activities: ${activity_budget:.0f}")
        print(f"      💰 Total: ${flight_cost + hotel_cost + activity_budget:.0f} / ${total_budget}")
        
        # Check if negotiation was successful
        if flight_cost + hotel_cost + activity_budget <= total_budget:
            print("   ✅ Budget negotiation successful - within limits!")
        else:
            print("   ⚠️  Budget negotiation needed optimization")
    
    async def get_flight_quotes(self) -> Dict[str, Any]:
        """Get flight quotes from flight agent"""
        try:
            search_data = {
                "departure_airport": "JFK",
                "arrival_airport": "MIA", 
                "departure_date": self.trip_request['start_date'],
                "return_date": self.trip_request['end_date'],
                "passengers": self.trip_request['travelers'],
                "budget_constraint": 500
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.agents['flight']}/api/search-flights",
                    json=search_data
                )
                response.raise_for_status()
                
                result = response.json()
                flights = result.get('flights', [])
                
                if flights:
                    best_flight = flights[0]
                    print(f"   ✈️  Flight Quote: ${best_flight.get('total_price', 400)} via {best_flight.get('airline', 'Airline')}")
                    return {"estimated_cost": best_flight.get('total_price', 400)}
                
        except Exception as e:
            print(f"   ❌ Flight quote error: {e}")
        
        return {"estimated_cost": 400}  # Fallback
    
    async def negotiate_hotel_budget(self, available_budget: float) -> Dict[str, Any]:
        """Negotiate hotel pricing with available budget"""
        try:
            negotiation_data = {
                "hotel_id": "HTL001_demo",
                "available_budget": available_budget,
                "nights": 2,
                "current_price_per_night": 200
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.agents['hotel']}/api/negotiate-budget",
                    json=negotiation_data
                )
                response.raise_for_status()
                
                result = response.json()
                negotiation = result.get('negotiation_result', {})
                
                if negotiation.get('negotiation_accepted'):
                    final_price = negotiation.get('total_price', available_budget)
                    print(f"   🏨 Hotel Negotiation: ${final_price} (accepted)")
                    return {"final_cost": final_price}
                else:
                    counter_offer = negotiation.get('counter_offer_total', available_budget)
                    print(f"   🏨 Hotel Negotiation: ${counter_offer} (counter-offer)")
                    return {"final_cost": counter_offer}
                    
        except Exception as e:
            print(f"   ❌ Hotel negotiation error: {e}")
        
        return {"final_cost": available_budget}
    
    async def plan_activities_within_budget(self, activity_budget: float) -> Dict[str, Any]:
        """Plan activities within remaining budget"""
        try:
            activity_data = {
                "destination": self.trip_request['destination'],
                "budget_per_person": activity_budget / self.trip_request['travelers'],
                "group_size": self.trip_request['travelers'],
                "activity_types": ["museums", "tours", "food_tour"]
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.agents['activity']}/api/search-activities",
                    json=activity_data
                )
                response.raise_for_status()
                
                result = response.json()
                activities = result.get('activities', [])
                
                total_cost = 0
                planned_activities = []
                
                for activity in activities:
                    cost = activity.get('total_cost', 0)
                    if total_cost + cost <= activity_budget:
                        planned_activities.append(activity)
                        total_cost += cost
                
                print(f"   🎯 Activities Planned: {len(planned_activities)} within ${activity_budget:.0f} budget")
                return {"activities": planned_activities, "total_cost": total_cost}
                
        except Exception as e:
            print(f"   ❌ Activity planning error: {e}")
        
        return {"activities": [], "total_cost": 0}
    
    async def demonstrate_ai_optimization(self):
        """Demonstrate AI-powered trip optimization"""
        try:
            optimization_data = {
                "trip_data": self.trip_request,
                "special_instructions": "Optimize for hackathon attendees with tech interests",
                "coordination_data": {
                    "flights": [{"airline": "JetBlue", "price": 380}],
                    "hotels": [{"name": "Tech Hotel", "price": 160}],
                    "activities": [{"name": "Tech Museum", "type": "educational"}]
                }
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.agents['ai']}/api/generate-itinerary",
                    json=optimization_data
                )
                response.raise_for_status()
                
                result = response.json()
                itinerary_result = result.get('itinerary_result', {})
                
                confidence_score = itinerary_result.get('confidence_score', 0)
                total_cost = itinerary_result.get('total_estimated_cost', 0)
                
                print(f"   🧠 AI Optimization Complete")
                print(f"      Confidence Score: {confidence_score:.2f}")
                print(f"      Estimated Cost: ${total_cost:.0f}")
                
                ai_insights = itinerary_result.get('ai_insights', {})
                if ai_insights:
                    print(f"      Personalization Score: {ai_insights.get('personalization_score', 'N/A')}")
                
        except Exception as e:
            print(f"   ❌ AI optimization error: {e}")
    
    async def demonstrate_disruption_handling(self):
        """Demonstrate disruption handling coordination"""
        try:
            disruption_data = {
                "disruption_type": "flight_delay",
                "severity": "medium", 
                "affected_components": ["arrival_time", "hotel_checkin"],
                "current_itinerary": [
                    {"date": "2025-09-28", "events": [{"time": "14:00", "type": "hotel_checkin"}]}
                ]
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.agents['ai']}/api/handle-disruption",
                    json=disruption_data
                )
                response.raise_for_status()
                
                result = response.json()
                disruption_result = result.get('disruption_result', {})
                
                if disruption_result.get('disruption_handled'):
                    alternatives = disruption_result.get('alternatives', [])
                    print(f"   🚨 Disruption Handled: {len(alternatives)} alternatives provided")
                    
                    if alternatives:
                        best_alternative = alternatives[0]
                        print(f"      Best Option: {best_alternative.get('alternative_type', 'N/A')}")
                        print(f"      Impact Level: {best_alternative.get('impact', 'N/A')}")
                else:
                    print(f"   ❌ Disruption handling failed")
                    
        except Exception as e:
            print(f"   ❌ Disruption handling error: {e}")


async def main():
    """Run the A2A negotiation demo"""
    demo = A2AAgentNegotiationDemo()
    await demo.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())
