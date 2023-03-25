import pytest
import tempfile, os
from collections import OrderedDict
from wiki.core import Processor, Page, Wiki

class TestProcessor:
    def test_constructor(self):
        p = Processor("some text")
        assert p.input == "some text"
    
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
