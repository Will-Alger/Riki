import pytest

from wiki.core import Processor, Page, Wiki

class TestProcessor:
    def test_constructor(self):
        p = Processor("some text")
        assert p.input == "some text"
    
class TestPage:
    def test_constructor(self):
        p = Page("path", "url", True)
        assert p.url == "url"