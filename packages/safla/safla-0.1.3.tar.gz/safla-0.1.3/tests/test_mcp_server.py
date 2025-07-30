"""
Comprehensive test suite for the modular MCP server.

Tests the core MCP server functionality including initialization,
request handling, handler registration, and stdio communication.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import Dict, Any, List

from safla.mcp.server import ModularMCPServer
from safla.mcp.handlers.base import BaseHandler
from safla.mcp.state.manager import StateManager
from safla.utils.config import SAFLAConfig
from safla.exceptions import SAFLAError


class MockHandler(BaseHandler):
    """Mock handler for testing."""
    
    def __init__(self, config, state_manager):
        super().__init__(config, state_manager)
        self._tools = ["mock_tool", "another_tool"]
    
    async def handle_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "mock_tool":
            return {"result": "mock_result", "args": arguments}
        elif tool_name == "another_tool":
            return {"result": "another_result"}
        raise ValueError(f"Unknown tool: {tool_name}")
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "mock_tool",
                "description": "A mock tool for testing",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "another_tool",
                "description": "Another mock tool",
                "inputSchema": {"type": "object"}
            }
        ]


class TestModularMCPServer:
    """Test cases for ModularMCPServer."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration."""
        config = MagicMock(spec=SAFLAConfig)
        config.get.return_value = {}
        return config
    
    @pytest.fixture
    def server(self, mock_config):
        """Create a server instance for testing."""
        with patch('safla.mcp.server.SystemHandler'), \
             patch('safla.mcp.server.OptimizationHandler'), \
             patch('safla.mcp.server.BenchmarkingHandler'):
            server = ModularMCPServer(config=mock_config)
        return server
    
    def test_server_initialization(self, mock_config):
        """Test server initialization."""
        with patch('safla.mcp.server.SystemHandler') as mock_system, \
             patch('safla.mcp.server.OptimizationHandler') as mock_opt, \
             patch('safla.mcp.server.BenchmarkingHandler') as mock_bench:
            
            server = ModularMCPServer(config=mock_config)
            
            # Verify components are initialized
            assert server.config == mock_config
            assert server.request_id == 0
            assert isinstance(server.state_manager, StateManager)
            assert isinstance(server._handlers, dict)
            assert isinstance(server._resources, dict)
            
            # Verify handlers are initialized
            mock_system.assert_called_once()
            mock_opt.assert_called_once()
            mock_bench.assert_called_once()
    
    def test_register_handler(self, server):
        """Test handler registration."""
        mock_handler = MockHandler(server.config, server.state_manager)
        
        server._register_handler(mock_handler)
        
        # Verify tools are registered
        assert "mock_tool" in server._handlers
        assert "another_tool" in server._handlers
        assert server._handlers["mock_tool"] == mock_handler
        assert server._handlers["another_tool"] == mock_handler
    
    def test_handler_registration_override_warning(self, server, caplog):
        """Test warning when overriding existing handler."""
        mock_handler1 = MockHandler(server.config, server.state_manager)
        mock_handler2 = MockHandler(server.config, server.state_manager)
        
        server._register_handler(mock_handler1)
        server._register_handler(mock_handler2)
        
        # Check for warning log
        assert "already registered" in caplog.text
    
    @pytest.mark.asyncio
    async def test_handle_initialize_request(self, server):
        """Test handling initialize request."""
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "client_info": {
                    "name": "Test Client",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        response = await server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert response["result"]["server_info"]["name"] == "SAFLA MCP Server"
        assert response["result"]["capabilities"]["tools"] is True
        assert response["result"]["capabilities"]["resources"] is True
        
        # Verify client info is stored
        stored_info = server.state_manager.get("client_info", namespace="session")
        assert stored_info["name"] == "Test Client"
    
    @pytest.mark.asyncio
    async def test_handle_list_tools_request(self, server):
        """Test handling list_tools request."""
        # Register a mock handler
        mock_handler = MockHandler(server.config, server.state_manager)
        server._register_handler(mock_handler)
        
        request = {
            "jsonrpc": "2.0",
            "method": "list_tools",
            "params": {},
            "id": 2
        }
        
        with patch.object(mock_handler, 'get_tool_descriptions') as mock_get_tools:
            mock_get_tools.return_value = [
                {"name": "mock_tool", "description": "Mock tool"}
            ]
            
            response = await server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 2
        assert "result" in response
        assert "tools" in response["result"]
    
    @pytest.mark.asyncio
    async def test_handle_call_tool_request(self, server):
        """Test handling call_tool request."""
        # Register a mock handler
        mock_handler = MockHandler(server.config, server.state_manager)
        server._register_handler(mock_handler)
        
        request = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "tool": "mock_tool",
                "arguments": {"param1": "value1"}
            },
            "id": 3
        }
        
        response = await server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 3
        assert "result" in response
        assert response["result"]["result"] == "mock_result"
        assert response["result"]["args"]["param1"] == "value1"
    
    @pytest.mark.asyncio
    async def test_handle_unknown_method(self, server):
        """Test handling unknown method."""
        request = {
            "jsonrpc": "2.0",
            "method": "unknown_method",
            "params": {},
            "id": 4
        }
        
        response = await server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 4
        assert "error" in response
        assert response["error"]["code"] == -32603
        assert "Unknown method" in response["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_handle_tool_not_found(self, server):
        """Test handling call to non-existent tool."""
        request = {
            "jsonrpc": "2.0",
            "method": "call_tool",
            "params": {
                "tool": "non_existent_tool",
                "arguments": {}
            },
            "id": 5
        }
        
        response = await server.handle_request(request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 5
        assert "error" in response
        assert response["error"]["code"] == -32603
    
    @pytest.mark.asyncio
    async def test_handle_malformed_request(self, server):
        """Test handling malformed request."""
        request = {
            "method": "list_tools"
            # Missing jsonrpc and id
        }
        
        response = await server.handle_request(request)
        
        assert "error" in response
    
    @pytest.mark.asyncio
    async def test_stdio_communication(self, server):
        """Test stdio communication handling."""
        # Mock stdin and stdout
        mock_stdin_data = [
            '{"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1}\n',
            '{"jsonrpc": "2.0", "method": "list_tools", "params": {}, "id": 2}\n',
            ''  # EOF
        ]
        
        with patch.object(server, '_read_line', side_effect=mock_stdin_data), \
             patch.object(server, '_write_response') as mock_write, \
             patch.object(server, '_cleanup') as mock_cleanup:
            
            await server.run()
            
            # Verify responses were written
            assert mock_write.call_count == 2
            mock_cleanup.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_json_decode_error(self, server):
        """Test handling JSON decode error."""
        invalid_json = 'invalid json data\n'
        
        with patch.object(server, '_read_line', side_effect=[invalid_json, '']), \
             patch.object(server, '_write_response') as mock_write, \
             patch.object(server, '_cleanup'):
            
            await server.run()
            
            # Verify error response was written
            mock_write.assert_called_once()
            error_response = mock_write.call_args[0][0]
            assert error_response["error"]["code"] == -32700
            assert "Parse error" in error_response["error"]["message"]
    
    @pytest.mark.asyncio
    async def test_request_id_handling(self, server):
        """Test proper request ID handling."""
        # Request with ID
        request_with_id = {
            "jsonrpc": "2.0",
            "method": "list_tools",
            "params": {},
            "id": 123
        }
        
        response = await server.handle_request(request_with_id)
        assert response["id"] == 123
        
        # Request without ID (notification)
        request_without_id = {
            "jsonrpc": "2.0",
            "method": "list_tools",
            "params": {}
        }
        
        response = await server.handle_request(request_without_id)
        assert "id" not in response or response["id"] is None
    
    @pytest.mark.asyncio
    async def test_handler_initialization_error(self, mock_config):
        """Test graceful handling of handler initialization errors."""
        with patch('safla.mcp.server.SystemHandler', side_effect=Exception("Init error")), \
             patch('safla.mcp.server.OptimizationHandler'), \
             patch('safla.mcp.server.BenchmarkingHandler'), \
             patch('safla.mcp.server.logger') as mock_logger:
            
            server = ModularMCPServer(config=mock_config)
            
            # Verify error was logged
            mock_logger.error.assert_called()
            assert "Failed to initialize handler" in str(mock_logger.error.call_args)
    
    def test_create_response(self, server):
        """Test response creation."""
        response = server._create_response(123, {"data": "test"})
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 123
        assert response["result"] == {"data": "test"}
    
    def test_create_error_response(self, server):
        """Test error response creation."""
        error_response = server._create_error_response(
            -32603, "Internal error", "Details here", 456
        )
        
        assert error_response["jsonrpc"] == "2.0"
        assert error_response["id"] == 456
        assert error_response["error"]["code"] == -32603
        assert error_response["error"]["message"] == "Internal error"
        assert error_response["error"]["data"] == "Details here"
    
    @pytest.mark.asyncio
    async def test_state_persistence(self, server):
        """Test state persistence functionality."""
        # Store some state
        server.state_manager.set("test_key", "test_value", namespace="test")
        
        # Verify state is stored
        value = server.state_manager.get("test_key", namespace="test")
        assert value == "test_value"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, server):
        """Test handling concurrent requests."""
        # Register a mock handler
        mock_handler = MockHandler(server.config, server.state_manager)
        server._register_handler(mock_handler)
        
        # Create multiple requests
        requests = [
            {
                "jsonrpc": "2.0",
                "method": "call_tool",
                "params": {"tool": "mock_tool", "arguments": {"id": i}},
                "id": i
            }
            for i in range(5)
        ]
        
        # Handle requests concurrently
        tasks = [server.handle_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # Verify all requests were handled
        assert len(responses) == 5
        for i, response in enumerate(responses):
            assert response["id"] == i
            assert "result" in response