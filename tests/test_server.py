"""
Tests for the main server functionality
"""

from unittest.mock import Mock, patch

import pytest

from server import handle_call_tool, handle_list_tools


class TestServerTools:
    """Test server tool handling"""

    @pytest.mark.asyncio
    async def test_handle_list_tools(self):
        """Test listing all available tools"""
        tools = await handle_list_tools()
        tool_names = [tool.name for tool in tools]

        # Check all core tools are present
        assert "thinkdeep" in tool_names
        assert "codereview" in tool_names
        assert "debug" in tool_names
        assert "analyze" in tool_names
        assert "chat" in tool_names
        assert "precommit" in tool_names
        assert "get_version" in tool_names

        # Should have exactly 7 tools
        assert len(tools) == 7

        # Check descriptions are verbose
        for tool in tools:
            assert len(tool.description) > 50  # All should have detailed descriptions

    @pytest.mark.asyncio
    async def test_handle_call_tool_unknown(self):
        """Test calling an unknown tool"""
        result = await handle_call_tool("unknown_tool", {})
        assert len(result) == 1
        assert "Unknown tool: unknown_tool" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_chat(self):
        """Test chat functionality"""
        # Set test environment
        import os

        os.environ["PYTEST_CURRENT_TEST"] = "test"

        # Create a mock for the model
        with patch("tools.base.BaseTool.create_model") as mock_create:
            mock_model = Mock()
            mock_model.generate_content.return_value = Mock(
                candidates=[Mock(content=Mock(parts=[Mock(text="Chat response")]))]
            )
            mock_create.return_value = mock_model

            result = await handle_call_tool("chat", {"prompt": "Hello Gemini"})

            assert len(result) == 1
            # Parse JSON response
            import json

            response_data = json.loads(result[0].text)
            assert response_data["status"] == "success"
            assert "Chat response" in response_data["content"]
            assert "Claude's Turn" in response_data["content"]

    @pytest.mark.asyncio
    async def test_handle_get_version(self):
        """Test getting version info"""
        result = await handle_call_tool("get_version", {})
        assert len(result) == 1

        response = result[0].text
        assert "Gemini MCP Server v" in response  # Version agnostic check
        assert "Available Tools:" in response
        assert "thinkdeep" in response
