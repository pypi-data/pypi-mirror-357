"""
Diperion Semantic Engine - Advanced semantic infrastructure for business knowledge.

This module provides semantic graph operations, business intelligence,
and natural language querying capabilities.
"""

from .client import DiperionClient, connect
from .models import (
    Business, Node, Edge, QueryResult, BusinessCapabilities, 
    RelationshipInfo, GraphVisualization, CommandResult
)
from .business_intelligence import BusinessIntelligence
from .agent_proxy import AgentProxy, get_agent_proxy

# Convenience aliases
SemanticClient = DiperionClient
SemanticEngine = DiperionClient

__version__ = "1.0.0"

__all__ = [
    # Core client
    "DiperionClient",
    "SemanticClient", 
    "SemanticEngine",
    "connect",
    
    # Data models
    "Business",
    "Node",
    "Edge",
    "QueryResult",
    "BusinessCapabilities",
    "RelationshipInfo",
    "GraphVisualization",
    "CommandResult",
    
    # Advanced features
    "BusinessIntelligence",
    
    # Agent proxy (ultra-confidential)
    "AgentProxy",
    "get_agent_proxy",
    
    # Version
    "__version__"
]

# Quick start for semantic engine
def quickstart():
    """Print semantic engine quick start guide."""
    print("""
🧠 Diperion Semantic Engine Quick Start
======================================

1. Connect to semantic engine:
   >>> from diperion.semantic_engine import connect
   >>> client = connect("http://localhost:8080")

2. Create business knowledge:
   >>> business = client.create_business("my_store")
   >>> product = client.create_node("my_store", "iPhone 15", "Product")

3. Query semantically:
   >>> results = client.query("my_store", "Find all products")
   >>> print([node.name for node in results.nodes])

4. Business intelligence:
   >>> analysis = client.comprehensive_business_analysis("my_store")
   >>> print(f"Maturity: {analysis['business_maturity']}/10")

For agents (ultra-confidential):
   >>> from diperion.semantic_engine import get_agent_proxy
   >>> proxy = get_agent_proxy()
    """)


# Convenience function for local development
def connect_local(port: int = 8080) -> DiperionClient:
    """Connect to local semantic engine."""
    return connect(f"http://localhost:{port}") 