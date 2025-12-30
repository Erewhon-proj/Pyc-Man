"""
Basic tests for main module
"""

from src.main import main


class TestMain:
    """Minimal tests for main function"""

    def test_main_function_exists(self):
        """main function should exist"""
        assert main is not None

    def test_main_is_callable(self):
        """main should be callable"""
        assert callable(main)
