"""
Diperion Python SDK

A clean, developer-friendly Python SDK for the Diperion Semantic Engine.
Build powerful semantic applications without worrying about the underlying
complexity of HTTP requests or data parsing.
"""

__version__ = "0.1.0"
__author__ = "Diperion Team"
__email__ = "contact@diperion.com"

# ===================
# BACKWARD COMPATIBILITY - Current API continues to work
# ===================
from .semantic_engine.client import DiperionClient, connect
from .semantic_engine.agent_proxy import AgentProxy, get_agent_proxy

# Import data models for backward compatibility
from .semantic_engine.models import (
    Business, Node, Edge, QueryResult, BusinessCapabilities,
    RelationshipInfo, GraphVisualization, CommandResult
)

# Import exceptions for backward compatibility
from .common.exceptions import (
    DiperionError, ConnectionError, AuthenticationError,
    BusinessNotFoundError, NodeNotFoundError, InvalidQueryError,
    ValidationError, ServerError
)

# Import business intelligence for backward compatibility
from .semantic_engine.business_intelligence import BusinessIntelligence

# ===================
# FORWARD COMPATIBILITY - New modular API
# ===================

# Import service modules
from . import semantic_engine
from . import common

# Convenience aliases
from .semantic_engine import SemanticClient, SemanticEngine

# Service factory functions
def semantic_engine_client(url: str = "http://localhost:8080", **kwargs) -> 'SemanticClient':
    """Create a semantic engine client."""
    return semantic_engine.connect(url, **kwargs)

# Aliases for convenience
engine = semantic_engine
knowledge = semantic_engine  # Alternative semantic name
graph = semantic_engine      # Technical name

# ===================
# PUBLIC API
# ===================
__all__ = [
    # === BACKWARD COMPATIBLE API ===
    # Core client (current API continues working)
    "DiperionClient", "connect", 
    
    # Agent proxy (ultra-confidential)
    "AgentProxy", "get_agent_proxy",
    
    # Data models
    "Business", "Node", "Edge", "QueryResult", "BusinessCapabilities",
    "RelationshipInfo", "GraphVisualization", "CommandResult",
    
    # Exceptions
    "DiperionError", "ConnectionError", "AuthenticationError",
    "BusinessNotFoundError", "NodeNotFoundError", "InvalidQueryError",
    "ValidationError", "ServerError",
    
    # Business Intelligence
    "BusinessIntelligence",
    
    # === NEW MODULAR API ===
    # Service modules
    "semantic_engine", "common",
    
    # Semantic engine aliases
    "SemanticClient", "SemanticEngine",
    
    # Factory functions
    "semantic_engine_client",
    
    # Convenience aliases
    "engine", "knowledge", "graph",
    
    # Meta
    "__version__",
    "__author__",
    "__email__"
]

# ===================
# CONVENIENCE FUNCTIONS
# ===================

def quickstart():
    """Print a comprehensive quick start guide for all services."""
    print(f"""
🚀 Diperion SDK v{__version__} Quick Start
=========================================

=== CURRENT API (Backward Compatible) ===
1. Basic usage:
   >>> import diperion
   >>> client = diperion.connect("http://localhost:8080")
   >>> businesses = client.list_businesses()

2. Agent operations (ultra-confidential):
   >>> proxy = diperion.get_agent_proxy()

=== NEW MODULAR API ===
3. Semantic Engine (specific import):
   >>> from diperion import semantic_engine
   >>> client = semantic_engine.connect("http://localhost:8080")

4. Alternative semantic engine imports:
   >>> from diperion import engine, knowledge, graph
   >>> client = engine.connect("http://localhost:8080")
   >>> client = knowledge.connect("http://localhost:8080")
   >>> client = graph.connect("http://localhost:8080")

5. Factory function:
   >>> client = diperion.semantic_engine_client("http://localhost:8080")

=== FUTURE SERVICES (Coming Soon) ===
   >>> from diperion import analytics, recommendations, search
   >>> analytics_client = analytics.connect("http://analytics:9090")
   >>> ml_client = recommendations.connect("http://ml:7070")

For detailed documentation: https://docs.diperion.com/python-sdk
    """)

def connect_local(port: int = 8080) -> DiperionClient:
    """Connect to a local Diperion server (backward compatible)."""
    return connect(f"http://localhost:{port}")

def connect_cloud(url: str) -> DiperionClient:
    """Connect to a cloud Diperion server (backward compatible)."""
    return connect(url) 

# ===================
# MIGRATION HELPERS
# ===================

def migrate_to_semantic_engine():
    """Print migration guide for new semantic engine API."""
    print("""
🔄 Migration Guide: Current API → Semantic Engine API
====================================================

OLD (still works):
   import diperion
   client = diperion.connect("http://localhost:8080")

NEW (recommended for semantic operations):
   from diperion import semantic_engine
   client = semantic_engine.connect("http://localhost:8080")

ALTERNATIVE (convenient aliases):
   from diperion import engine  # Short alias
   from diperion import knowledge  # Semantic alias
   from diperion import graph  # Technical alias

All APIs provide the same functionality!
Your existing code continues to work unchanged.
    """)

# Auto-detect and suggest optimal import
def suggest_import(service_type: str = "semantic"):
    """Suggest the best import method for a service."""
    suggestions = {
        "semantic": [
            "from diperion import semantic_engine",
            "from diperion import engine",
            "from diperion import knowledge"
        ],
        "analytics": [
            "from diperion import analytics  # Coming soon"
        ],
        "ml": [
            "from diperion import recommendations  # Coming soon"
        ]
    }
    
    print(f"💡 Suggested imports for {service_type}:")
    for suggestion in suggestions.get(service_type, ["Service not available yet"]):
        print(f"   {suggestion}")

# Show available services
def list_services():
    """List all available Diperion services."""
    print(f"""
📋 Available Diperion Services (v{__version__})
==============================================

✅ SEMANTIC ENGINE (Available)
   - Semantic graph operations
   - Business intelligence
   - Natural language queries
   - Agent operations (ultra-confidential)
   
   Import: from diperion import semantic_engine

🔄 ANALYTICS (Coming Soon)
   - Business analytics dashboards
   - Performance metrics
   - Usage insights
   
🔄 RECOMMENDATIONS (Coming Soon)
   - ML-powered recommendations
   - Semantic similarity
   - Predictive modeling
   
🔄 SEARCH (Coming Soon)
   - Advanced semantic search
   - Full-text indexing
   - Faceted search
    """)

# Development helpers
def dev_info():
    """Show development information."""
    print(f"""
🛠️  Diperion SDK Development Info
===============================

Version: {__version__}
Author: {__author__}
Contact: {__email__}

Architecture: Modular, scalable service-oriented design
Backward Compatibility: 100% maintained
Forward Compatibility: Ready for new services

Current Services: 1 (Semantic Engine)
Planned Services: 3+ (Analytics, ML, Search)
    """)

# Export development helpers
__all__.extend([
    "quickstart", "connect_local", "connect_cloud",
    "migrate_to_semantic_engine", "suggest_import", 
    "list_services", "dev_info"
]) 