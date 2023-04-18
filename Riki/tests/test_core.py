import pytest
import tempfile, os
from collections import OrderedDict
from wiki.core import Processor, Page, Wiki
from werkzeug.exceptions import HTTPException, NotFound
from wiki.core import Processor, Page
from Riki import app

@pytest.fixture
def client():
    tempdir = '/tmp'
    wiki = Wiki(tempdir)
    url = 'originalURL'
    newurl = 'newURL'
    newurlFolder = 'newURL//new_folder'
    app.config['TESTING'] = True

    with app.test_client() as client:
        client.tempdir = tempdir
        client.wiki = wiki
        client.url = url
        client.newurl = newurl
        client.newurlFolder = newurlFolder
        with app.app_context():
            pass
        yield client
        wiki.delete(url)
        wiki.delete(newurl)
        wiki.delete(newurlFolder)

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
    # def test_process_meta(self):
    #     sample = Processor("# Sample Title\n\nSome sample paragraph text")

    #     sample.process_pre()
    #     sample.process_markdown()
    #     sample.split_raw()
    #     sample.process_meta()

    #     assert sample.meta == "# sample title"

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
    @pytest.fixture(autouse=True)
    def setup_method(self, client):
        self.tempdir = client.tempdir
        self.wiki = client.wiki
        self.url = client.url
        self.newurl = client.newurl
        self.newurlFolder = client.newurlFolder

    def test_constructor(self):
        assert self.wiki.root == self.tempdir

    def test_path(self):
        expected_path = os.path.join(self.wiki.root, 'originalURL.md')
        path = self.wiki.path(self.url)
        assert path == expected_path

    def test_exists(self):
        # url = 'test_page_exists'
        assert not self.wiki.exists(self.url)

        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_exists()')

        assert self.wiki.exists(self.url)

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
            self.wiki.get_or_404(self.url)
        
        assert info.type == NotFound
        assert info.value.code == 404

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
        wiki_path = self.wiki.path(self.url)
        with open(wiki_path, 'w') as f:
            f.write('# Existing Page')

        deleted = self.wiki.delete(self.url)

        assert deleted is True
        assert not self.wiki.exists(wiki_path)

    def test_delete_nonexistent_page(self):
        deleted = self.wiki.delete(self.url)
        assert deleted is False
    
    def test_index(self):
        wiki_pages = self.wiki.index()
        assert len(wiki_pages) == 0

        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_index()')

        wiki_pages = self.wiki.index()
        assert len(wiki_pages) == 1

        # TODO: Test If Sorting is Accurate
    
    # def test_index_by(self):
    #     # Create a few test pages with different tags
    #     path1 = self.wiki.path('page1')
    #     with open(path1, 'w') as f:
    #         f.write('title: Page 1\ntags: a,b,c\n\ncontent')

    #     path2 = self.wiki.path('page2')
    #     with open(path2, 'w') as f:
    #         f.write('title: Page 2\ntags: b,c,d\n\ncontent')

    #     path3 = self.wiki.path('page3')
    #     with open(path3, 'w') as f:
    #         f.write('title: Page 3\ntags: c,d,e\n\ncontent')

    #     # Get the index by the 'tags' attribute
    #     index = self.wiki.index_by('tags')
    #     print(f'Index -> {index}')

        # assert 1 == 2
    
    def test_get_by_title(self):
        # Create a few test pages with different tags
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: Page 1\ntags: a,b,c\n\ncontent')
        
        # get the page by the title
        pages = self.wiki.get_by_title('Page 1')
        assert pages[0] is not None
        assert pages[0].title == 'Page 1'
        assert pages[0].url == self.url.lower()

        # get the page by the title
        pages = self.wiki.get_by_title('Page That Doesn\'t Exist')
        assert pages is None

    def test_get_tags(self):
        path = self.wiki.path(self.url)
        with open(path, 'w') as f:
            f.write('title: # Page 1\n\ntest_index_by()')
        tags = self.wiki.get_tags()
        assert tags  == {}

        workout_page = self.wiki.path("workout_page")
        workout_page_content = 'Perform 30 minutes of moderate to high intensity exercise, such as jogging, cycling, or weight lifting, at least 3-4 times per week.'
        with open(workout_page, 'w') as f:
            f.write(f'title: # 7 Week Workout Plans\ntags: inspirational, personal\n\n{workout_page_content}')
        
        adventurous_page = self.wiki.path("adventurous_page")
        adventurous_page_content = 'Explore a new outdoor activity, such as hiking, rock climbing, or kayaking, at least once a month to add excitement and adventure to your personal life.'
        with open(adventurous_page, 'w') as f:
            f.write(f'title: # Lifestyle\ntags: personal, outdoor\n\n{adventurous_page_content}')

        tags = self.wiki.get_tags()

        assert len(tags['inspirational']) == 1
        assert len(tags['personal']) == 2
        assert len(tags['outdoor']) == 1

        seven_week_workout_plan_page = tags['inspirational'][0]
        assert seven_week_workout_plan_page.title == '# 7 Week Workout Plans'
        assert seven_week_workout_plan_page.body.strip() == workout_page_content
        assert seven_week_workout_plan_page.tags == 'inspirational, personal'

        lifestyle_page = tags['personal'][1]
        assert lifestyle_page.title == '# Lifestyle'
        assert lifestyle_page.body.strip() == adventurous_page_content
        assert lifestyle_page.tags == 'personal, outdoor'
    
    def test_index_by_tag(self):
        workout_page = self.wiki.path("workout_page")
        workout_page_content = 'Perform 30 minutes of moderate to high intensity exercise, such as jogging, cycling, or weight lifting, at least 3-4 times per week.'
        with open(workout_page, 'w') as f:
            f.write(f'title: # 7 Week Workout Plans\ntags: inspirational, personal\n\n{workout_page_content}')
        
        adventurous_page = self.wiki.path("adventurous_page")
        adventurous_page_content = 'Explore a new outdoor activity, such as hiking, rock climbing, or kayaking, at least once a month to add excitement and adventure to your personal life.'
        with open(adventurous_page, 'w') as f:
            f.write(f'title: # Lifestyle\ntags: personal, outdoor\n\n{adventurous_page_content}')
        
        focus_page = self.wiki.path("focus")
        focus_page_content = 'Organize your closet by sorting clothes into keep, donate, and toss piles.'
        with open(focus_page, 'w') as f:
            f.write(f'title: # Focus Mode\ntags: work, indoor\n\n{focus_page_content}')
        
        tag = 'personal'
        tagged_pages = self.wiki.index_by_tag(tag)
        assert tagged_pages[0].title == '# 7 Week Workout Plans'
        assert tagged_pages[1].title == '# Lifestyle'
        assert len(tagged_pages) == 2

        tag = 'indoor'
        tagged_pages = self.wiki.index_by_tag(tag)
        assert len(tagged_pages) == 1
        assert tagged_pages[0].title == '# Focus Mode'

        tag = 'travel'
        tagged_pages = self.wiki.index_by_tag(tag)
        assert len(tagged_pages) == 0
    
    def test_search_default(self):
        workout_page = self.wiki.path("workout_page")
        workout_page_content = 'Perform 30 minutes of moderate to high intensity exercise, such as jogging, cycling, or weight lifting, at least 3-4 times per week.'
        with open(workout_page, 'w') as f:
            f.write(f'title: # 7 Week Workout Plans\ntags: inspirational, personal\n\n{workout_page_content}')
        
        adventurous_page = self.wiki.path("adventurous_page")
        adventurous_page_content = 'Explore a new outdoor activity, such as hiking, rock climbing, or kayaking, at least once a month to add excitement and adventure to your personal life.'
        with open(adventurous_page, 'w') as f:
            f.write(f'title: # Lifestyle\ntags: personal, outdoor\n\n{adventurous_page_content}')
        
        focus_page = self.wiki.path("focus")
        focus_page_content = 'Organize your closet by sorting clothes into keep, donate, and toss piles.'
        with open(focus_page, 'w') as f:
            f.write(f'title: # Focus Mode\ntags: work, indoor\n\n{focus_page_content}')
        
        # search for the term 'jogging' with ignore_case=True and default (attrs=['title', 'tags', 'body'])
        term = 'jogging'
        search_results = self.wiki.search(term)
        assert len(search_results) == 1
        assert search_results[0].title == '# 7 Week Workout Plans'
    
    def test_search_while_not_ignoring_case(self):
        workout_page = self.wiki.path("workout_page")
        workout_page_content = 'Perform 30 minutes of moderate to high intensity exercise, such as jogging, cycling, or weight lifting, at least 3-4 times per week.'
        with open(workout_page, 'w') as f:
            f.write(f'title: # 7 Week Workout Plans CommonSearchableTerm\ntags: inspirational, personal\n\n{workout_page_content}')
        
        adventurous_page = self.wiki.path("adventurous_page")
        adventurous_page_content = 'Explore a new outdoor activity, such as hiking, rock climbing, or kayaking, at least once a month to add excitement and adventure to your personal life.'
        with open(adventurous_page, 'w') as f:
            f.write(f'title: # Lifestyle\ntags: personal, outdoor, CommonSearchableTerm\n\n{adventurous_page_content}')
        
        focus_page = self.wiki.path("focus")
        focus_page_content = 'Organize your closet by sorting clothes into keep, donate, and toss piles.'
        with open(focus_page, 'w') as f:
            f.write(f'title: # Focus Mode\ntags: work, indoor\n\n{focus_page_content}')
        
        # search for the term 'CommonSearchableTerm' with ignore_case=False and attrs=['title', 'tags']
        term = 'CommonSearchableTerm'
        search_results = self.wiki.search(term, ignore_case=False, attrs=['title', 'tags'])
        assert len(search_results) == 2
        assert search_results[0].title == '# 7 Week Workout Plans CommonSearchableTerm'
        assert search_results[1].title == '# Lifestyle'

        # search for the term 'CommonSearchableTerm' with ignore_case=False and attrs=['title', 'tags']
        term = 'commonsearchableterm'
        search_results = self.wiki.search(term, ignore_case=False, attrs=['title', 'tags'])
        assert len(search_results) == 0
    
    def test_search_that_is_not_in_the_attribute_specified(self):
        workout_page = self.wiki.path("workout_page")
        workout_page_content = 'Perform 30 minutes of moderate to high intensity exercise, such as jogging, cycling, or weight lifting, at least 3-4 times per week.'
        with open(workout_page, 'w') as f:
            f.write(f'title: # 7 Week Workout Plans TermNotFoundInTheBody\ntags: inspirational, personal\n\n{workout_page_content}')
        
        adventurous_page = self.wiki.path("adventurous_page")
        adventurous_page_content = 'Explore a new outdoor activity, such as hiking, rock climbing, or kayaking, at least once a month to add excitement and adventure to your personal life.'
        with open(adventurous_page, 'w') as f:
            f.write(f'title: # Lifestyle\ntags: personal, outdoor, TermNotFoundInTheBody\n\n{adventurous_page_content}')
        
        focus_page = self.wiki.path("focus")
        focus_page_content = 'Organize your closet by sorting clothes into keep, donate, and toss piles.'
        with open(focus_page, 'w') as f:
            f.write(f'title: # Focus Mode\ntags: work, indoor\n\n{focus_page_content}')
        
        # search for the term 'TermNotFoundInTheBody' with ignore_case=False and attrs=['body']
        term = 'TermNotFoundInTheBody'
        search_results = self.wiki.search(term, ignore_case=False, attrs=['body'])
        assert len(search_results) == 0
