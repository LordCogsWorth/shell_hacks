#!/bin/bash

# A2A Agent Ecosystem Startup Script
echo "🚀 Starting Shell Hacks A2A Agent Ecosystem..."
echo "================================================"

# Kill any existing agents
pkill -f "python src/agents/" 2>/dev/null || true

# Wait a moment for cleanup
sleep 2

# Start each agent in background
echo "🛩️  Starting FlightBookingAgent on port 8001..."
python src/agents/flight_booking_agent.py &
FLIGHT_PID=$!

sleep 1
echo "🏨 Starting HotelBookingAgent on port 8002..."
python src/agents/hotel_booking_agent.py &
HOTEL_PID=$!

sleep 1
echo "🎯 Starting ActivityPlanningAgent on port 8003..."
python src/agents/activity_planning_agent.py &
ACTIVITY_PID=$!

sleep 1
echo "🧠 Starting GeminiAIAgent on port 8004..."
python src/agents/gemini_ai_agent.py &
AI_PID=$!

sleep 1
echo "🔍 Starting AgentDiscoveryService on port 8005..."
python src/agents/agent_discovery_service.py &
DISCOVERY_PID=$!

echo ""
echo "⏳ Waiting for agents to initialize..."
sleep 5

echo ""
echo "🔍 Testing Agent Discovery..."
curl -s -X POST http://localhost:8005/api/discover-agents | python -c "
import sys,json
try:
    data = json.load(sys.stdin)
    result = data['discovery_result']
    print(f'✅ Discovery Success: {result[\"total_discovered\"]} agents found')
    print(f'📊 Ecosystem Health: {result[\"ecosystem_health\"][\"overall_health_score\"]}%')
    for agent in result['active_agents']:
        print(f'   🤖 {agent[\"name\"]} - {len(agent[\"capabilities\"])} capabilities')
except:
    print('❌ Discovery test failed')
"

echo ""
echo "� Starting Frontend Web Server..."
python -m http.server 8000 > /dev/null 2>&1 &
WEB_PID=$!

echo ""
echo "🎉 Complete Travel System is Ready!"
echo "===================================="
echo "🌐 Frontend Website:      http://localhost:8000/frontend/"
echo ""
echo "🤖 A2A Agent Ecosystem:"
echo "🛩️  FlightBookingAgent:    http://localhost:8001"
echo "🏨 HotelBookingAgent:     http://localhost:8002"
echo "🎯 ActivityPlanningAgent: http://localhost:8003"
echo "🧠 GeminiAIAgent:         http://localhost:8004"
echo "🔍 AgentDiscoveryService: http://localhost:8005"
echo ""
echo "🚀 Ready for hackathon demo!"
echo "💡 Open http://localhost:8000/frontend/ to use the app"
echo ""
echo "To stop everything: pkill -f 'python'"
