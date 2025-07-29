"""
CrewAI Integration for MetricLLM
================================

Provides comprehensive integration with CrewAI for monitoring agent responses,
team performance, and collecting detailed metrics from multi-agent workflows.
"""

import os
import asyncio
import time
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from metricllm import monitor
from metricllm.utils.metric_logging import get_logger

try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    from langchain.schema import BaseMessage
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False


class AgentRole(Enum):
    """Enumeration of common CrewAI agent roles."""
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"
    EXPERT = "expert"
    PLANNER = "planner"
    EXECUTOR = "executor"
    VALIDATOR = "validator"
    CUSTOM = "custom"


@dataclass
class AgentResponse:
    """Structured representation of an agent's response."""
    agent_id: str
    agent_name: str
    agent_role: str
    task_id: str
    task_description: str
    response_content: str
    execution_time: float
    timestamp: str
    status: str
    metadata: Dict[str, Any]


@dataclass
class CrewResponse:
    """Structured representation of a crew's complete response."""
    crew_id: str
    crew_name: str
    agents_involved: List[str]
    total_execution_time: float
    final_result: str
    agent_responses: List[AgentResponse]
    timestamp: str
    status: str
    metadata: Dict[str, Any]


class CrewAIMonitor:
    """
    Enhanced monitoring wrapper for CrewAI that collects detailed responses
    and metrics from agents and crews.
    """
    
    def __init__(self, enable_monitoring: bool = True):
        self.logger = get_logger(__name__)
        self.enable_monitoring = enable_monitoring
        self.agent_responses: List[AgentResponse] = []
        self.crew_responses: List[CrewResponse] = []
        
        if not CREWAI_AVAILABLE:
            raise ImportError("CrewAI package required. Install with: pip install crewai")
    
    def monitor_agent(self, 
                     agent_name: str,
                     agent_role: str = "custom",
                     track_performance: bool = True,
                     collect_metadata: bool = True) -> Callable:
        """
        Decorator to monitor individual agent responses.
        
        Args:
            agent_name: Name of the agent
            agent_role: Role of the agent
            track_performance: Whether to track performance metrics
            collect_metadata: Whether to collect additional metadata
        """
        def decorator(func: Callable) -> Callable:
            @monitor(
                provider="crewai",
                model="agent",
                track_tokens=True,
                track_cost=True,
                evaluate=True,
                responsible_ai_check=True
            )
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if self.enable_monitoring:
                        # Extract response content
                        response_content = self._extract_response_content(result)
                        
                        # Create agent response record
                        agent_response = AgentResponse(
                            agent_id=f"{agent_name}_{int(time.time())}",
                            agent_name=agent_name,
                            agent_role=agent_role,
                            task_id=kwargs.get("task_id", "unknown"),
                            task_description=kwargs.get("task_description", ""),
                            response_content=response_content,
                            execution_time=execution_time,
                            timestamp=datetime.now().isoformat(),
                            status="success",
                            metadata={
                                "track_performance": track_performance,
                                "collect_metadata": collect_metadata,
                                "function_name": func.__name__,
                                "args_count": len(args),
                                "kwargs_keys": list(kwargs.keys())
                            }
                        )
                        
                        self.agent_responses.append(agent_response)
                        self.logger.info(f"Agent response collected: {agent_name}")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    if self.enable_monitoring:
                        agent_response = AgentResponse(
                            agent_id=f"{agent_name}_{int(time.time())}",
                            agent_name=agent_name,
                            agent_role=agent_role,
                            task_id=kwargs.get("task_id", "unknown"),
                            task_description=kwargs.get("task_description", ""),
                            response_content=str(e),
                            execution_time=execution_time,
                            timestamp=datetime.now().isoformat(),
                            status="error",
                            metadata={
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "function_name": func.__name__
                            }
                        )
                        
                        self.agent_responses.append(agent_response)
                        self.logger.error(f"Agent error collected: {agent_name} - {str(e)}")
                    
                    raise
                    
            return wrapper
        return decorator
    
    def monitor_crew(self,
                    crew_name: str,
                    track_team_performance: bool = True,
                    collect_agent_interactions: bool = True) -> Callable:
        """
        Decorator to monitor crew execution and collect all agent responses.
        
        Args:
            crew_name: Name of the crew
            track_team_performance: Whether to track team-level performance
            collect_agent_interactions: Whether to collect agent interaction data
        """
        def decorator(func: Callable) -> Callable:
            @monitor(
                provider="crewai",
                model="crew",
                track_tokens=True,
                track_cost=True,
                evaluate=True,
                responsible_ai_check=True
            )
            def wrapper(*args, **kwargs):
                start_time = time.time()
                crew_agent_responses = []
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    if self.enable_monitoring:
                        # Extract final result
                        final_result = self._extract_response_content(result)
                        
                        # Get agent responses from this execution
                        # This would need to be coordinated with the actual CrewAI execution
                        agents_involved = kwargs.get("agents", [])
                        
                        # Create crew response record
                        crew_response = CrewResponse(
                            crew_id=f"{crew_name}_{int(time.time())}",
                            crew_name=crew_name,
                            agents_involved=agents_involved,
                            total_execution_time=execution_time,
                            final_result=final_result,
                            agent_responses=crew_agent_responses,
                            timestamp=datetime.now().isoformat(),
                            status="success",
                            metadata={
                                "track_team_performance": track_team_performance,
                                "collect_agent_interactions": collect_agent_interactions,
                                "function_name": func.__name__,
                                "agents_count": len(agents_involved)
                            }
                        )
                        
                        self.crew_responses.append(crew_response)
                        self.logger.info(f"Crew response collected: {crew_name}")
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    if self.enable_monitoring:
                        crew_response = CrewResponse(
                            crew_id=f"{crew_name}_{int(time.time())}",
                            crew_name=crew_name,
                            agents_involved=kwargs.get("agents", []),
                            total_execution_time=execution_time,
                            final_result=str(e),
                            agent_responses=crew_agent_responses,
                            timestamp=datetime.now().isoformat(),
                            status="error",
                            metadata={
                                "error_type": type(e).__name__,
                                "error_message": str(e),
                                "function_name": func.__name__
                            }
                        )
                        
                        self.crew_responses.append(crew_response)
                        self.logger.error(f"Crew error collected: {crew_name} - {str(e)}")
                    
                    raise
                    
            return wrapper
        return decorator
    
    def _extract_response_content(self, result: Any) -> str:
        """Extract response content from various result types."""
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            return str(result)
        elif hasattr(result, 'content'):
            return str(result.content)
        elif hasattr(result, 'result'):
            return str(result.result)
        elif hasattr(result, '__dict__'):
            return str(result.__dict__)
        else:
            return str(result)
    
    def get_agent_responses(self, 
                           agent_name: Optional[str] = None,
                           agent_role: Optional[str] = None,
                           status: Optional[str] = None) -> List[AgentResponse]:
        """Get filtered agent responses."""
        responses = self.agent_responses
        
        if agent_name:
            responses = [r for r in responses if r.agent_name == agent_name]
        if agent_role:
            responses = [r for r in responses if r.agent_role == agent_role]
        if status:
            responses = [r for r in responses if r.status == status]
            
        return responses
    
    def get_crew_responses(self,
                          crew_name: Optional[str] = None,
                          status: Optional[str] = None) -> List[CrewResponse]:
        """Get filtered crew responses."""
        responses = self.crew_responses
        
        if crew_name:
            responses = [r for r in responses if r.crew_name == crew_name]
        if status:
            responses = [r for r in responses if r.status == status]
            
        return responses
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get aggregated performance metrics."""
        if not self.agent_responses and not self.crew_responses:
            return {}
        
        metrics = {
            "total_agents": len(self.agent_responses),
            "total_crews": len(self.crew_responses),
            "successful_agents": len([r for r in self.agent_responses if r.status == "success"]),
            "successful_crews": len([r for r in self.crew_responses if r.status == "success"]),
            "average_agent_execution_time": 0.0,
            "average_crew_execution_time": 0.0,
            "agent_roles_distribution": {},
            "crew_performance": {}
        }
        
        # Calculate average execution times
        if self.agent_responses:
            successful_agents = [r for r in self.agent_responses if r.status == "success"]
            if successful_agents:
                metrics["average_agent_execution_time"] = sum(r.execution_time for r in successful_agents) / len(successful_agents)
        
        if self.crew_responses:
            successful_crews = [r for r in self.crew_responses if r.status == "success"]
            if successful_crews:
                metrics["average_crew_execution_time"] = sum(r.total_execution_time for r in successful_crews) / len(successful_crews)
        
        # Calculate role distribution
        for response in self.agent_responses:
            role = response.agent_role
            metrics["agent_roles_distribution"][role] = metrics["agent_roles_distribution"].get(role, 0) + 1
        
        # Calculate crew performance
        for response in self.crew_responses:
            crew_name = response.crew_name
            if crew_name not in metrics["crew_performance"]:
                metrics["crew_performance"][crew_name] = {
                    "total_executions": 0,
                    "successful_executions": 0,
                    "average_execution_time": 0.0
                }
            
            metrics["crew_performance"][crew_name]["total_executions"] += 1
            if response.status == "success":
                metrics["crew_performance"][crew_name]["successful_executions"] += 1
        
        # Calculate average execution time per crew
        for crew_name, data in metrics["crew_performance"].items():
            crew_responses = [r for r in self.crew_responses if r.crew_name == crew_name and r.status == "success"]
            if crew_responses:
                data["average_execution_time"] = sum(r.total_execution_time for r in crew_responses) / len(crew_responses)
        
        return metrics
    
    def export_responses(self, format: str = "json") -> str:
        """Export all responses in the specified format."""
        if format.lower() == "json":
            data = {
                "agent_responses": [asdict(r) for r in self.agent_responses],
                "crew_responses": [asdict(r) for r in self.crew_responses],
                "performance_metrics": self.get_performance_metrics(),
                "export_timestamp": datetime.now().isoformat()
            }
            import json
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")


class CrewAIIntegration:
    """
    Main integration class that provides easy-to-use methods for creating
    monitored CrewAI agents and crews.
    """
    
    def __init__(self, enable_monitoring: bool = True):
        self.monitor = CrewAIMonitor(enable_monitoring=enable_monitoring)
        self.logger = get_logger(__name__)
        
        if not CREWAI_AVAILABLE:
            raise ImportError("CrewAI package required. Install with: pip install crewai")
    
    def create_monitored_agent(self,
                              name: str,
                              role: str,
                              goal: str,
                              backstory: str = "",
                              verbose: bool = True,
                              allow_delegation: bool = True,
                              **kwargs) -> Agent:
        """
        Create a CrewAI agent with monitoring capabilities.
        
        Args:
            name: Agent name
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            verbose: Whether to enable verbose output
            allow_delegation: Whether to allow task delegation
            **kwargs: Additional agent parameters
        """
        agent = Agent(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            verbose=verbose,
            allow_delegation=allow_delegation,
            **kwargs
        )
        
        # Wrap the agent's execution method with monitoring
        original_execute = agent.execute
        
        @self.monitor.monitor_agent(
            agent_name=name,
            agent_role=role,
            track_performance=True,
            collect_metadata=True
        )
        def monitored_execute(*args, **kwargs):
            return original_execute(*args, **kwargs)
        
        agent.execute = monitored_execute
        return agent
    
    def create_monitored_crew(self,
                             agents: List[Agent],
                             tasks: List[Task],
                             name: str = "Monitored Crew",
                             process: Process = Process.sequential,
                             verbose: bool = True,
                             **kwargs) -> Crew:
        """
        Create a CrewAI crew with monitoring capabilities.
        
        Args:
            agents: List of agents
            tasks: List of tasks
            name: Crew name
            process: Process type (sequential, hierarchical, etc.)
            verbose: Whether to enable verbose output
            **kwargs: Additional crew parameters
        """
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=process,
            verbose=verbose,
            **kwargs
        )
        
        # Wrap the crew's kickoff method with monitoring
        original_kickoff = crew.kickoff
        
        @self.monitor.monitor_crew(
            crew_name=name,
            track_team_performance=True,
            collect_agent_interactions=True
        )
        def monitored_kickoff(*args, **kwargs):
            return original_kickoff(*args, **kwargs)
        
        crew.kickoff = monitored_kickoff
        return crew
    
    def get_all_responses(self) -> Dict[str, Any]:
        """Get all collected responses and metrics."""
        return {
            "agent_responses": self.monitor.agent_responses,
            "crew_responses": self.monitor.crew_responses,
            "performance_metrics": self.monitor.get_performance_metrics()
        }
    
    def get_agent_responses(self, **kwargs) -> List[AgentResponse]:
        """Get filtered agent responses."""
        return self.monitor.get_agent_responses(**kwargs)
    
    def get_crew_responses(self, **kwargs) -> List[CrewResponse]:
        """Get filtered crew responses."""
        return self.monitor.get_crew_responses(**kwargs)
    
    def export_data(self, format: str = "json") -> str:
        """Export all monitoring data."""
        return self.monitor.export_responses(format)


# Convenience functions for quick integration
def create_monitored_agent(name: str, role: str, goal: str, **kwargs) -> Agent:
    """Quick function to create a monitored agent."""
    integration = CrewAIIntegration()
    return integration.create_monitored_agent(name, role, goal, **kwargs)


def create_monitored_crew(agents: List[Agent], tasks: List[Task], **kwargs) -> Crew:
    """Quick function to create a monitored crew."""
    integration = CrewAIIntegration()
    return integration.create_monitored_crew(agents, tasks, **kwargs)


def get_crewai_responses() -> Dict[str, Any]:
    """Quick function to get all CrewAI responses."""
    integration = CrewAIIntegration()
    return integration.get_all_responses() 