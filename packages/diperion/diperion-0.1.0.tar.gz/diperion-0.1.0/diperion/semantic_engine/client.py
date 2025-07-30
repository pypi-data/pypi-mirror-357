"""
Diperion SDK Client

Clean, developer-friendly API for the Diperion Semantic Engine.
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional, Union
from .models import (
    Business, Node, Edge, QueryResult, BusinessCapabilities, 
    RelationshipInfo, GraphVisualization, CommandResult, Relationship
)
from ..common.exceptions import (
    DiperionError, ConnectionError, BusinessNotFoundError, 
    NodeNotFoundError, InvalidQueryError, ServerError
)
from .business_intelligence import BusinessIntelligence
from .config import get_config


class DiperionClient:
    """
    Main client for interacting with the Diperion Semantic Engine.
    
    This client provides a clean, Pythonic API that abstracts away
    the complexity of HTTP requests and raw data handling.
    
    URL Configuration Priority:
    1. Explicit base_url parameter
    2. DIPERION_API_URL environment variable
    3. DIPERION_BASE_URL environment variable  
    4. Environment-based configuration
    5. Default localhost for development
    """
    
    def __init__(self, base_url: str = None, timeout: int = None, environment: str = None):
        """
        Initialize the Diperion client.
        
        Args:
            base_url: Base URL of the Diperion server (highest priority)
            timeout: Request timeout in seconds (uses config default if None)
            environment: Environment name (development, production, staging)
        """
        config = get_config()
        
        self.base_url = config.get_base_url(base_url, environment).rstrip('/')
        self.timeout = timeout or config.get_timeout()
        self.session = requests.Session()
        self.session.timeout = self.timeout
        
        # Initialize business intelligence module
        self._business_intelligence = None
        
        # Test connection
        self._test_connection()
    
    @property
    def intelligence(self) -> BusinessIntelligence:
        """Access to advanced business intelligence operations."""
        if self._business_intelligence is None:
            self._business_intelligence = BusinessIntelligence(self)
        return self._business_intelligence
    
    def _test_connection(self) -> None:
        """Test connection to the server."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot connect to Diperion server at {self.base_url}: {e}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request with error handling."""
        url = f"{self.base_url}/api/v1{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Lost connection to Diperion server")
        except requests.exceptions.Timeout:
            raise ConnectionError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise BusinessNotFoundError("Business not found")
            else:
                raise ServerError(f"Server error: {e.response.text}", e.response.status_code)
        except Exception as e:
            raise DiperionError(f"Unexpected error: {str(e)}")
    
    # ===================
    # BUSINESS MANAGEMENT
    # ===================
    
    def list_businesses(self) -> List[Business]:
        """
        Get all available businesses.
        
        Returns:
            List of Business objects
        """
        data = self._make_request("GET", "/businesses")
        
        businesses = []
        for business_data in data.get("businesses", []):
            business = Business(
                id=business_data["id"],
                name=business_data["name"],
                industry=business_data.get("industry", "general"),
                loaded=business_data.get("loaded", True)
            )
            businesses.append(business)
        
        return businesses
    
    def get_business(self, business_id: str) -> BusinessCapabilities:
        """
        Get detailed information about a business.
        
        Args:
            business_id: ID of the business
            
        Returns:
            BusinessCapabilities object with detailed info
        """
        data = self._make_request("GET", f"/businesses/{business_id}/capabilities")
        
        # Calculate total entities from entity_types
        entity_types = data.get("entity_types", [])
        total_entities = sum(et.get("count", 0) for et in entity_types)
        
        return BusinessCapabilities(
            business_id=data["business_id"],
            name=data["name"],
            industry=data["industry"],
            entity_types=entity_types,
            total_entities=total_entities,
            example_commands=data.get("example_commands", []),
            query_patterns=data.get("query_patterns", [])
        )
    
    def create_business(self, business_id: str, description: str = None) -> Business:
        """
        Create a new business with base entities.
        
        Args:
            business_id: ID for the new business
            description: Optional description of the business
            
        Returns:
            Business object
        """
        # Clean business ID
        clean_id = business_id.lower().replace(" ", "_")
        
        # Create base entities by making a simple query (this triggers auto-creation)
        try:
            self.query(clean_id, "LIST Product")
        except:
            # Business might not exist yet, that's okay
            pass
        
        # Get business info
        business_data = self.get_business(clean_id)
        
        return Business(
            id=business_data.business_id,
            name=business_data.name,
            industry=business_data.industry,
            loaded=True
        )
    
    # ===================
    # NODE MANAGEMENT
    # ===================
    
    def create_node(self, business_id: str, name: str, node_type: str = "Product", 
                   attributes: Dict[str, Any] = None, description: str = None) -> Node:
        """
        Create a new semantic node.
        
        Args:
            business_id: ID of the business
            name: Name of the node
            node_type: Type of the node (Product, Client, etc.)
            attributes: Optional attributes dictionary
            description: Optional description
            
        Returns:
            Node object
        """
        node_data = {
            "name": name,
            "type": node_type,
            "attributes": attributes or {}
        }
        
        if description:
            node_data["description"] = description
        
        command = f"CREATE NODE {json.dumps(node_data)}"
        result = self._execute_command(business_id, command)
        
        if not result.success:
            raise DiperionError(f"Failed to create node: {result.message}")
        
        # Handle different data formats from server
        node_id = "generated"
        if isinstance(result.data, dict):
            node_id = result.data.get("id", "generated")
        elif isinstance(result.data, list) and result.data:
            # If data is a list, try to get ID from first item
            first_item = result.data[0]
            if isinstance(first_item, dict):
                node_id = first_item.get("id", "generated")
        
        # Return a constructed Node object
        return Node(
            id=node_id,
            name=name,
            node_type=node_type,
            attributes=attributes or {},
            description=description
        )
    
    def find_nodes(self, business_id: str, node_type: str = None, 
                  conditions: Dict[str, Any] = None) -> List[Node]:
        """
        Find nodes matching criteria.
        
        Args:
            business_id: ID of the business
            node_type: Type of nodes to find (optional)
            conditions: Conditions to match (optional)
            
        Returns:
            List of Node objects
        """
        if node_type:
            query = f"FIND {node_type}"
        else:
            query = "FIND Entity"
        
        if conditions:
            condition_parts = []
            for key, value in conditions.items():
                if isinstance(value, str):
                    condition_parts.append(f'{key} = "{value}"')
                else:
                    condition_parts.append(f'{key} = {value}')
            
            if condition_parts:
                query += " WHERE " + " AND ".join(condition_parts)
        
        return self.query(business_id, query).nodes
    
    # ===================
    # QUERYING
    # ===================
    
    def query(self, business_id: str, query: str) -> QueryResult:
        """
        Execute a semantic query.
        
        Args:
            business_id: ID of the business
            query: Natural language or DSL query
            
        Returns:
            QueryResult with matching nodes
        """
        data = self._make_request("POST", f"/businesses/{business_id}/query", 
                                json={"query": query})
        
        nodes = []
        for node_data in data.get("results", []):
            # Process relationships
            relationships = []
            for rel_data in node_data.get("relationships", []):
                relationship = Relationship(
                    target_id=rel_data.get("target_id", ""),
                    target_name=rel_data.get("target_name", ""),
                    relationship_type=rel_data.get("relationship_type", ""),
                    weight=rel_data.get("weight", 1.0),
                    label=rel_data.get("label")
                )
                relationships.append(relationship)
            
            node = Node(
                id=node_data.get("id", ""),
                name=node_data.get("name", ""),
                node_type=node_data.get("item_type", "Unknown"),
                attributes=node_data.get("attributes", {}),
                description=node_data.get("description"),
                relationships=relationships
            )
            nodes.append(node)
        
        return QueryResult(
            nodes=nodes,
            message=data.get("message", ""),
            query=query,
            processing_time_ms=data.get("processing_time_ms", 0),
            total_found=len(nodes)
        )
    
    def execute_dsl(self, business_id: str, command: str) -> CommandResult:
        """
        Execute a DSL command directly.
        
        Args:
            business_id: ID of the business
            command: DSL command to execute
            
        Returns:
            CommandResult with execution details
        """
        return self._execute_command(business_id, command)
    
    def _execute_command(self, business_id: str, command: str) -> CommandResult:
        """Internal method to execute DSL commands."""
        data = self._make_request("POST", f"/businesses/{business_id}/dsl", 
                                json={"command": command})
        
        return CommandResult(
            status=data.get("status", "unknown"),
            message=data.get("message", ""),
            data=data.get("data", {}),
            processing_time_ms=data.get("processing_time_ms", 0),
            warnings=data.get("warnings", [])
        )
    
    # ===================
    # RELATIONSHIPS
    # ===================
    
    def create_relationship(self, business_id: str, from_node_name: str, 
                          to_node_name: str, relationship_type: str, 
                          weight: float = 1.0) -> bool:
        """
        Create a relationship between two nodes.
        
        Args:
            business_id: ID of the business
            from_node_name: Name of the source node
            to_node_name: Name of the target node
            relationship_type: Type of relationship
            weight: Relationship weight (0.0 to 1.0)
            
        Returns:
            True if successful
        """
        data = self._make_request("POST", f"/businesses/{business_id}/relation-nodes", 
                                json={
                                    "product_name": from_node_name,
                                    "relation_type": relationship_type,
                                    "relationship_name": to_node_name
                                })
        
        return data.get("success") == True
    
    def get_relationships(self, business_id: str, relationship_type: str = None) -> List[RelationshipInfo]:
        """
        Get information about relationships in the business.
        
        Args:
            business_id: ID of the business
            relationship_type: Filter by relationship type (optional)
            
        Returns:
            List of RelationshipInfo objects
        """
        params = {}
        if relationship_type:
            params["relationship_type"] = relationship_type
        
        data = self._make_request("GET", f"/businesses/{business_id}/relationships", 
                                params=params)
        
        relationships = []
        for rel_data in data.get("relationship_types", []):
            relationship = RelationshipInfo(
                relationship_type=rel_data["type"],
                count=rel_data["count"],
                examples=rel_data.get("examples", []),
                from_nodes=rel_data.get("from_nodes", []),
                to_nodes=rel_data.get("to_nodes", [])
            )
            relationships.append(relationship)
        
        return relationships
    
    # ===================
    # VISUALIZATION
    # ===================
    
    def get_graph_visualization(self, business_id: str, max_nodes: int = 100, 
                              node_types: List[str] = None) -> GraphVisualization:
        """
        Get graph visualization data.
        
        Args:
            business_id: ID of the business
            max_nodes: Maximum number of nodes to return
            node_types: Filter by node types (optional)
            
        Returns:
            GraphVisualization object
        """
        request_data = {
            "max_nodes": max_nodes,
            "max_edges": max_nodes * 3,
            "node_types": node_types,
            "include_positions": False
        }
        
        data = self._make_request("POST", f"/businesses/{business_id}/graph/visualization", 
                                json=request_data)
        
        return GraphVisualization(
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            metadata=data.get("metadata", {}),
            processing_time_ms=data.get("processing_time_ms", 0)
        )
    
    # ===================
    # HIGH-LEVEL INTELLIGENCE METHODS
    # ===================
    
    def smart_business_setup(self, business_name: str, description: str = None) -> Dict[str, Any]:
        """
        Intelligently set up a business with auto-generated ID and base taxonomy.
        
        This method encapsulates proprietary business setup logic.
        
        Args:
            business_name: Human-readable business name
            description: Optional business description
            
        Returns:
            Setup results with business ID and created entities
        """
        # Use proprietary business ID generation
        business_id = self.intelligence.auto_generate_business_id(business_name)
        
        # Create business with intelligent taxonomy
        result = self.intelligence.create_intelligent_taxonomy(
            business_id, 
            description or f"Business: {business_name}"
        )
        
        return {
            **result,
            "business_name": business_name,
            "generated_business_id": business_id
        }
    
    def comprehensive_business_analysis(self, business_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive business analysis using proprietary algorithms.
        
        This method encapsulates advanced analysis logic that would be difficult
        to reverse-engineer from external code.
        
        Args:
            business_id: The business identifier
            
        Returns:
            Comprehensive business analysis with proprietary insights
        """
        return self.intelligence.perform_comprehensive_introspection(business_id)
    
    def auto_generate_business_id(self, business_name: str) -> str:
        """
        Generate a clean business ID from a business name using proprietary rules.
        
        Args:
            business_name: Human-readable business name
            
        Returns:
            Clean business ID
        """
        return self.intelligence.auto_generate_business_id(business_name)


# ===================
# CONVENIENCE FUNCTIONS
# ===================

def connect(base_url: str = None, timeout: int = None, environment: str = None) -> DiperionClient:
    """
    Create a new Diperion client connection.
    
    Args:
        base_url: Base URL of the Diperion server (highest priority)
        timeout: Request timeout in seconds (uses config default if None)
        environment: Environment name (development, production, staging)
        
    Returns:
        DiperionClient instance
    """
    return DiperionClient(base_url, timeout, environment) 