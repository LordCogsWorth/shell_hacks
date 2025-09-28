#!/bin/bash

# Quick A2A Demo Commands
echo "🧪 A2A Agent Ecosystem Test Suite"
echo "================================="

echo ""
echo "1️⃣ Agent Discovery:"
curl -s -X POST http://localhost:8005/api/discover-agents | python -c "
import sys,json
data = json.load(sys.stdin)
result = data['discovery_result']
print(f'Agents Found: {result[\"total_discovered\"]}')
print(f'Health Score: {result[\"ecosystem_health\"][\"overall_health_score\"]}%')
"

echo ""
echo "2️⃣ Budget Negotiation:"
curl -s -X POST http://localhost:8002/api/negotiate-budget \
  -H "Content-Type: application/json" \
  -d '{"hotel_id":"HTL001","available_budget":400,"nights":2,"current_price_per_night":200}' | \
  python -c "
import sys,json
data = json.load(sys.stdin)
result = data['negotiation_result']
print(f'Negotiation: {\"✅ Accepted\" if result[\"negotiation_accepted\"] else \"❌ Rejected\"}')
print(f'Final Price: \${result.get(\"final_price_per_night\", result.get(\"counter_offer_per_night\", \"N/A\"))}/night')
"

echo ""
echo "3️⃣ Activity Planning:"
curl -s -X POST http://localhost:8003/api/search-activities \
  -H "Content-Type: application/json" \
  -d '{"destination":"Miami","budget_per_person":75,"group_size":2}' | \
  python -c "
import sys,json
data = json.load(sys.stdin)
activities = data['activities']
print(f'Activities Found: {len(activities)}')
if activities:
    print(f'Best Option: {activities[0][\"name\"]} - \${activities[0][\"calculated_price\"]}/person')
"

echo ""
echo "4️⃣ AI Coordination:"
curl -s -X POST http://localhost:8005/api/coordinate-agents \
  -H "Content-Type: application/json" \
  -d '{"task_type":"comprehensive_trip_planning","requirements":{"budget":1200,"travelers":2}}' | \
  python -c "
import sys,json
data = json.load(sys.stdin)
result = data['coordination_result']
print(f'Success Probability: {result[\"success_probability\"]*100:.1f}%')
print(f'Execution Time: {result[\"estimated_execution_time\"]}')
"

echo ""
echo "✅ All tests complete! Your A2A ecosystem is ready! 🚀"
