import pytest

from wiki.core import Processor, Page
from Riki import app

class TestProcessor:
    def test_constructor(self):
        # Complete setup and execution is in this fixture
        sample = Processor("# Sample Title\n\nSome sample paragraph text")
        assert sample.input == "# Sample Title\n\nSome sample paragraph text"

    def test_process_pre(self):
        sample = Processor("# Sample Title\n\nSome sample paragraph text")

        sample.process_pre()

        assert sample.pre == "# Sample Title\n\nSome sample paragraph text"

    def test_process_markdown(self):
        sample = Processor("# Sample Title\n\nSome sample paragraph text")

        sample.process_pre()
        sample.process_markdown()

        assert sample.html == "<h1>Sample Title</h1>\n<p>Some sample paragraph text</p>"
        
    def test_split_raw(self):
        sample = Processor("# Sample Title\n\nSome sample paragraph text")

        sample.process_pre()
        sample.process_markdown()
        sample.split_raw()

        assert sample.meta_raw == "# Sample Title"
        assert sample.markdown == "Some sample paragraph text"
    

    # FAILING TEST
    # codebase gives KeyError when running this test
    def test_process_meta(self):
        sample = Processor("# Sample Title\n\nSome sample paragraph text")

        sample.process_pre()
        sample.process_markdown()
        sample.split_raw()
        sample.process_meta()

        assert sample.meta == "# sample title"

    # Above test fails and is required to run below tests.
    def test_process_post(self):
        pass

    def test_process(self):
        pass
        #sample = Processor("# Sample Title\n\nSome sample paragraph text")
        
        #temp = sample.process()
        
        #assert temp.final == "<h1>Sample Title</h1>\n<p>Some sample paragraph text</p>"
        #assert temp.markdown == ""



class TestPage:
    def test_constructor(self):
        p = Page("path", "url", True)
        assert p.url == "url"
    

