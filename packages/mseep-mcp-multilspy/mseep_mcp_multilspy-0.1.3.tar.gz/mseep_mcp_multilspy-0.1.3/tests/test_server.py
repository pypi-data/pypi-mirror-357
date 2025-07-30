import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_multilspy.server import (
    initialize_language_server,
    request_completions,
    request_definition,
    shutdown_language_server,
)


class TestMultilspyMcpServer(unittest.TestCase):
    """Test the multilspy MCP server functionality."""

    @patch("mcp_multilspy.server.LanguageServer")
    @patch("mcp_multilspy.server.lsp_sessions")
    @patch("mcp_multilspy.server.os.path.isdir")
    async def test_initialize_language_server(self, mock_isdir, mock_sessions, mock_ls_create):
        """Test initializing a language server."""
        # Setup
        mock_isdir.return_value = True
        mock_ls = MagicMock()
        mock_ls_create.create.return_value = mock_ls
        
        # Test
        result = await initialize_language_server(
            session_id="test-session",
            project_root="/path/to/project",
            language="python"
        )
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertEqual(result["session_id"], "test-session")
        self.assertEqual(result["language"], "python")
        self.assertEqual(result["project_root"], "/path/to/project")
        
        # Verify session was stored
        self.assertTrue("test-session" in mock_sessions)
    
    @patch("mcp_multilspy.server.lsp_sessions")
    async def test_shutdown_language_server(self, mock_sessions):
        """Test shutting down a language server."""
        # Setup
        mock_sessions.get.return_value = MagicMock()
        mock_sessions.__contains__.return_value = True
        
        # Test
        result = await shutdown_language_server("test-session")
        
        # Assertions
        self.assertTrue(result["success"])
    
    @patch("mcp_multilspy.server.lsp_sessions")
    async def test_request_definition(self, mock_sessions):
        """Test requesting definitions."""
        # Setup
        mock_lsp = MagicMock()
        mock_lsp.start_server = AsyncMock().__aenter__.return_value = None
        mock_lsp.open_file = MagicMock().__enter__.return_value = None
        
        mock_definition = MagicMock()
        mock_definition.uri = "file:///path/to/project/src/file.py"
        mock_definition.range.start.line = 10
        mock_definition.range.start.character = 5
        mock_definition.range.end.line = 10
        mock_definition.range.end.character = 15
        
        mock_lsp.request_definition = AsyncMock(return_value=[mock_definition])
        
        mock_session = MagicMock()
        mock_session.language_server = mock_lsp
        mock_session.project_root = "/path/to/project"
        
        mock_sessions.__contains__.return_value = True
        mock_sessions.get.return_value = mock_session
        
        # Test
        result = await request_definition(
            session_id="test-session",
            file_path="src/file.py",
            line=5,
            column=10
        )
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertTrue(result["found"])
        self.assertEqual(len(result["definitions"]), 1)
        self.assertEqual(result["definitions"][0]["file"], "src/file.py")
        
    @patch("mcp_multilspy.server.lsp_sessions")
    async def test_request_completions(self, mock_sessions):
        """Test requesting completions."""
        # Setup
        mock_lsp = MagicMock()
        mock_lsp.start_server = AsyncMock().__aenter__.return_value = None
        mock_lsp.open_file = MagicMock().__enter__.return_value = None
        
        mock_completion_item = MagicMock()
        mock_completion_item.label = "test_method"
        mock_completion_item.kind = 2  # Method
        mock_completion_item.detail = "test_method(param): str"
        mock_completion_item.documentation = "Test method documentation"
        
        mock_completions = MagicMock()
        mock_completions.items = [mock_completion_item]
        
        mock_lsp.request_completions = AsyncMock(return_value=mock_completions)
        
        mock_session = MagicMock()
        mock_session.language_server = mock_lsp
        mock_session.project_root = "/path/to/project"
        
        mock_sessions.__contains__.return_value = True
        mock_sessions.get.return_value = mock_session
        
        # Test
        result = await request_completions(
            session_id="test-session",
            file_path="src/file.py",
            line=5,
            column=10
        )
        
        # Assertions
        self.assertTrue(result["success"])
        self.assertTrue(result["found"])
        self.assertEqual(len(result["completions"]), 1)
        self.assertEqual(result["completions"][0]["label"], "test_method")
        self.assertEqual(result["completions"][0]["kind"], 2)
        self.assertEqual(result["completions"][0]["detail"], "test_method(param): str")


if __name__ == "__main__":
    unittest.main()