"""
AI Agents functionality for the Cognify SDK.

This module handles AI agent operations including agent discovery,
specialized queries, and agent orchestration.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .models import (
    AgentInfo,
    AgentQueryRequest,
    AgentResponse,
    AgentStatus,
    AgentStats,
)
from ..exceptions import CognifyValidationError, CognifyAPIError, CognifyNotFoundError

if TYPE_CHECKING:
    from .rag_module import RAGModule


logger = logging.getLogger(__name__)


class AgentsModule:
    """
    Handles AI agent operations and orchestration.
    """
    
    def __init__(self, rag_module: "RAGModule") -> None:
        """
        Initialize agents module.
        
        Args:
            rag_module: Parent RAG module instance
        """
        self.rag = rag_module
        self.client = rag_module.client
    
    # Agent Discovery
    
    async def list_agents(
        self,
        status: Optional[AgentStatus] = None,
        specialization: Optional[str] = None,
        include_metrics: bool = False
    ) -> List[AgentInfo]:
        """
        List available AI agents.
        
        Args:
            status: Filter by agent status (optional)
            specialization: Filter by specialization (optional)
            include_metrics: Include performance metrics (default: False)
            
        Returns:
            List of AgentInfo objects
            
        Raises:
            CognifyAPIError: If request fails
        """
        params = {
            'include_metrics': include_metrics
        }
        
        if status:
            params['status'] = status.value
        if specialization:
            params['specialization'] = specialization
        
        logger.debug(f"Listing agents with filters: {params}")
        
        response = await self.client.http.arequest(
            'GET',
            '/rag/agents',
            params=params
        )
        
        agents_data = response.get('data', [])
        agents = [AgentInfo(**agent) for agent in agents_data]
        
        logger.info(f"Found {len(agents)} agents")
        return agents
    
    def list_agents_sync(
        self,
        status: Optional[AgentStatus] = None,
        specialization: Optional[str] = None,
        include_metrics: bool = False
    ) -> List[AgentInfo]:
        """
        List available AI agents synchronously.
        
        Args:
            status: Filter by agent status (optional)
            specialization: Filter by specialization (optional)
            include_metrics: Include performance metrics (default: False)
            
        Returns:
            List of AgentInfo objects
        """
        params = {
            'include_metrics': include_metrics
        }
        
        if status:
            params['status'] = status.value
        if specialization:
            params['specialization'] = specialization
        
        response = self.client.http.request(
            'GET',
            '/rag/agents',
            params=params
        )
        
        agents_data = response.get('data', [])
        return [AgentInfo(**agent) for agent in agents_data]
    
    async def get_agent(self, agent_id: str) -> AgentInfo:
        """
        Get information about a specific agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            AgentInfo object
            
        Raises:
            CognifyNotFoundError: If agent not found
            CognifyAPIError: If request fails
        """
        logger.debug(f"Getting agent info: {agent_id}")
        
        try:
            response = await self.client.http.arequest(
                'GET',
                f'/rag/agents/{agent_id}'
            )
            
            agent_data = response.get('data', {})
            agent = AgentInfo(**agent_data)
            
            logger.info(f"Retrieved agent: {agent.name} ({agent.status.value})")
            return agent
            
        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Agent not found: {agent_id}",
                    resource_type="agent",
                    resource_id=agent_id
                )
            raise
    
    def get_agent_sync(self, agent_id: str) -> AgentInfo:
        """
        Get agent information synchronously.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            AgentInfo object
        """
        try:
            response = self.client.http.request(
                'GET',
                f'/rag/agents/{agent_id}'
            )
            
            agent_data = response.get('data', {})
            return AgentInfo(**agent_data)
            
        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Agent not found: {agent_id}",
                    resource_type="agent",
                    resource_id=agent_id
                )
            raise
    
    # Agent Queries
    
    async def query_agent(
        self,
        query: str,
        agent_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AgentResponse:
        """
        Submit a query to a specific agent or auto-select best agent.
        
        Args:
            query: Query for the agent
            agent_id: Specific agent ID (auto-select if None)
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            context: Additional context (optional)
            temperature: Response creativity (default: 0.7)
            max_tokens: Maximum response tokens (default: 1000)
            
        Returns:
            AgentResponse with agent's answer
            
        Raises:
            CognifyValidationError: If query is invalid
            CognifyAPIError: If agent query fails
        """
        request = AgentQueryRequest(
            query=query,
            agent_id=agent_id,
            collection_id=collection_id,
            workspace_id=workspace_id,
            context=context,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"Submitting agent query: {query[:50]}...")
        
        response = await self.client.http.arequest(
            'POST',
            '/rag/agents/query',
            json=request.dict(exclude_none=True)
        )
        
        # Parse response
        data = response.get('data', {})
        
        agent_response = AgentResponse(
            query_id=data.get('query_id', f"agent_{int(datetime.now().timestamp())}"),
            agent_id=data.get('agent_id', 'unknown'),
            agent_name=data.get('agent_name', 'Unknown Agent'),
            query=query,
            response=data.get('response', ''),
            confidence=data.get('confidence', 0.0),
            reasoning=data.get('reasoning'),
            citations=[],  # Would parse citations if provided
            processing_time_ms=data.get('processing_time_ms', 0.0),
            tokens_used=data.get('tokens_used', 0),
            created_at=datetime.now()
        )
        
        logger.info(f"Agent query completed: {agent_response.query_id}")
        return agent_response
    
    def query_agent_sync(
        self,
        query: str,
        agent_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AgentResponse:
        """
        Submit a query to an agent synchronously.
        
        Args:
            query: Query for the agent
            agent_id: Specific agent ID (auto-select if None)
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            context: Additional context (optional)
            temperature: Response creativity (default: 0.7)
            max_tokens: Maximum response tokens (default: 1000)
            
        Returns:
            AgentResponse with agent's answer
        """
        request = AgentQueryRequest(
            query=query,
            agent_id=agent_id,
            collection_id=collection_id,
            workspace_id=workspace_id,
            context=context,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        response = self.client.http.request(
            'POST',
            '/rag/agents/query',
            json=request.dict(exclude_none=True)
        )
        
        # Parse response
        data = response.get('data', {})
        
        return AgentResponse(
            query_id=data.get('query_id', f"agent_{int(datetime.now().timestamp())}"),
            agent_id=data.get('agent_id', 'unknown'),
            agent_name=data.get('agent_name', 'Unknown Agent'),
            query=query,
            response=data.get('response', ''),
            confidence=data.get('confidence', 0.0),
            reasoning=data.get('reasoning'),
            citations=[],
            processing_time_ms=data.get('processing_time_ms', 0.0),
            tokens_used=data.get('tokens_used', 0),
            created_at=datetime.now()
        )
    
    # Agent Selection
    
    async def recommend_agent(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> List[AgentInfo]:
        """
        Get agent recommendations for a query.
        
        Args:
            query: Query to analyze
            collection_id: Collection context (optional)
            workspace_id: Workspace context (optional)
            
        Returns:
            List of recommended agents (sorted by suitability)
            
        Raises:
            CognifyValidationError: If query is invalid
            CognifyAPIError: If recommendation fails
        """
        if not query or not query.strip():
            raise CognifyValidationError("Query cannot be empty")
        
        params = {
            'query': query.strip()
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        logger.debug(f"Getting agent recommendations for: {query[:50]}...")
        
        response = await self.client.http.arequest(
            'GET',
            '/rag/agents/recommend',
            params=params
        )
        
        agents_data = response.get('data', [])
        recommended_agents = [AgentInfo(**agent) for agent in agents_data]
        
        logger.info(f"Found {len(recommended_agents)} recommended agents")
        return recommended_agents
    
    def recommend_agent_sync(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> List[AgentInfo]:
        """
        Get agent recommendations synchronously.
        
        Args:
            query: Query to analyze
            collection_id: Collection context (optional)
            workspace_id: Workspace context (optional)
            
        Returns:
            List of recommended agents
        """
        if not query or not query.strip():
            raise CognifyValidationError("Query cannot be empty")
        
        params = {
            'query': query.strip()
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        response = self.client.http.request(
            'GET',
            '/rag/agents/recommend',
            params=params
        )
        
        agents_data = response.get('data', [])
        return [AgentInfo(**agent) for agent in agents_data]
    
    # Agent Statistics
    
    async def get_agent_stats(self) -> AgentStats:
        """
        Get agent service statistics.
        
        Returns:
            AgentStats with service metrics
            
        Raises:
            CognifyAPIError: If stats request fails
        """
        logger.debug("Getting agent service statistics")
        
        response = await self.client.http.arequest(
            'GET',
            '/rag/agents/stats'
        )
        
        data = response.get('data', {})
        
        return AgentStats(
            total_agents=data.get('total_agents', 0),
            active_agents=data.get('active_agents', 0),
            total_queries=data.get('total_queries', 0),
            avg_response_time_ms=data.get('avg_response_time_ms', 0.0),
            queries_by_agent=data.get('queries_by_agent', {}),
            agent_performance=data.get('agent_performance', {}),
            specialization_usage=data.get('specialization_usage', {}),
            last_updated=datetime.now()
        )
    
    def get_agent_stats_sync(self) -> AgentStats:
        """
        Get agent service statistics synchronously.
        
        Returns:
            AgentStats with service metrics
        """
        response = self.client.http.request(
            'GET',
            '/rag/agents/stats'
        )
        
        data = response.get('data', {})
        
        return AgentStats(
            total_agents=data.get('total_agents', 0),
            active_agents=data.get('active_agents', 0),
            total_queries=data.get('total_queries', 0),
            avg_response_time_ms=data.get('avg_response_time_ms', 0.0),
            queries_by_agent=data.get('queries_by_agent', {}),
            agent_performance=data.get('agent_performance', {}),
            specialization_usage=data.get('specialization_usage', {}),
            last_updated=datetime.now()
        )
