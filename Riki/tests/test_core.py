import pytest
import tempfile, os
from PIL import Image
from collections import OrderedDict
from wiki.core import Processor, Page, Wiki

from wiki.core import Processor, Page, Wiki
import config

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
        sample = Processor("meta:page\n\n# Sample Title\nSome sample paragraph text")

        sample.process_pre()
        sample.process_markdown()
        sample.split_raw()

        assert sample.meta_raw == "meta:page"
        assert sample.markdown == "# Sample Title\nSome sample paragraph text"
    

    # FAILING TEST
    # codebase gives KeyError when running this test
    def test_process_meta(self):
        sample = Processor("meta:page\n\n# Sample Title\nSome sample paragraph text")

        sample.process_pre()
        sample.process_markdown()
        sample.split_raw()
        sample.process_meta()

        test = OrderedDict([('meta', 'page')])
        assert sample.meta == test

    # Above test fails and is required to run below tests.
    def test_process_post(self):
        sample = Processor("meta:page\n\n# Sample Title\nSome sample paragraph text")

        sample.process_pre()
        sample.process_markdown()
        sample.split_raw()
        sample.process_meta()
        sample.process_post()
        assert sample.final == "<h1>Sample Title</h1>\n<p>Some sample paragraph text</p>"

    def test_process(self):
        sample = Processor("meta:page\n\n# Sample Title\nSome sample paragraph text")
        
        sample.process()
        
        assert sample.final == "<h1>Sample Title</h1>\n<p>Some sample paragraph text</p>"
        assert sample.markdown == "# Sample Title\nSome sample paragraph text"
        assert sample.meta == OrderedDict([('meta', 'page')])



class TestPage:
    def setup_method(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tempdir.name, "test.html")
        self.page = Page(self.path, "url", True)

    def test_constructor(self):
        assert self.page.url == "url"

    def test___repr__(self):
        assert str(self.page) == f"<Page: url@{self.path}>"

    def test_load(self):
        content = "Test content"
        with open(self.path, 'w', encoding="utf-8") as f:
            f.write(content)
        # Call load() to read the content of the file
        self.page.load()
        assert self.page.content == content

    def test_save_with_existing_directory(self):
        self.page['title'] = 'Test'
        self.page.body = '<p>Test</p>'
        self.page.save()
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()
        assert os.path.exists(self.path)
        assert content == "title: Test\n\n<p>Test</p>"

    def test_save_with_no_existing_directory(self):
        p = Page("nonexistent.path", "url", new=True)
        p['title'] = 'Test'
        p.body = '<p>Test</p>'
        with pytest.raises(FileNotFoundError):
            p.save()

    def test_meta(self):
        self.page.meta["key"] = "value"
        self.page.meta["name"] = "abebe"
        assert self.page["key"] == "value"
        assert self.page["name"] == "abebe"

    def test__getitem__(self):
        self.page._meta["key"] = "value"
        assert self.page["key"] == "value"

    def test__setitem__(self):
        self.page["key"] = "value"
        assert self.page._meta["key"] == "value"

    def test_html(self):
        self.page._html = "<html></html>"
        assert self.page.html == "<html></html>"

    def test_title(self):
        self.page['title'] = "Test title"
        assert self.page.title == "Test title"

    def test_missing_title(self):
        url = "url"
        assert self.page.title == url

    def test_tags(self):
        self.page.tags = 'test_tag1, test_tag2'
        assert self.page.tags == 'test_tag1, test_tag2'

    def test_missing_tags(self):
        assert self.page.tags == ""


class TestWiki:
    def setup_method(self):
        self.tempdir = '/tmp'
        self.wiki = Wiki(self.tempdir)

    def test_constructor(self):
        assert self.wiki.root == self.tempdir

    def test_path(self):
        url = 'page1'
        expected_path = os.path.join(self.wiki.root, 'page1.md')
        path = self.wiki.path(url)
        assert path == expected_path

    def test_exists(self):
        url = 'page1'
        assert not self.wiki.exists(url)

        path = self.wiki.path(url)
        with open(path, 'w') as f:
            f.write('# Page 1')

        assert self.wiki.exists(url)

    def test_delete_existing_page(self):
        url = 'existing-page'
        wiki_path = self.wiki.path(url)
        with open(wiki_path, 'w') as f:
            f.write('# Existing Page')

        page = self.wiki.delete(url)

        assert page is True
        assert not self.wiki.exists(wiki_path)

    def test_delete_nonexistent_page(self):
        url = 'nonexistent-page'
        page = self.wiki.delete(url)
        assert page is False

    def test_allowed_file(self):
        assert self.wiki.allowed_file('badfile') is False
        assert self.wiki.allowed_file('goodfile.jpg')

    def test_save_image(self):
        file = Image.new("L", [128,128])
        file.filename = "filename.jpg"
        self.wiki.save_image(file)
        full_path = os.path.join(config.PIC_BASE, file.filename)
        assert os.path.exists(full_path)
        with Image.open(full_path) as im:
            assert im.format == 'JPEG'
            assert im.size == (128, 128)
            assert im.mode == 'L'