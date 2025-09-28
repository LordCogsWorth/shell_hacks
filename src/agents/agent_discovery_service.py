"""
Agent Discovery Service - A2A Protocol Service Discovery

This service enables dynamic discovery of A2A agents, capability matching,
and coordinated communication between distributed agents in the ecosystem.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
import json
import httpx
import uvicorn
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Information about a discovered agent"""
    agent_id: str
    name: str
    version: str
    base_url: str
    capabilities: List[str]
    endpoints: Dict[str, str]
    last_seen: datetime
    status: str = "active"
    response_time_ms: Optional[float] = None


class AgentDiscoveryService:
    """
    Central service for discovering and coordinating A2A agents
    """
    
    def __init__(self):
        self.service_id = "agent-discovery-service"
        self.name = "AgentDiscoveryService"
        self.version = "1.0.0"
        
        # Registry of discovered agents
        self.agent_registry: Dict[str, AgentInfo] = {}
        
        # Known agent endpoints to check
        self.known_endpoints = [
            "http://localhost:8001",  # FlightBookingAgent
            "http://localhost:8002",  # HotelBookingAgent
            "http://localhost:8003",  # ActivityPlanningAgent
            "http://localhost:8004",  # GeminiAIAgent
            "http://localhost:8000",  # TravelMasterAgent (orchestrator)
        ]
        
        # Capability mappings
        self.capability_index: Dict[str, List[str]] = {}
        
        logger.info(f"🔍 AgentDiscoveryService initialized for A2A ecosystem")
    
    async def discover_all_agents(self) -> Dict[str, Any]:
        """Discover all available A2A agents in the ecosystem"""
        logger.info("🔍 Starting comprehensive agent discovery")
        
        discovered_agents = []
        discovery_results = []
        
        for endpoint in self.known_endpoints:
            try:
                agent_info = await self._discover_agent(endpoint)
                if agent_info:
                    discovered_agents.append(agent_info)
                    discovery_results.append({
                        "endpoint": endpoint,
                        "status": "success",
                        "agent_id": agent_info.agent_id
                    })
                else:
                    discovery_results.append({
                        "endpoint": endpoint,
                        "status": "no_response",
                        "error": "No A2A agent found"
                    })
            except Exception as e:
                discovery_results.append({
                    "endpoint": endpoint,
                    "status": "error",
                    "error": str(e)
                })
                logger.warning(f"⚠️ Failed to discover agent at {endpoint}: {e}")
        
        # Update registry and capability index
        for agent in discovered_agents:
            self.agent_registry[agent.agent_id] = agent
            self._update_capability_index(agent)
        
        logger.info(f"✅ Discovered {len(discovered_agents)} active A2A agents")
        
        return {
            "service_id": self.service_id,
            "discovery_timestamp": datetime.now().isoformat(),
            "total_discovered": len(discovered_agents),
            "active_agents": [asdict(agent) for agent in discovered_agents],
            "discovery_details": discovery_results,
            "capability_summary": self._generate_capability_summary(),
            "ecosystem_health": self._assess_ecosystem_health(discovered_agents)
        }
    
    async def find_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find agents that have a specific capability"""
        logger.info(f"🎯 Finding agents with capability: {capability}")
        
        matching_agents = []
        
        for agent_id, agent_info in self.agent_registry.items():
            if capability in agent_info.capabilities:
                # Test agent availability
                is_available = await self._check_agent_availability(agent_info.base_url)
                
                matching_agents.append({
                    "agent_id": agent_info.agent_id,
                    "name": agent_info.name,
                    "base_url": agent_info.base_url,
                    "capabilities": agent_info.capabilities,
                    "endpoints": agent_info.endpoints,
                    "available": is_available,
                    "last_seen": agent_info.last_seen.isoformat(),
                    "response_time_ms": agent_info.response_time_ms
                })
        
        logger.info(f"✅ Found {len(matching_agents)} agents with {capability} capability")
        return matching_agents
    
    async def coordinate_agents(self, coordination_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate multiple agents for a complex task"""
        task_type = coordination_request.get('task_type', 'general_assistance')
        requirements = coordination_request.get('requirements', {})
        preferred_agents = coordination_request.get('preferred_agents', [])
        
        logger.info(f"🤝 Coordinating agents for task: {task_type}")
        
        # Determine required capabilities
        required_capabilities = self._determine_required_capabilities(task_type, requirements)
        
        # Find suitable agents
        coordination_plan = {}
        
        for capability in required_capabilities:
            suitable_agents = await self.find_agents_by_capability(capability)
            available_agents = [agent for agent in suitable_agents if agent['available']]
            
            if available_agents:
                # Select best agent (prefer specified ones, then by response time)
                best_agent = self._select_best_agent(available_agents, preferred_agents)
                coordination_plan[capability] = best_agent
            else:
                coordination_plan[capability] = None
        
        # Generate coordination strategy
        coordination_strategy = self._generate_coordination_strategy(coordination_plan, task_type, requirements)
        
        return {
            "service_id": self.service_id,
            "task_type": task_type,
            "coordination_timestamp": datetime.now().isoformat(),
            "required_capabilities": required_capabilities,
            "coordination_plan": coordination_plan,
            "coordination_strategy": coordination_strategy,
            "estimated_execution_time": self._estimate_execution_time(coordination_plan),
            "success_probability": self._calculate_success_probability(coordination_plan)
        }
    
    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get current status of the entire A2A ecosystem"""
        logger.info("📊 Generating ecosystem status report")
        
        # Refresh agent statuses
        await self._refresh_agent_statuses()
        
        active_agents = [agent for agent in self.agent_registry.values() if agent.status == "active"]
        inactive_agents = [agent for agent in self.agent_registry.values() if agent.status != "active"]
        
        # Capability coverage
        all_capabilities = set()
        for agent in active_agents:
            all_capabilities.update(agent.capabilities)
        
        return {
            "service_id": self.service_id,
            "ecosystem_timestamp": datetime.now().isoformat(),
            "total_registered_agents": len(self.agent_registry),
            "active_agents": len(active_agents),
            "inactive_agents": len(inactive_agents),
            "agent_details": {
                "active": [asdict(agent) for agent in active_agents],
                "inactive": [asdict(agent) for agent in inactive_agents]
            },
            "capability_coverage": {
                "total_capabilities": len(all_capabilities),
                "available_capabilities": list(all_capabilities),
                "capability_distribution": self._get_capability_distribution()
            },
            "ecosystem_health_score": self._calculate_ecosystem_health_score(),
            "coordination_readiness": self._assess_coordination_readiness(),
            "recommendations": self._generate_ecosystem_recommendations()
        }
    
    async def test_agent_communication(self, source_agent_id: str, target_agent_id: str) -> Dict[str, Any]:
        """Test communication between two agents"""
        logger.info(f"🔗 Testing communication: {source_agent_id} -> {target_agent_id}")
        
        if target_agent_id not in self.agent_registry:
            return {
                "success": False,
                "error": f"Target agent {target_agent_id} not found in registry"
            }
        
        target_agent = self.agent_registry[target_agent_id]
        
        try:
            # Test basic connectivity
            start_time = datetime.now()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{target_agent.base_url}/.well-known/agent")
                response.raise_for_status()
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "source_agent_id": source_agent_id,
                "target_agent_id": target_agent_id,
                "target_agent_name": target_agent.name,
                "communication_test": "passed",
                "response_time_ms": response_time,
                "target_capabilities": target_agent.capabilities,
                "available_endpoints": target_agent.endpoints,
                "test_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "source_agent_id": source_agent_id,
                "target_agent_id": target_agent_id,
                "error": f"Communication failed: {str(e)}",
                "test_timestamp": datetime.now().isoformat()
            }
    
    # Helper methods
    
    async def _discover_agent(self, endpoint: str) -> Optional[AgentInfo]:
        """Discover a single agent at the given endpoint"""
        try:
            start_time = datetime.now()
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{endpoint}/.well-known/agent")
                response.raise_for_status()
                
                response_time = (datetime.now() - start_time).total_seconds() * 1000
                agent_data = response.json()
                
                agent_info = AgentInfo(
                    agent_id=agent_data.get('agent_id', 'unknown'),
                    name=agent_data.get('name', 'Unknown Agent'),
                    version=agent_data.get('version', '1.0.0'),
                    base_url=endpoint,
                    capabilities=agent_data.get('capabilities', []),
                    endpoints=agent_data.get('endpoints', {}),
                    last_seen=datetime.now(),
                    status="active",
                    response_time_ms=response_time
                )
                
                logger.info(f"✅ Discovered agent: {agent_info.name} ({agent_info.agent_id}) at {endpoint}")
                return agent_info
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to discover agent at {endpoint}: {e}")
            return None
    
    async def _check_agent_availability(self, base_url: str) -> bool:
        """Check if an agent is currently available"""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{base_url}/")
                return response.status_code == 200
        except:
            return False
    
    def _update_capability_index(self, agent: AgentInfo):
        """Update the capability index with agent information"""
        for capability in agent.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            if agent.agent_id not in self.capability_index[capability]:
                self.capability_index[capability].append(agent.agent_id)
    
    def _generate_capability_summary(self) -> Dict[str, List[str]]:
        """Generate a summary of capabilities and which agents provide them"""
        return {
            capability: agent_ids.copy() 
            for capability, agent_ids in self.capability_index.items()
        }
    
    def _assess_ecosystem_health(self, discovered_agents: List[AgentInfo]) -> Dict[str, Any]:
        """Assess the overall health of the A2A ecosystem"""
        total_expected = len(self.known_endpoints)
        total_discovered = len(discovered_agents)
        
        health_score = (total_discovered / total_expected) * 100 if total_expected > 0 else 0
        
        # Check for essential capabilities
        essential_capabilities = ['flight_search', 'hotel_search', 'activity_search', 'itinerary_generation']
        covered_essential = sum(1 for cap in essential_capabilities if cap in self.capability_index)
        
        return {
            "overall_health_score": round(health_score, 1),
            "agents_discovered": f"{total_discovered}/{total_expected}",
            "essential_capabilities_covered": f"{covered_essential}/{len(essential_capabilities)}",
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "critical",
            "redundancy_level": self._calculate_redundancy_level()
        }
    
    def _determine_required_capabilities(self, task_type: str, requirements: Dict[str, Any]) -> List[str]:
        """Determine what capabilities are needed for a task"""
        capability_maps = {
            "comprehensive_trip_planning": [
                "flight_search", "hotel_search", "activity_search", "itinerary_generation"
            ],
            "budget_optimization": [
                "budget_negotiation", "price_optimization", "cost_analysis"
            ],
            "disruption_handling": [
                "disruption_handling", "alternative_planning", "real_time_updates"
            ],
            "itinerary_generation": [
                "itinerary_generation", "schedule_optimization", "ai_recommendations"
            ]
        }
        
        return capability_maps.get(task_type, ["general_travel_assistance"])
    
    def _select_best_agent(self, available_agents: List[Dict], preferred_agents: List[str]) -> Dict[str, Any]:
        """Select the best agent for a task"""
        # Prefer specified agents
        for agent in available_agents:
            if agent['agent_id'] in preferred_agents:
                return agent
        
        # Otherwise, select by response time
        return min(available_agents, key=lambda x: x.get('response_time_ms', 1000))
    
    def _generate_coordination_strategy(self, coordination_plan: Dict[str, Any], 
                                     task_type: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a strategy for coordinating the selected agents"""
        return {
            "execution_order": self._determine_execution_order(coordination_plan, task_type),
            "communication_pattern": "sequential_with_feedback",
            "data_sharing_approach": "centralized_through_orchestrator",
            "error_handling": "graceful_degradation_with_alternatives",
            "timeout_strategy": "progressive_timeout_with_fallback",
            "success_criteria": self._define_success_criteria(task_type, requirements)
        }
    
    def _estimate_execution_time(self, coordination_plan: Dict[str, Any]) -> str:
        """Estimate how long the coordinated task will take"""
        base_times = {
            "flight_search": 3000,  # 3 seconds
            "hotel_search": 2500,   # 2.5 seconds
            "activity_search": 2000, # 2 seconds
            "itinerary_generation": 5000  # 5 seconds
        }
        
        total_time_ms = sum(base_times.get(cap, 1000) for cap in coordination_plan.keys())
        return f"{total_time_ms / 1000:.1f}s"
    
    def _calculate_success_probability(self, coordination_plan: Dict[str, Any]) -> float:
        """Calculate probability of successful task completion"""
        # Base probability per agent (assuming 95% reliability)
        agent_reliability = 0.95
        active_agents = sum(1 for agent in coordination_plan.values() if agent is not None)
        
        if active_agents == 0:
            return 0.0
        
        # Overall probability decreases with more agents involved
        overall_probability = agent_reliability ** active_agents
        return round(overall_probability, 3)
    
    async def _refresh_agent_statuses(self):
        """Refresh the status of all registered agents"""
        for agent_id, agent_info in self.agent_registry.items():
            is_available = await self._check_agent_availability(agent_info.base_url)
            agent_info.status = "active" if is_available else "inactive"
            if is_available:
                agent_info.last_seen = datetime.now()
    
    def _get_capability_distribution(self) -> Dict[str, int]:
        """Get distribution of capabilities across agents"""
        return {
            capability: len(agent_ids)
            for capability, agent_ids in self.capability_index.items()
        }
    
    def _calculate_ecosystem_health_score(self) -> float:
        """Calculate overall ecosystem health score"""
        active_count = sum(1 for agent in self.agent_registry.values() if agent.status == "active")
        total_count = len(self.agent_registry)
        
        if total_count == 0:
            return 0.0
        
        return round((active_count / total_count) * 100, 1)
    
    def _assess_coordination_readiness(self) -> Dict[str, Any]:
        """Assess readiness for agent coordination"""
        essential_agents = ["flight-booking-agent", "hotel-booking-agent", "activity-planning-agent"]
        active_essential = sum(1 for agent_id in essential_agents 
                              if agent_id in self.agent_registry and 
                              self.agent_registry[agent_id].status == "active")
        
        return {
            "essential_agents_active": f"{active_essential}/{len(essential_agents)}",
            "coordination_ready": active_essential >= 2,
            "full_capability": active_essential == len(essential_agents),
            "missing_agents": [agent_id for agent_id in essential_agents 
                              if agent_id not in self.agent_registry or 
                              self.agent_registry[agent_id].status != "active"]
        }
    
    def _generate_ecosystem_recommendations(self) -> List[str]:
        """Generate recommendations for ecosystem improvement"""
        recommendations = []
        
        active_count = sum(1 for agent in self.agent_registry.values() if agent.status == "active")
        
        if active_count < 3:
            recommendations.append("Consider starting more agents for better redundancy")
        
        if "budget_negotiation" not in self.capability_index:
            recommendations.append("Add budget negotiation capabilities for cost optimization")
        
        if len(self.capability_index) < 8:
            recommendations.append("Expand capability coverage for more comprehensive trip planning")
        
        return recommendations
    
    def _calculate_redundancy_level(self) -> str:
        """Calculate redundancy level in the ecosystem"""
        redundant_capabilities = sum(1 for agents in self.capability_index.values() if len(agents) > 1)
        total_capabilities = len(self.capability_index)
        
        if total_capabilities == 0:
            return "none"
        
        redundancy_ratio = redundant_capabilities / total_capabilities
        
        if redundancy_ratio >= 0.7:
            return "high"
        elif redundancy_ratio >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _determine_execution_order(self, coordination_plan: Dict[str, Any], task_type: str) -> List[str]:
        """Determine optimal execution order for capabilities"""
        order_maps = {
            "comprehensive_trip_planning": ["flight_search", "hotel_search", "activity_search", "itinerary_generation"],
            "budget_optimization": ["budget_analysis", "price_optimization", "budget_negotiation"],
            "disruption_handling": ["disruption_detection", "alternative_planning", "rebooking"]
        }
        
        default_order = list(coordination_plan.keys())
        return order_maps.get(task_type, default_order)
    
    def _define_success_criteria(self, task_type: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Define success criteria for the task"""
        return {
            "all_agents_respond": True,
            "within_budget": requirements.get('budget_constraint', True),
            "meets_timeline": requirements.get('timeline_constraint', True),
            "quality_threshold": requirements.get('quality_threshold', 0.8)
        }


def create_discovery_service_app() -> FastAPI:
    """Create FastAPI app for Agent Discovery Service"""
    
    app = FastAPI(
        title="AgentDiscoveryService",
        description="A2A Protocol service discovery and coordination hub",
        version="1.0.0"
    )
    
    # Add CORS for cross-agent communication
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize discovery service
    discovery_service = AgentDiscoveryService()
    
    @app.get("/")
    async def root():
        return {
            "service": discovery_service.name,
            "service_id": discovery_service.service_id,
            "version": discovery_service.version,
            "status": "active",
            "description": "A2A Protocol Agent Discovery and Coordination Service",
            "endpoints": {
                "discover": "/api/discover-agents",
                "find_capability": "/api/find-agents/{capability}",
                "coordinate": "/api/coordinate-agents",
                "ecosystem_status": "/api/ecosystem-status",
                "test_communication": "/api/test-communication"
            }
        }
    
    @app.get("/.well-known/agent")
    async def get_agent_card():
        """A2A Agent Card for the discovery service itself"""
        return {
            "name": discovery_service.name,
            "agent_id": discovery_service.service_id,
            "version": discovery_service.version,
            "description": "Central service for A2A agent discovery, capability matching, and coordination",
            "capabilities": [
                "agent_discovery",
                "capability_matching",
                "coordination_planning", 
                "ecosystem_monitoring",
                "communication_testing"
            ],
            "endpoints": {
                "discover_all_agents": "/api/discover-agents",
                "find_agents_by_capability": "/api/find-agents/{capability}",
                "coordinate_agents": "/api/coordinate-agents",
                "get_ecosystem_status": "/api/ecosystem-status",
                "test_agent_communication": "/api/test-communication"
            },
            "communication_protocols": ["HTTP", "JSON"],
            "service_type": "discovery_and_coordination",
            "manages_ecosystem": True
        }
    
    @app.post("/api/discover-agents")
    async def discover_agents():
        """Discover all available A2A agents in the ecosystem"""
        result = await discovery_service.discover_all_agents()
        return {
            "success": True,
            "discovery_result": result
        }
    
    @app.get("/api/find-agents/{capability}")
    async def find_agents_by_capability(capability: str):
        """Find agents that provide a specific capability"""
        agents = await discovery_service.find_agents_by_capability(capability)
        return {
            "success": True,
            "capability": capability,
            "matching_agents": agents,
            "total_found": len(agents)
        }
    
    @app.post("/api/coordinate-agents")
    async def coordinate_agents(coordination_request: Dict[str, Any]):
        """Coordinate multiple agents for a complex task"""
        result = await discovery_service.coordinate_agents(coordination_request)
        return {
            "success": True,
            "coordination_result": result
        }
    
    @app.get("/api/ecosystem-status")
    async def get_ecosystem_status():
        """Get comprehensive status of the A2A ecosystem"""
        status = await discovery_service.get_ecosystem_status()
        return {
            "success": True,
            "ecosystem_status": status
        }
    
    @app.post("/api/test-communication")
    async def test_communication(request_data: Dict[str, Any]):
        """Test communication between two agents"""
        source_agent_id = request_data.get('source_agent_id', 'discovery-service')
        target_agent_id = request_data.get('target_agent_id')
        
        if not target_agent_id:
            raise HTTPException(status_code=400, detail="target_agent_id is required")
        
        result = await discovery_service.test_agent_communication(source_agent_id, target_agent_id)
        return result
    
    return app


if __name__ == "__main__":
    app = create_discovery_service_app()
    
    print("🔍 AgentDiscoveryService starting...")
    print("🤖 A2A Protocol ecosystem discovery and coordination")
    print("🔗 Agent capability matching and communication testing")
    print("📊 Real-time ecosystem health monitoring")
    print("🤝 Multi-agent coordination planning")
    print("📍 Available at: http://localhost:8005")
    print("🤖 Service info: http://localhost:8005/.well-known/agent")
    print("🔗 API endpoints: http://localhost:8005/api/")
    
    uvicorn.run(app, host="0.0.0.0", port=8005)
