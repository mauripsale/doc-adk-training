import unittest
from unittest.mock import MagicMock, patch
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools import ToolContext
from agent import (
    before_agent_callback, 
    after_agent_callback, 
    before_model_callback, 
    before_tool_callback,
    BLOCKED_WORDS
)

class TestCallbacks(unittest.TestCase):

    def setUp(self):
        self.callback_context = MagicMock(spec=CallbackContext)
        self.callback_context.state = {}
        self.callback_context.session = MagicMock()
        self.callback_context.session.events = []

    def test_before_agent_callback_cache_hit(self):
        self.callback_context.state['cached_response'] = "Cached answer"
        result = before_agent_callback(self.callback_context)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, types.Content)
        self.assertEqual(result.parts[0].text, "[CACHED]: Cached answer")

    def test_before_agent_callback_cache_miss(self):
        result = before_agent_callback(self.callback_context)
        self.assertIsNone(result)

    def test_after_agent_callback_saves_cache(self):
        # Mock session events
        event = MagicMock()
        event.author = "model"
        event.content = types.Content(parts=[types.Part(text="New answer")], role="model")
        self.callback_context.session.events = [event]
        
        after_agent_callback(self.callback_context)
        self.assertEqual(self.callback_context.state.get('cached_response'), "New answer")

    def test_before_model_callback_blocks_offensive(self):
        llm_request = MagicMock(spec=LlmRequest)
        content = types.Content(parts=[types.Part(text="This is offensive")], role="user")
        llm_request.contents = [content]
        
        result = before_model_callback(self.callback_context, llm_request)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, LlmResponse)
        self.assertIn("cannot process offensive prompts", result.content.parts[0].text)

    def test_before_model_callback_allows_safe(self):
        llm_request = MagicMock(spec=LlmRequest)
        content = types.Content(parts=[types.Part(text="This is safe")], role="user")
        llm_request.contents = [content]
        
        result = before_model_callback(self.callback_context, llm_request)
        self.assertIsNone(result)

    def test_before_tool_callback_blocks_large_count(self):
        tool = MagicMock(spec=BaseTool)
        tool.name = 'generate_text'
        args = {'topic': 'AI', 'word_count': 6000}
        tool_context = MagicMock(spec=ToolContext)
        
        result = before_tool_callback(tool, args, tool_context)
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'error')
        self.assertIn("exceeds the maximum limit", result['message'])

    def test_before_tool_callback_allows_small_count(self):
        tool = MagicMock(spec=BaseTool)
        tool.name = 'generate_text'
        args = {'topic': 'AI', 'word_count': 100}
        tool_context = MagicMock(spec=ToolContext)
        
        result = before_tool_callback(tool, args, tool_context)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
