"""
Diperion SDK Data Models

Clean, developer-friendly data models for the Diperion Semantic Engine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class Business:
    """Represents a business in the semantic engine."""
    
    id: str
    name: str
    industry: str = "general"
    loaded: bool = True
    last_query: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"Business(id='{self.id}', name='{self.name}', industry='{self.industry}')"


@dataclass
class Relationship:
    """Represents a relationship from one node to another."""
    
    target_id: str
    target_name: str
    relationship_type: str
    weight: float = 1.0
    label: Optional[str] = None
    
    def __str__(self) -> str:
        return f"Relationship({self.relationship_type} -> {self.target_name}, weight={self.weight})"


@dataclass
class Node:
    """Represents a semantic node."""
    
    id: str
    name: str
    node_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    relationships: List[Relationship] = field(default_factory=list)
    
    def __str__(self) -> str:
        rel_count = len(self.relationships)
        return f"Node(id='{self.id}', name='{self.name}', type='{self.node_type}', relationships={rel_count})"
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get an attribute value with optional default."""
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Set an attribute value."""
        self.attributes[key] = value
    
    def get_relationships(self, relationship_type: Optional[str] = None) -> List[Relationship]:
        """Get relationships, optionally filtered by type."""
        if relationship_type is None:
            return self.relationships
        return [rel for rel in self.relationships if rel.relationship_type == relationship_type]
    
    def get_related_nodes(self, relationship_type: Optional[str] = None) -> List[str]:
        """Get names of nodes related through specified relationship type."""
        relationships = self.get_relationships(relationship_type)
        return [rel.target_name for rel in relationships]


@dataclass
class Edge:
    """Represents a relationship between nodes."""
    
    id: str
    from_node: str
    to_node: str
    edge_type: str
    weight: float = 1.0
    label: Optional[str] = None
    bidirectional: bool = False
    
    def __str__(self) -> str:
        direction = "<->" if self.bidirectional else "->"
        return f"Edge({self.from_node} {direction} {self.to_node}, type='{self.edge_type}')"


@dataclass
class QueryResult:
    """Result of a semantic query."""
    
    nodes: List[Node]
    message: str
    query: str
    processing_time_ms: int = 0
    total_found: int = 0
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def __iter__(self):
        return iter(self.nodes)
    
    def __getitem__(self, index):
        return self.nodes[index]
    
    def first(self) -> Optional[Node]:
        """Get the first result, if any."""
        return self.nodes[0] if self.nodes else None
    
    def names(self) -> List[str]:
        """Get list of node names."""
        return [node.name for node in self.nodes]


@dataclass
class BusinessCapabilities:
    """Business capabilities and metadata."""
    
    business_id: str
    name: str
    industry: str
    entity_types: List[Dict[str, Any]]
    total_entities: int = 0
    total_relationships: int = 0
    example_commands: List[str] = field(default_factory=list)
    query_patterns: List[str] = field(default_factory=list)
    
    def get_entity_types(self) -> List[str]:
        """Get list of entity type names."""
        return [et.get('name', 'Unknown') for et in self.entity_types]
    
    def get_entity_count(self, entity_type: str) -> int:
        """Get count for specific entity type."""
        for et in self.entity_types:
            if et.get('name') == entity_type:
                return et.get('count', 0)
        return 0


@dataclass
class RelationshipInfo:
    """Information about a relationship type."""
    
    relationship_type: str
    count: int
    examples: List[Dict[str, Any]] = field(default_factory=list)
    from_nodes: List[str] = field(default_factory=list)
    to_nodes: List[str] = field(default_factory=list)


@dataclass
class GraphVisualization:
    """Graph visualization data."""
    
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    processing_time_ms: int = 0
    
    def node_count(self) -> int:
        return len(self.nodes)
    
    def edge_count(self) -> int:
        return len(self.edges)
    
    def get_node_types(self) -> List[str]:
        """Get unique node types in the graph."""
        return list(set(node.get('node_type', 'Unknown') for node in self.nodes))


@dataclass
class CommandResult:
    """Result of a DSL command execution."""
    
    status: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: int = 0
    warnings: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Check if the command was successful."""
        return self.status.lower() == "success"
    
    def __bool__(self) -> bool:
        return self.success 


@dataclass
class UpdateNodeRequest:
    """Request to update a node's attributes."""
    
    node_id: str
    attributes: Dict[str, Any]
    business_id: Optional[str] = None


@dataclass
class DeleteNodeRequest:
    """Request to delete a node."""
    
    node_id: str
    business_id: Optional[str] = None


@dataclass
class UpdateRelationshipRequest:
    """Request to update a relationship."""
    
    relationship_id: str
    weight: Optional[float] = None
    label: Optional[str] = None
    business_id: Optional[str] = None


@dataclass
class DeleteRelationshipRequest:
    """Request to delete a relationship."""
    
    relationship_id: str
    business_id: Optional[str] = None 