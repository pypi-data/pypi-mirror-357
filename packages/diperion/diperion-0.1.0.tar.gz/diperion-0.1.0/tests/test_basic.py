"""
Basic tests for the Diperion SDK
"""

import pytest
from unittest.mock import Mock, patch
import diperion
from diperion.exceptions import ConnectionError, BusinessNotFoundError


class TestDiperionSDK:
    """Test suite for the Diperion SDK."""
    
    def test_import(self):
        """Test that the package can be imported."""
        assert diperion.__version__ == "0.1.0"
        assert hasattr(diperion, 'DiperionClient')
        assert hasattr(diperion, 'connect')
    
    def test_connect_function(self):
        """Test the connect convenience function."""
        with patch('diperion.client.DiperionClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            
            client = diperion.connect("http://test:8080")
            mock_client.assert_called_once_with("http://test:8080", 30)
    
    def test_connect_local_function(self):
        """Test the connect_local convenience function."""
        with patch('diperion.client.DiperionClient') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            
            client = diperion.connect_local(9090)
            mock_client.assert_called_once_with("http://localhost:9090", 30)
    
    @patch('diperion.client.requests.Session')
    def test_client_initialization(self, mock_session):
        """Test client initialization."""
        # Mock the health check
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_response
        
        client = diperion.DiperionClient("http://test:8080", timeout=60)
        
        assert client.base_url == "http://test:8080"
        assert client.timeout == 60
        
        # Verify health check was called
        mock_session.return_value.get.assert_called_once_with("http://test:8080/health")
    
    @patch('diperion.client.requests.Session')
    def test_connection_error(self, mock_session):
        """Test connection error handling."""
        # Mock a connection error
        mock_session.return_value.get.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(diperion.ConnectionError):
            diperion.DiperionClient("http://invalid:8080")
    
    def test_data_models(self):
        """Test that data models can be instantiated."""
        business = diperion.Business(
            id="test_business",
            name="Test Business",
            industry="test"
        )
        assert business.id == "test_business"
        assert business.name == "Test Business"
        assert str(business) == "Business(id='test_business', name='Test Business', industry='test')"
        
        node = diperion.Node(
            id="node1",
            name="Test Node",
            node_type="Product",
            attributes={"price": 100}
        )
        assert node.get_attribute("price") == 100
        assert node.get_attribute("missing", "default") == "default"
        
        node.set_attribute("category", "electronics")
        assert node.get_attribute("category") == "electronics"
    
    def test_query_result(self):
        """Test QueryResult functionality."""
        nodes = [
            diperion.Node("1", "Node 1", "Product"),
            diperion.Node("2", "Node 2", "Product")
        ]
        
        result = diperion.QueryResult(
            nodes=nodes,
            message="Test query",
            query="FIND Product",
            total_found=2
        )
        
        assert len(result) == 2
        assert result.first().name == "Node 1"
        assert result.names() == ["Node 1", "Node 2"]
        
        # Test iteration
        node_names = [node.name for node in result]
        assert node_names == ["Node 1", "Node 2"]
        
        # Test indexing
        assert result[0].name == "Node 1"
        assert result[1].name == "Node 2"
    
    def test_quickstart_function(self, capsys):
        """Test the quickstart function."""
        diperion.quickstart()
        captured = capsys.readouterr()
        assert "🚀 Diperion SDK Quick Start" in captured.out
        assert "import diperion" in captured.out


if __name__ == "__main__":
    pytest.main([__file__]) 