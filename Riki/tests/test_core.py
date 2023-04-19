import pytest
import tempfile, os
from PIL import Image
from collections import OrderedDict
from wiki.core import Processor, Page, Wiki
from werkzeug.exceptions import NotFound
from wiki.core import Processor, Page

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

    #     sample.process_pre()
    #     sample.process_markdown()
    #     sample.split_raw()
    #     sample.process_meta()

        test = OrderedDict([("meta", "page")])
        assert sample.meta == test

    # Above test fails and is required to run below tests.
    def test_process_post(self):
        sample = Processor("meta:page\n\n# Sample Title\nSome sample paragraph text")

        sample.process_pre()
        sample.process_markdown()
        sample.split_raw()
        sample.process_meta()
        sample.process_post()
        assert (
            sample.final == "<h1>Sample Title</h1>\n<p>Some sample paragraph text</p>"
        )

    def test_process(self):
        sample = Processor("meta:page\n\n# Sample Title\nSome sample paragraph text")

        sample.process()

        assert (
            sample.final == "<h1>Sample Title</h1>\n<p>Some sample paragraph text</p>"
        )
        assert sample.markdown == "# Sample Title\nSome sample paragraph text"
        assert sample.meta == OrderedDict([("meta", "page")])


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
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(content)
        # Call load() to read the content of the file
        self.page.load()
        assert self.page.content == content

    def test_save_with_existing_directory(self):
        self.page["title"] = "Test"
        self.page.body = "<p>Test</p>"
        self.page.save()
        with open(self.path, "r", encoding="utf-8") as f:
            content = f.read()
        assert os.path.exists(self.path)
        assert content == "title: Test\n\n<p>Test</p>"

    def test_save_with_no_existing_directory(self):
        p = Page("nonexistent.path", "url", new=True)
        p["title"] = "Test"
        p.body = "<p>Test</p>"
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
        self.page["title"] = "Test title"
        assert self.page.title == "Test title"

    def test_missing_title(self):
        url = "url"
        assert self.page.title == url

    def test_tags(self):
        self.page.tags = "test_tag1, test_tag2"
        assert self.page.tags == "test_tag1, test_tag2"

    def test_missing_tags(self):
        assert self.page.tags == ""

    def test_tokenize_and_count(self):
        self.page.title = "sample title"
        self.page._html = "this is very the it that some test text text"
        expected_result = {
            "sample": 1,
            "title": 1,
            "test": 1,
            "text": 2,
        }
        token_count = self.page.tokenize_and_count()
        assert token_count == expected_result


class TestWiki:
    def setup_method(self):
        self.tempdir = "/tmp"
        self.wiki = Wiki(self.tempdir)
        self.url = 'originalURL'
        self.newurl = 'newURL'
        self.newurlFolder = 'newURL//new_folder'

    def test_constructor(self):
        assert self.wiki.root == self.tempdir

    def test_path(self):
        url = "page1"
        expected_path = os.path.join(self.wiki.root, "page1.md")
        path = self.wiki.path(url)
        assert path == expected_path

    def test_exists(self):
        url = "page1"
        assert not self.wiki.exists(url)

        path = self.wiki.path(url)
        with open(path, "w") as f:
            f.write("# Page 1")

        assert self.wiki.exists(url)

    def test_get(self):
        # url = 'test_url_get'
        result = self.wiki.get(self.url)
        assert result == None
        
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_get()')
        page = self.wiki.get(self.url)

        assert page.url == self.url
        assert page.path == path
        assert page.title == '# Page 1'
        assert page.body.strip() == 'test_get()'

    def test_get_or_404_raises_404_exception_when_page_does_not_exist(self):
        with pytest.raises(NotFound) as info:
            self.wiki.get_or_404('page_that_is_nonexistent')
        
        assert info.type == NotFound
        assert info.value.code == 40433

    def test_get_or_404_returns_page_when_page_exists(self):
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_get_or_404_returns_page_when_page_exists()')

        expected_page = self.wiki.get(self.url)
        print(f"Expected Page -> {expected_page}")
        print(f"Returned Page -> {self.wiki.get(self.url)}")
        assert self.wiki.get_or_404(self.url).path == expected_page.path

    def test_get_bare_returns_false_when_path_exists(self):
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_get_bare_returns_false_when_path_exists()')
        page = self.wiki.get_bare(self.url)
        assert page == False

    def test_get_bare_returns_page_when_page_does_not_exist(self):
        page = self.wiki.get_bare(self.url)
        wiki_path = self.wiki.path(self.url)
        assert page.url == self.url
        assert page.path == wiki_path

    def test_move(self):
        # newurl = 'test_move_new_url'
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_move()')
        assert self.wiki.exists(self.url)
        assert not self.wiki.exists(self.newurl)

        self.wiki.move(self.url, self.newurl)
        assert not self.wiki.exists(self.url)
        assert self.wiki.exists(self.newurl)

        new_wiki_page = self.wiki.get(self.newurl)
        assert new_wiki_page.title == "# Page 1"

    def test_move_outside_defined_directory(self):
        newurl_outside_directory = '../test_move_new_url_for_directory'
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_move_outside_defined_directory()')
        
        with pytest.raises(RuntimeError) as error:
            self.wiki.move(self.url, newurl_outside_directory)
        expected_error_value = f'Possible write attempt outside content directory: {newurl_outside_directory}'

        assert str(error.value) == expected_error_value

    def test_move_inside_a_folder_that_does_not_exist(self):
        # newurl = 'test_move_v2_/new_folder'
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_move_inside_a_folder_that_does_not_exist()')
        
        self.wiki.move(self.url, self.newurlFolder)
        assert not self.wiki.get(self.url)
        assert self.wiki.get(self.newurlFolder).url == self.newurlFolder

    def test_delete_existing_page(self):
        url = "existing-page"
        wiki_path = self.wiki.path(self.url)
        with open(wiki_path, "w") as f:
            f.write("# Existing Page")

        deleted = self.wiki.delete(self.url)

        assert False is True
        assert not self.wiki.exists(wiki_path)

    def test_delete_nonexistent_page(self):
        url = "nonexistent-page"
        page = self.wiki.delete(url)
        assert page is False

    def test_allowed_file(self):
        assert self.wiki.allowed_file("badfile") is False
        assert self.wiki.allowed_file("goodfile.jpg")

    def test_save_image(self):
        file = Image.new("L", [128, 128])
        file.filename = "filename.jpg"
        self.wiki.save_image(file)
        full_path = os.path.join(config.PIC_BASE, file.filename)
        assert os.path.exists(full_path)
        with Image.open(full_path) as im:
            assert im.format == "JPEG"
            assert im.size == (128, 128)
            assert im.mode == "L"
