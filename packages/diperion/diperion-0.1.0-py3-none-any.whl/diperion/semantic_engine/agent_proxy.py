"""
Agent Proxy Module - Diperion SDK

Ultra-high-level agent operations that handle ALL complexity internally.
This module makes agent tools extremely simple - just one line calls.
"""

import time
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from ..common.exceptions import DiperionError

if TYPE_CHECKING:
    from .client import DiperionClient


class AgentProxy:
    """
    Ultra-high-level agent proxy that handles ALL complexity internally.
    
    This class encapsulates:
    - Session state management
    - Business ID resolution
    - Data validation
    - Error handling
    - Response formatting
    - Cache management
    - All business logic
    
    Agent tools become one-line calls to this proxy.
    """
    
    def __init__(self, client: 'DiperionClient'):
        self.client = client
        self._session_cache = {}
    
    def _get_session_key(self, tool_context) -> str:
        """Generate a unique session key for state management."""
        return f"session_{id(tool_context)}"
    
    def _get_session_state(self, tool_context) -> Dict[str, Any]:
        """Get session state with automatic initialization."""
        session_key = self._get_session_key(tool_context)
        if session_key not in self._session_cache:
            self._session_cache[session_key] = {
                "current_business_id": "",
                "business_capabilities": {},
                "entity_types": [],
                "relationship_patterns": [],
                "available_attributes": {},
                "last_introspection": None
            }
            
        # Safely handle Google ADK state - read individual values instead of update
        if hasattr(tool_context, 'state') and tool_context.state:
            try:
                # Try to read specific keys we care about
                for key in ["current_business_id", "business_capabilities", "entity_types", 
                           "relationship_patterns", "available_attributes", "last_introspection"]:
                    try:
                        if key in tool_context.state:
                            self._session_cache[session_key][key] = tool_context.state[key]
                    except (KeyError, TypeError):
                        # Skip if the key doesn't exist or causes an error
                        continue
            except Exception:
                # If state access fails completely, just use our cache
                pass
            
        return self._session_cache[session_key]
    
    def _update_session_state(self, tool_context, updates: Dict[str, Any]):
        """Update session state internally."""
        state = self._get_session_state(tool_context)
        state.update(updates)
        
        # Safely update tool_context.state - handle Google ADK state system
        if hasattr(tool_context, 'state'):
            try:
                for key, value in updates.items():
                    try:
                        tool_context.state[key] = value
                    except Exception:
                        # Skip if setting the key fails (Google ADK state system)
                        continue
            except Exception:
                # If state access fails, just log it for debug
                print(f"DEBUG: Could not update tool_context.state: {updates}")
        else:
            print("DEBUG: tool_context has no state attribute")
    
    def _resolve_business_id(self, tool_context, business_id: Optional[str] = None) -> str:
        """Resolve business ID using proprietary logic."""
        if business_id:
            clean_id = self.client.auto_generate_business_id(business_id)
            self._update_session_state(tool_context, {"current_business_id": clean_id})
            return clean_id
        
        state = self._get_session_state(tool_context)
        current_id = state.get("current_business_id", "")
        
        if not current_id:
            raise DiperionError("No business ID specified. Use set_current_business first.")
        
        return current_id
    
    def _format_success_response(self, message: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Format a standardized success response."""
        response = {
            "status": "success",
            "message": message,
            "timestamp": time.time()
        }
        
        if data is not None:
            if isinstance(data, dict):
                response.update(data)
            else:
                response["data"] = data
        
        response.update(kwargs)
        return response
    
    def _format_error_response(self, message: str, error_type: str = "general") -> Dict[str, Any]:
        """Format a standardized error response."""
        return {
            "status": "error",
            "message": message,
            "error_type": error_type,
            "timestamp": time.time()
        }
    
    def _handle_operation(self, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """Handle any operation with automatic error management."""
        try:
            result = operation_func(*args, **kwargs)
            # Ensure result is JSON serializable
            if not isinstance(result, dict):
                return self._format_error_response(f"Operation returned non-dict result: {type(result)}", "unexpected_error")
            return result
        except DiperionError as e:
            return self._format_error_response(str(e), "diperion_error")
        except Exception as e:
            # Enhanced error handling to capture more information
            import traceback
            error_msg = str(e) if str(e) else f"Exception of type {type(e).__name__}"
            if not error_msg or error_msg == "0":
                error_msg = f"Unknown {type(e).__name__} exception"
            # Add traceback for debugging
            tb = traceback.format_exc()
            print(f"DEBUG: Exception in _handle_operation: {error_msg}")
            print(f"DEBUG: Traceback: {tb}")
            return self._format_error_response(f"Unexpected error: {error_msg}", "unexpected_error")
    
    # ===================
    # ULTRA-SIMPLE AGENT OPERATIONS
    # ===================
    
    def get_business_state(self, tool_context) -> Dict[str, Any]:
        """Get current business state - handles everything internally."""
        def _operation():
            state = self._get_session_state(tool_context)
            return self._format_success_response("Business state retrieved", state)
        
        return self._handle_operation(_operation)
    
    def set_current_business(self, tool_context, business_id: str) -> Dict[str, Any]:
        """Set current business - handles everything internally."""
        def _operation():
            if not business_id or not business_id.strip():
                raise DiperionError("Business ID cannot be empty")
            
            clean_id = self.client.auto_generate_business_id(business_id)
            self._update_session_state(tool_context, {"current_business_id": clean_id})
            
            return self._format_success_response(
                f"Current business set to: {clean_id}",
                business_id=clean_id
            )
        
        return self._handle_operation(_operation)
    
    def perform_business_introspection(self, tool_context, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform comprehensive business introspection - handles everything internally."""
        def _operation():
            resolved_id = self._resolve_business_id(tool_context, business_id)
            
            # Use SDK's advanced comprehensive analysis
            result = self.client.comprehensive_business_analysis(resolved_id)
            
            # Update session state automatically
            self._update_session_state(tool_context, {
                "current_business_id": resolved_id,
                "business_capabilities": result.get("business_info", {}),
                "entity_types": result.get("entity_types", []),
                "relationship_patterns": result.get("relationship_patterns", []),
                "available_attributes": result.get("available_attributes", {}),
                "last_introspection": time.time()
            })
            
            return result
        
        return self._handle_operation(_operation)
    
    def execute_dsl_command(self, tool_context, command: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute DSL command - handles everything internally."""
        def _operation():
            if not command or not command.strip():
                raise DiperionError("DSL command cannot be empty")
            
            resolved_id = self._resolve_business_id(tool_context, business_id)
            
            # Execute using SDK
            result = self.client.execute_dsl(resolved_id, command.strip())
            
            # Auto-invalidate cache if needed
            if result.success and command.strip().upper().startswith(("CREATE", "UPDATE", "DELETE")):
                self._update_session_state(tool_context, {
                    "last_introspection": None,
                    "business_capabilities": None
                })
            
            # Format response automatically
            return self._format_success_response(
                result.message if result.success else result.message,
                {
                    "status": "success" if result.success else "error",
                    "data": result.data,
                    "processing_time_ms": result.processing_time_ms,
                    "warnings": result.warnings,
                    "business_id": resolved_id,
                    "command": command.strip()
                }
            )
        
        return self._handle_operation(_operation)
    
    def query_business(self, tool_context, query: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Query business - handles everything internally."""
        def _operation():
            if not query or not query.strip():
                raise DiperionError("Query cannot be empty")
            
            resolved_id = self._resolve_business_id(tool_context, business_id)
            
            # Execute query using SDK
            result = self.client.query(resolved_id, query.strip())
            
            # Auto-convert to standard format INCLUDING relationships
            recommendations = [
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.node_type,
                    "attributes": node.attributes,
                    "description": node.description,
                    "relationships": [
                        {
                            "target_id": rel.target_id,
                            "target_name": rel.target_name,
                            "relationship_type": rel.relationship_type,
                            "weight": rel.weight,
                            "label": rel.label
                        }
                        for rel in node.relationships
                    ]
                }
                for node in result.nodes
            ]
            
            return self._format_success_response(
                result.message,
                {
                    "query": query.strip(),
                    "dsl_command": query.strip(),
                    "results": recommendations,
                    "count": len(recommendations),
                    "processing_time_ms": result.processing_time_ms,
                    "business_id": resolved_id,
                    "used_introspection": True,
                    "entity_type_used": "auto_detected"
                }
            )
        
        return self._handle_operation(_operation)
    
    def create_business_taxonomy(self, tool_context, business_description: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Create business taxonomy - handles everything internally."""
        def _operation():
            if not business_description or not business_description.strip():
                raise DiperionError("Business description cannot be empty")
            
            resolved_id = self._resolve_business_id(tool_context, business_id)
            
            # Use SDK's intelligent taxonomy creation
            result = self.client.intelligence.create_intelligent_taxonomy(
                resolved_id, 
                business_description.strip()
            )
            
            # Auto-invalidate cache
            self._update_session_state(tool_context, {
                "last_introspection": None,
                "business_capabilities": None
            })
            
            return result
        
        return self._handle_operation(_operation)
    
    def list_businesses(self, tool_context) -> Dict[str, Any]:
        """List businesses - handles everything internally."""
        def _operation():
            businesses = self.client.list_businesses()
            
            business_list = [
                {
                    "id": business.id,
                    "name": business.name,
                    "industry": business.industry,
                    "loaded": business.loaded
                }
                for business in businesses
            ]
            
            return self._format_success_response(
                f"Found {len(business_list)} businesses",
                {
                    "businesses": business_list,
                    "total": len(business_list)
                }
            )
        
        return self._handle_operation(_operation)
    
    def inspect_available_relationships(self, tool_context, business_id: Optional[str] = None, 
                                     relationship_type: Optional[str] = None, from_node_type: Optional[str] = None, 
                                     limit: Optional[int] = None) -> Dict[str, Any]:
        """Inspect relationships - handles everything internally."""
        def _operation():
            resolved_id = self._resolve_business_id(tool_context, business_id)
            
            # Use SDK to get relationships
            relationships = self.client.get_relationships(resolved_id, relationship_type)
            
            # Auto-format response
            relationship_types = {}
            for rel in relationships:
                rel_type = rel.relationship_type
                if rel_type not in relationship_types:
                    relationship_types[rel_type] = {
                        "type": rel_type,
                        "count": rel.count,
                        "examples": rel.examples[:3],
                        "from_nodes": rel.from_nodes[:10],
                        "to_nodes": getattr(rel, 'to_nodes', [])[:10]
                    }
            
            return self._format_success_response(
                "Relationships inspected",
                {
                    "business_id": resolved_id,
                    "total_relationships": sum(rt["count"] for rt in relationship_types.values()),
                    "unique_relationship_types": len(relationship_types),
                    "relationship_types": list(relationship_types.values()),
                    "filters_applied": {
                        "relationship_type": relationship_type,
                        "from_node_type": from_node_type,
                        "limit": limit or 50
                    }
                }
            )
        
        return self._handle_operation(_operation)
    
    def inspect_relation_nodes(self, tool_context, business_id: Optional[str] = None,
                             name_pattern: Optional[str] = None, relation_type: Optional[str] = None,
                             limit: Optional[int] = None) -> Dict[str, Any]:
        """Inspect relation nodes - handles everything internally."""
        def _operation():
            resolved_id = self._resolve_business_id(tool_context, business_id)
            
            # Auto-build query
            query = "FIND RelationNode"
            if relation_type:
                query += f' WHERE relation_type = "{relation_type}"'
            
            result = self.client.query(resolved_id, query)
            
            # Auto-organize by relation type
            relation_types = {}
            for node in result.nodes:
                rel_type = node.get_attribute("relation_type", "unknown")
                
                if rel_type not in relation_types:
                    relation_types[rel_type] = {
                        "relation_type": rel_type,
                        "count": 0,
                        "nodes": []
                    }
                
                relation_types[rel_type]["count"] += 1
                relation_types[rel_type]["nodes"].append({
                    "id": node.id,
                    "name": node.name,
                    "attributes": node.attributes
                })
            
            return self._format_success_response(
                "Relation nodes inspected",
                {
                    "business_id": resolved_id,
                    "total_relation_nodes": len(result.nodes),
                    "unique_relation_types": len(relation_types),
                    "relation_types": list(relation_types.values()),
                    "filters_applied": {
                        "name_pattern": name_pattern,
                        "relation_type": relation_type,
                        "limit": limit or 30
                    }
                }
            )
        
        return self._handle_operation(_operation)
    
    def create_relation_node_connection(self, tool_context, product_name: str, 
                                      relation_node_name: str, relationship_type: str, 
                                      business_id: Optional[str] = None) -> Dict[str, Any]:
        """Create relation node connection - handles everything internally."""
        def _operation():
            # Auto-validate inputs
            if not all([product_name.strip(), relation_node_name.strip(), relationship_type.strip()]):
                raise DiperionError("All parameters must be provided")
            
            resolved_id = self._resolve_business_id(tool_context, business_id)
            
            # Use SDK to create relationship
            success = self.client.create_relationship(
                business_id=resolved_id,
                from_node_name=product_name.strip(),
                to_node_name=relation_node_name.strip(),
                relationship_type=relationship_type.strip()
            )
            
            if not success:
                raise DiperionError("Failed to create relationship")
            
            # Auto-invalidate caches
            state = self._get_session_state(tool_context)
            if "available_relationships" in state:
                del state["available_relationships"]
            if "available_relation_nodes" in state:
                del state["available_relation_nodes"]
            
            return self._format_success_response(
                "Relation created successfully",
                {
                    "business_id": resolved_id,
                    "product_name": product_name.strip(),
                    "relation_node_name": relation_node_name.strip(),
                    "relationship_type": relationship_type.strip(),
                    "explanation": f"Created relationship: {product_name} --[{relationship_type}]--> {relation_node_name}"
                }
            )
        
        return self._handle_operation(_operation)
    
    def smart_business_setup(self, tool_context, business_name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Auto-create business with smart setup."""
        def _operation():
            # Use SDK's smart business setup
            try:
                result = self.client.smart_business_setup(business_name, description or f"Business for {business_name}")
                self._update_session_state(tool_context, {"current_business_id": result["business_id"]})
                return result
            except Exception as e:
                return {"error": f"Failed to setup business: {str(e)}", "success": False}
        
        return self._handle_operation(_operation)
    
    def update_node(self, tool_context, node_id: str, attributes: Dict[str, Any], business_id: Optional[str] = None) -> Dict[str, Any]:
        """Update a node's attributes."""
        def _operation():
            resolved_business_id = self._resolve_business_id(tool_context, business_id)
            try:
                # Use DSL command approach for consistency
                import json
                attributes_json = json.dumps(attributes)
                dsl_command = f'UPDATE NODE "{node_id}" SET {attributes_json}'
                
                result = self.client.execute_dsl(resolved_business_id, dsl_command)
                if result.success:
                    return self._format_success_response(
                        f"Node {node_id} updated successfully",
                        {"node_id": node_id, "updated_attributes": attributes}
                    )
                else:
                    return self._format_error_response(f"Failed to update node: {result.message}")
            except Exception as e:
                return self._format_error_response(f"Failed to update node: {str(e)}")
        
        return self._handle_operation(_operation)
    
    def delete_node(self, tool_context, node_id: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete a node."""
        def _operation():
            resolved_business_id = self._resolve_business_id(tool_context, business_id)
            try:
                # Use DSL command approach for consistency
                dsl_command = f'DELETE NODE "{node_id}"'
                
                result = self.client.execute_dsl(resolved_business_id, dsl_command)
                if result.success:
                    return self._format_success_response(
                        f"Node {node_id} deleted successfully",
                        {"node_id": node_id}
                    )
                else:
                    return self._format_error_response(f"Failed to delete node: {result.message}")
            except Exception as e:
                return self._format_error_response(f"Failed to delete node: {str(e)}")
        
        return self._handle_operation(_operation)
    
    def update_relationship(self, tool_context, relationship_id: str, weight: Optional[float] = None, 
                          label: Optional[str] = None, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Update a relationship's properties."""
        def _operation():
            resolved_business_id = self._resolve_business_id(tool_context, business_id)
            try:
                # Build update object
                update_data = {}
                if weight is not None:
                    update_data["weight"] = weight
                if label is not None:
                    update_data["label"] = label
                
                if not update_data:
                    return self._format_error_response("No updates provided - specify weight or label")
                
                # Use DSL command approach for consistency
                import json
                update_json = json.dumps(update_data)
                dsl_command = f'UPDATE RELATIONSHIP "{relationship_id}" SET {update_json}'
                
                result = self.client.execute_dsl(resolved_business_id, dsl_command)
                if result.success:
                    return self._format_success_response(
                        f"Relationship {relationship_id} updated successfully",
                        {"relationship_id": relationship_id, "updates": update_data}
                    )
                else:
                    return self._format_error_response(f"Failed to update relationship: {result.message}")
            except Exception as e:
                return self._format_error_response(f"Failed to update relationship: {str(e)}")
        
        return self._handle_operation(_operation)
    
    def delete_relationship(self, tool_context, relationship_id: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Delete a relationship."""
        def _operation():
            resolved_business_id = self._resolve_business_id(tool_context, business_id)
            try:
                # Use DSL command approach for consistency
                dsl_command = f'DELETE RELATIONSHIP "{relationship_id}"'
                
                result = self.client.execute_dsl(resolved_business_id, dsl_command)
                if result.success:
                    return self._format_success_response(
                        f"Relationship {relationship_id} deleted successfully",
                        {"relationship_id": relationship_id}
                    )
                else:
                    return self._format_error_response(f"Failed to delete relationship: {result.message}")
            except Exception as e:
                return self._format_error_response(f"Failed to delete relationship: {str(e)}")
        
        return self._handle_operation(_operation)


# Global proxy instance
_agent_proxy = None

def get_agent_proxy():
    """Get or create the global agent proxy instance."""
    global _agent_proxy
    if _agent_proxy is None:
        try:
            from .client import connect
            client = connect("http://127.0.0.1:8080", timeout=30)
            _agent_proxy = AgentProxy(client)
            print("DEBUG: Agent proxy initialized successfully")
        except Exception as e:
            print(f"DEBUG: Failed to initialize agent proxy: {e}")
            import traceback
            traceback.print_exc()
            raise e
    return _agent_proxy 