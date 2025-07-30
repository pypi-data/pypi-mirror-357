"""
Validation tests for e2b-mcp package.

Tests for proper validation of server configurations, tools, and error handling.
"""

import pytest

from e2b_mcp import E2BMCPRunner, MCPError, ServerConfig, Tool


class TestServerConfigValidation:
    """Test ServerConfig validation features."""

    def test_valid_server_config(self):
        """Test valid server configurations."""
        # Minimal config
        config_minimal = ServerConfig(name="minimal_server", command="python test.py")
        assert config_minimal.name == "minimal_server"
        assert config_minimal.command == "python test.py"
        assert config_minimal.install_commands == []
        assert config_minimal.description == ""

        # Full config
        config_full = ServerConfig(
            name="full_server",
            command="python -m server --stdio",
            install_commands=["pip install test-package"],
            description="Full test server",
            timeout_minutes=15,
            env={"DEBUG": "1", "API_KEY": "test"},
        )
        assert config_full.install_commands == ["pip install test-package"]
        assert config_full.timeout_minutes == 15
        assert config_full.env["DEBUG"] == "1"

    def test_invalid_server_names(self):
        """Test server name validation."""
        # Empty name
        with pytest.raises(ValueError, match="Server name must be a non-empty string"):
            ServerConfig(name="", command="python test.py")

        # None name
        with pytest.raises(ValueError, match="Server name must be a non-empty string"):
            ServerConfig(name=None, command="python test.py")

        # Invalid characters
        invalid_names = [
            "server with spaces",
            "server!",
            "server@home",
            "server#1",
            "server$",
            "server%",
            "server^",
            "server&",
            "server*",
            "server()",
            "server=",
            "server+",
            "server[",
            "server]",
            "server{",
            "server}",
            "server\\",
            "server|",
            "server;",
            "server:",
            "server'",
            'server"',
            "server<",
            "server>",
            "server,",
            "server?",
            "server/",
        ]

        for invalid_name in invalid_names:
            with pytest.raises(ValueError, match="Server name must contain only alphanumeric"):
                ServerConfig(name=invalid_name, command="python test.py")

    def test_valid_server_names(self):
        """Test valid server name formats."""
        valid_names = [
            "server",
            "server1",
            "server_1",
            "server-1",
            "test_server",
            "test-server",
            "MyServer",
            "my_server_123",
            "server-with-dashes",
            "server_with_underscores",
            "123server",
            "SERVER",
            "a",
            "a1",
            "a_1",
            "a-1",
        ]

        for valid_name in valid_names:
            config = ServerConfig(name=valid_name, command="python test.py")
            assert config.name == valid_name

    def test_invalid_commands(self):
        """Test command validation."""
        # Empty command
        with pytest.raises(ValueError, match="Server command must be a non-empty string"):
            ServerConfig(name="test", command="")

        # None command
        with pytest.raises(ValueError, match="Server command must be a non-empty string"):
            ServerConfig(name="test", command=None)

    def test_invalid_timeouts(self):
        """Test timeout validation."""
        # Zero timeout
        with pytest.raises(ValueError, match="Timeout must be a positive integer"):
            ServerConfig(name="test", command="python test.py", timeout_minutes=0)

        # Negative timeout
        with pytest.raises(ValueError, match="Timeout must be a positive integer"):
            ServerConfig(name="test", command="python test.py", timeout_minutes=-1)

        # Non-integer timeout
        with pytest.raises(ValueError, match="Timeout must be a positive integer"):
            ServerConfig(name="test", command="python test.py", timeout_minutes=5.5)

    def test_invalid_initialization_timeout(self):
        """Test initialization_timeout validation."""
        # Zero initialization_timeout
        with pytest.raises(ValueError, match="Initialization timeout must be a positive integer"):
            ServerConfig(name="test", command="python test.py", initialization_timeout=0)

        # Negative initialization_timeout
        with pytest.raises(ValueError, match="Initialization timeout must be a positive integer"):
            ServerConfig(name="test", command="python test.py", initialization_timeout=-1)

        # Non-integer initialization_timeout
        with pytest.raises(ValueError, match="Initialization timeout must be a positive integer"):
            ServerConfig(name="test", command="python test.py", initialization_timeout=5.5)

    def test_valid_initialization_timeouts(self):
        """Test valid initialization_timeout values."""
        # Default value
        config_default = ServerConfig(name="test", command="python test.py")
        assert config_default.initialization_timeout == 30

        # Custom values
        for timeout in [1, 5, 30, 60, 120, 300]:
            config = ServerConfig(
                name="test", command="python test.py", initialization_timeout=timeout
            )
            assert config.initialization_timeout == timeout

    def test_install_commands_validation(self):
        """Test install_commands validation."""
        # Valid install commands
        config = ServerConfig(
            name="test", command="test", install_commands=["pip install requests", "apt-get update"]
        )
        assert len(config.install_commands) == 2

        # Should reject non-list
        with pytest.raises(ValueError, match="install_commands must be a list"):
            ServerConfig(name="test", command="test", install_commands="not a list")  # type: ignore

        # Should reject non-string elements
        with pytest.raises(ValueError, match="install_commands\\[0\\] must be a string"):
            ServerConfig(name="test", command="test", install_commands=[123])  # type: ignore

    def test_from_dict_validation(self):
        """Test ServerConfig.from_dict validation."""
        # Valid dict
        data = {
            "command": "python test.py",
            "install_commands": ["pip install test-package"],
            "description": "Test",
            "timeout_minutes": 5,
            "env": {"TEST": "1"},
        }
        config = ServerConfig.from_dict("test", data)
        assert config.name == "test"
        assert config.command == "python test.py"

        # Missing command
        with pytest.raises(ValueError, match="Configuration must include 'command' field"):
            ServerConfig.from_dict("test", {"install_commands": ["pip install test"]})

        # Non-dict data
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            ServerConfig.from_dict("test", "not a dict")

        # None data
        with pytest.raises(ValueError, match="Configuration data must be a dictionary"):
            ServerConfig.from_dict("test", None)

    def test_utility_methods(self):
        """Test ServerConfig utility methods."""
        # Config without installation
        config_no_install = ServerConfig(name="test", command="python test.py")
        assert not config_no_install.requires_installation()
        assert config_no_install.get_display_name() == "test"

        # Config with installation
        config_with_install = ServerConfig(
            name="test", command="python test.py", install_commands=["pip install my-package"]
        )
        assert config_with_install.requires_installation()

        # Config with description
        config_with_desc = ServerConfig(
            name="test", command="python test.py", description="My awesome server"
        )
        assert config_with_desc.get_display_name() == "My awesome server"

        # Config with empty install_commands should work fine
        config_empty_install = ServerConfig(
            name="test",
            command="python test.py",
            install_commands=[],
        )
        assert not config_empty_install.requires_installation()


class TestToolValidation:
    """Test tool validation features."""

    def test_valid_tool_creation(self):
        """Test creating valid tools."""
        # Basic tool
        tool = Tool(name="test_tool", description="Test tool")
        assert tool.name == "test_tool"
        assert tool.description == "Test tool"
        assert tool.input_schema == {}
        assert tool.server_name == ""

        # Tool with schema
        schema = {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "First parameter"},
                "param2": {"type": "integer", "description": "Second parameter"},
            },
            "required": ["param1"],
        }
        tool_with_schema = Tool(
            name="complex_tool",
            description="Complex tool",
            input_schema=schema,
            server_name="test_server",
        )
        assert tool_with_schema.input_schema == schema
        assert tool_with_schema.server_name == "test_server"

    def test_invalid_tool_creation(self):
        """Test tool validation errors."""
        # Empty name
        with pytest.raises(ValueError, match="Tool name must be a non-empty string"):
            Tool(name="", description="Test")

        # None name
        with pytest.raises(ValueError, match="Tool name must be a non-empty string"):
            Tool(name=None, description="Test")

        # Invalid schema type
        with pytest.raises(ValueError, match="Input schema must be a dictionary"):
            Tool(name="test", description="Test", input_schema="not a dict")

    def test_from_mcp_tool(self):
        """Test Tool.from_mcp_tool method."""
        # Valid MCP tool data
        mcp_data = {
            "name": "test_tool",
            "description": "Test tool from MCP",
            "inputSchema": {"type": "object", "properties": {"param": {"type": "string"}}},
        }
        tool = Tool.from_mcp_tool(mcp_data, "test_server")
        assert tool.name == "test_tool"
        assert tool.description == "Test tool from MCP"
        assert tool.server_name == "test_server"

        # Missing name
        with pytest.raises(ValueError, match="Tool data must include 'name' field"):
            Tool.from_mcp_tool({"description": "Test"}, "server")

        # Non-dict data
        with pytest.raises(ValueError, match="Tool data must be a dictionary"):
            Tool.from_mcp_tool("not a dict", "server")

    def test_parameter_extraction(self):
        """Test parameter extraction methods."""
        schema = {
            "type": "object",
            "properties": {
                "required_param": {"type": "string", "description": "Required parameter"},
                "optional_param": {"type": "integer", "description": "Optional parameter"},
                "another_required": {"type": "boolean", "description": "Another required"},
            },
            "required": ["required_param", "another_required"],
        }

        tool = Tool(name="test", description="Test", input_schema=schema)

        # Test required parameters
        required = tool.get_required_parameters()
        assert set(required) == {"required_param", "another_required"}

        # Test optional parameters
        optional = tool.get_optional_parameters()
        assert set(optional) == {"optional_param"}

        # Test parameter info
        param_info = tool.get_parameter_info("required_param")
        assert param_info["type"] == "string"
        assert param_info["description"] == "Required parameter"

        # Non-existent parameter
        assert tool.get_parameter_info("nonexistent") is None

    def test_parameter_validation(self):
        """Test parameter validation against schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name parameter"},
                "age": {"type": "integer", "description": "Age parameter"},
                "active": {"type": "boolean", "description": "Active parameter"},
                "tags": {"type": "array", "description": "Tags parameter"},
                "config": {"type": "object", "description": "Config parameter"},
            },
            "required": ["name", "age"],
        }

        tool = Tool(name="test", description="Test", input_schema=schema)

        # Valid parameters
        valid_params = {"name": "test", "age": 25, "active": True}
        errors = tool.validate_parameters(valid_params)
        assert errors == []

        # Missing required parameter
        missing_required = {"name": "test"}  # missing age
        errors = tool.validate_parameters(missing_required)
        assert len(errors) == 1
        assert "Missing required parameter: age" in errors

        # Wrong type
        wrong_type = {"name": "test", "age": "not an integer"}
        errors = tool.validate_parameters(wrong_type)
        assert len(errors) == 1
        assert "should be of type integer" in errors[0]

        # Multiple errors
        multiple_errors = {"age": "not an integer"}  # missing name, wrong type
        errors = tool.validate_parameters(multiple_errors)
        assert len(errors) == 2

        # Valid with all types
        all_types = {
            "name": "test",
            "age": 25,
            "active": True,
            "tags": ["tag1", "tag2"],
            "config": {"key": "value"},
        }
        errors = tool.validate_parameters(all_types)
        assert errors == []

    def test_tool_utility_methods(self):
        """Test tool utility methods."""
        tool = Tool(name="test_tool", description="Test tool", server_name="test_server")

        # Full name
        assert tool.get_full_name() == "test_server.test_tool"

        # Tool without server
        tool_no_server = Tool(name="tool", description="Test")
        assert tool_no_server.get_full_name() == "tool"


class TestMCPErrorHandling:
    """Test improved error handling."""

    def test_mcp_error_with_context(self):
        """Test MCPError with server and tool context."""
        # Basic error
        error = MCPError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.server_name is None
        assert error.tool_name is None

        # Error with server context
        error_with_server = MCPError("Server error", server_name="test_server")
        assert "server=test_server" in str(error_with_server)
        assert error_with_server.server_name == "test_server"

        # Error with tool context
        error_with_tool = MCPError("Tool error", tool_name="test_tool")
        assert "tool=test_tool" in str(error_with_tool)
        assert error_with_tool.tool_name == "test_tool"

        # Error with both contexts
        error_with_both = MCPError("Full error", server_name="test_server", tool_name="test_tool")
        error_str = str(error_with_both)
        assert "server=test_server" in error_str
        assert "tool=test_tool" in error_str
        assert error_with_both.server_name == "test_server"
        assert error_with_both.tool_name == "test_tool"

    def test_error_inheritance(self):
        """Test that MCPError properly inherits from Exception."""
        error = MCPError("Test error")
        assert isinstance(error, Exception)

        # Can be caught as Exception
        try:
            raise MCPError("Test")
        except Exception as e:
            assert isinstance(e, MCPError)


class TestRunnerValidation:
    """Test validation features in E2BMCPRunner."""

    def test_runner_creation_validation(self):
        """Test runner creation with API key validation."""
        # Valid runner with explicit key
        runner = E2BMCPRunner(api_key="test_key")
        assert runner.api_key == "test_key"

        # No API key should raise error
        import os

        original_env = os.environ.get("E2B_API_KEY")
        if "E2B_API_KEY" in os.environ:
            del os.environ["E2B_API_KEY"]

        try:
            with pytest.raises(ValueError, match="E2B_API_KEY is required"):
                E2BMCPRunner()
        finally:
            if original_env:
                os.environ["E2B_API_KEY"] = original_env

    def test_bulk_server_configuration(self):
        """Test bulk server configuration."""
        runner = E2BMCPRunner(api_key="test_key")

        configs = {
            "server1": {"command": "python server1.py", "description": "First server"},
            "server2": {
                "command": "python server2.py",
                "install_commands": ["pip install test-package"],
                "timeout_minutes": 15,
            },
        }

        runner.add_servers(configs)

        assert len(runner.list_servers()) == 2
        assert "server1" in runner.list_servers()
        assert "server2" in runner.list_servers()

        # Check individual configs
        config1 = runner.get_server_config("server1")
        assert config1.command == "python server1.py"
        assert config1.description == "First server"

        config2 = runner.get_server_config("server2")
        assert config2.install_commands == ["pip install test-package"]
        assert config2.timeout_minutes == 15

    def test_server_info_method(self):
        """Test get_server_info method."""
        runner = E2BMCPRunner(api_key="test_key")

        config = ServerConfig(
            name="test_server",
            command="python test.py",
            install_commands=["pip install test-package"],
            description="Test server",
            timeout_minutes=20,
            initialization_timeout=45,
            env={"DEBUG": "1", "API_KEY": "test"},
        )
        runner.add_server(config)

        info = runner.get_server_info("test_server")
        assert info is not None
        assert info["name"] == "test_server"
        assert info["command"] == "python test.py"
        assert info["install_commands"] == ["pip install test-package"]
        assert info["description"] == "Test server"
        assert info["timeout_minutes"] == 20
        assert info["initialization_timeout"] == 45
        assert info["requires_installation"] is True
        assert info["display_name"] == "Test server"
        assert set(info["env_vars"]) == {"DEBUG", "API_KEY"}

        # Non-existent server
        assert runner.get_server_info("nonexistent") is None

    def test_session_management_methods(self):
        """Test session management utility methods."""
        runner = E2BMCPRunner(api_key="test_key")

        # Initially no sessions
        assert runner.get_active_session_count() == 0
        assert runner.list_active_sessions() == []
