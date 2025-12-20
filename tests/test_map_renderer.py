"""
Basic tests for map_renderer module
"""

from src.main import map_renderer


class TestMapRenderer:
    """Minimal tests for map renderer"""

    def test_map_renderer_function_exists(self):
        """map_renderer function should exist"""
        assert map_renderer is not None

    def test_map_renderer_is_callable(self):
        """map_renderer should be callable"""
        assert callable(map_renderer)
