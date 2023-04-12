"""
    Wiki core
    ~~~~~~~~~
"""
from collections import OrderedDict
from PIL import Image
from io import open
import os
import re

from flask import abort
from flask import url_for
import markdown
import config
import hashlib

import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

from bs4 import BeautifulSoup
import markdown

def clean_url(url):
    """
        Cleans the url and corrects various errors. Removes multiple
        spaces and all leading and trailing spaces. Changes spaces
        to underscores and makes all characters lowercase. Also
        takes care of Windows style folders use.

        :param str url: the url to clean


        :returns: the cleaned url
        :rtype: str
    """
    url = re.sub('[ ]{2,}', ' ', url).strip()
    url = url.lower().replace(' ', '_')
    url = url.replace('\\\\', '/').replace('\\', '/')
    return url


def wikilink(text, url_formatter=None):
    """
        Processes Wikilink syntax "[[Link]]" within the html body.
        This is intended to be run after content has been processed
        by markdown and is already HTML.

        :param str text: the html to highlight wiki links in.
        :param function url_formatter: which URL formatter to use,
            will by default use the flask url formatter

        Syntax:
            This accepts Wikilink syntax in the form of [[WikiLink]] or
            [[url/location|LinkName]]. Everything is referenced from the
            base location "/", therefore sub-pages need to use the
            [[page/subpage|Subpage]].

        :returns: the processed html
        :rtype: str
    """
    if url_formatter is None:
        url_formatter = url_for
    link_regex = re.compile(
        r"((?<!\<code\>)\[\[([^<].+?) \s*([|] \s* (.+?) \s*)?]])",
        re.X | re.U
    )
    for i in link_regex.findall(text):
        title = [i[-1] if i[-1] else i[1]][0]
        url = clean_url(i[1])
        html_url = "<a href='{0}'>{1}</a>".format(
            url_formatter('wiki.display', url=url),
            title
        )
        text = re.sub(link_regex, html_url, text, count=1)
    return text


class Processor(object):
    """
        The processor handles the processing of file content into
        metadata and markdown and takes care of the rendering.

        It also offers some helper methods that can be used for various
        cases.
    """

    preprocessors = []
    postprocessors = [wikilink]

    def __init__(self, text):
        """
            Initialization of the processor.

            :param str text: the text to process
        """
        self.md = markdown.Markdown(extensions=[
            'codehilite',
            'fenced_code',
            'meta',
            'tables'
        ])
        self.input = text
        self.markdown = None
        self.meta_raw = None

        self.pre = None
        self.html = None
        self.final = None
        self.meta = None

    def process_pre(self):
        """
            Content preprocessor.
        """
        current = self.input
        for processor in self.preprocessors:
            current = processor(current)
        self.pre = current

    def process_markdown(self):
        """
            Convert to HTML.
        """
        self.html = self.md.convert(self.pre)


    def split_raw(self):
        """
            Split text into raw meta and content.
        """
        self.meta_raw, self.markdown = self.pre.split('\n\n', 1)

    def process_meta(self):
        """
            Get metadata.

            .. warning:: Can only be called after :meth:`html` was
                called.
        """
        # the markdown meta plugin does not retain the order of the
        # entries, so we have to loop over the meta values a second
        # time to put them into a dictionary in the correct order
        self.meta = OrderedDict()
        for line in self.meta_raw.split('\n'):
            key = line.split(':', 1)[0]
            # markdown metadata always returns a list of lines, we will
            # reverse that here
            self.meta[key.lower()] = \
                '\n'.join(self.md.Meta[key.lower()])

    def process_post(self):
        """
            Content postprocessor.
        """
        current = self.html
        for processor in self.postprocessors:
            current = processor(current)
        self.final = current

    def process(self):
        """
            Runs the full suite of processing on the given text, all
            pre and post processing, markdown rendering and meta data
            handling.
        """
        self.process_pre()
        self.process_markdown()
        self.split_raw()
        self.process_meta()
        self.process_post()

        return self.final, self.markdown, self.meta


class Page(object):
    def __init__(self, path, url, new=False):
            # Initialize instance variables with provided values
            self.path = path
            self.url = url
            self.id = hashlib.sha256(self.url.encode('utf-8')).hexdigest()[:16]
    
            # Create an empty ordered dictionary for storing metadata
            self._meta = OrderedDict()
    
            # Load and render the page contents if this is not a new page
            if not new:
                self.load()   # Load page contents from file at `path` into instance
                self.render() # Render page as HTML      
    def __repr__(self):
        return "<Page: {}@{}>".format(self.url, self.path)

    def load(self):
            # Open the file at `path` in read mode using UTF-8 encoding
            with open(self.path, 'r', encoding='utf-8') as f:
                # Read the contents of the file and store them in the instance's `content` attribute
                self.content = f.read()

    def render(self):
        # Create a `Processor` object to process the page content
        processor = Processor(self.content)

        # Process the content and store the resulting HTML, body, and metadata in instance variables
        self._html, self.body, self._meta = processor.process()

    def save(self, update=True):
        # Get the directory containing the page file
        folder = os.path.dirname(self.path)

        # If the directory does not exist, create it
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Write metadata and page body to the page file
        with open(self.path, 'w', encoding='utf-8') as f:
            # Write metadata to the file in the format `key: value`
            for key, value in list(self._meta.items()):
                line = '%s: %s\n' % (key, value)
                f.write(line)

            # Write a newline character after the metadata
            f.write('\n')

            # Write the page body to the file, replacing Windows-style line endings with Unix-style line endings
            f.write(self.body.replace('\r\n', '\n'))

        # Reload and re-render the page if `update` is True
        if update:
            self.load()   # Load updated content from file into instance
            self.render() # Render updated content as HTML and update instance variables

    @property
    def meta(self):
        # Returns an ordered dictionary containing metadata for the page
        return self._meta

    def __getitem__(self, name):
        # Returns the value associated with a given metadata key
        return self._meta[name]

    def __setitem__(self, name, value):
        # Sets the value associated with a given metadata key
        self._meta[name] = value

    @property
    def html(self):
        # Returns the HTML code for the page
        return self._html

    def __html__(self):
        # Returns the HTML code for the page (used by certain frameworks and libraries)
        return self.html

    @property
    def title(self):
        # Tries to get the "title" metadata field; if it doesn't exist, returns the page URL
        try:
            return self['title']
        except KeyError:
            return self.url

    @title.setter
    def title(self, value):
        # Sets the "title" metadata field
        self['title'] = value

    @property
    def tags(self):
        # Tries to get the "tags" metadata field; if it doesn't exist, returns an empty string
        try:
            return self['tags']
        except KeyError:
            return ""

    @tags.setter
    def tags(self, value):
        # Sets the "tags" metadata field
        self['tags'] = value

    def get_page_text(self):
        # Extract the text content from the HTML body using Beautiful Soup
        body_text = BeautifulSoup(self.html, 'html.parser').get_text()
        # Concatenate the body text and title into a single string with a space in between
        return (body_text + " " + self.title)

    def tokenize(self, page_text):
        # Tokenize the lower case page text
        return word_tokenize(page_text.lower())

    def remove_stopwords(self, tokens):
        # Get a list of English stopwords
        english_stopwords = stopwords.words('english')
        return [t for t in tokens if t not in english_stopwords]
    
    def token_frequency(self, tokens_wo_stopwords):
        return dict(Counter(tokens_wo_stopwords))


    def tokenize_and_count(self):
        # Get page text without markdown
        page_text = self.get_page_text()

        # Tokenize the page text
        tokens = self.tokenize(page_text)

        # Remove stopwords from tokens
        tokens_wo_stopwords = self.remove_stopwords(tokens)

        # translate remaining tokens into dictionary of pairs [token -> token count]
        token_freq = self.token_frequency(tokens_wo_stopwords)

        # Return the dictionary of word frequencies
        return token_freq
        

class Wiki(object):
    def __init__(self, root):
        self.root = root

    def path(self, url):
        return os.path.join(self.root, url + '.md')

    def exists(self, url):
        path = self.path(url)
        return os.path.exists(path)

    def get(self, url):
        path = self.path(url)
        #path = os.path.join(self.root, url + '.md')
        if self.exists(url):
            return Page(path, url)
        return None

    def get_or_404(self, url):
        page = self.get(url)
        if page:
            return page
        abort(404)

    def get_bare(self, url):
        path = self.path(url)
        if self.exists(url):
            return False
        return Page(path, url, new=True)

    def move(self, url, newurl):
        source = os.path.join(self.root, url) + '.md'
        target = os.path.join(self.root, newurl) + '.md'
        # normalize root path (just in case somebody defined it absolute,
        # having some '../' inside) to correctly compare it to the target
        root = os.path.normpath(self.root)
        # get root path longest common prefix with normalized target path
        common = os.path.commonprefix((root, os.path.normpath(target)))
        # common prefix length must be at least as root length is
        # otherwise there are probably some '..' links in target path leading
        # us outside defined root directory
        if len(common) < len(root):
            raise RuntimeError(
                'Possible write attempt outside content directory: '
                '%s' % newurl)
        # create folder if it does not exists yet
        folder = os.path.dirname(target)
        if not os.path.exists(folder):
            os.makedirs(folder)
        os.rename(source, target)

    def delete(self, url):
        path = self.path(url)
        if not self.exists(url):
            return False
        os.remove(path)
        return True

    def index(self):
        """
            Builds up a list of all the available pages.

            :returns: a list of all the wiki pages
            :rtype: list
        """
        # make sure we always have the absolute path for fixing the
        # walk path
        pages = []
        root = os.path.abspath(self.root)
        for cur_dir, _, files in os.walk(root):
            # get the url of the current directory
            cur_dir_url = cur_dir[len(root)+1:]
            for cur_file in files:
                path = os.path.join(cur_dir, cur_file)
                if cur_file.endswith('.md'):
                    url = clean_url(os.path.join(cur_dir_url, cur_file[:-3]))
                    page = Page(path, url)
                    pages.append(page)
        return sorted(pages, key=lambda x: x.title.lower())

    def index_by(self, key):
        """
            Get an index based on the given key.

            Will use the metadata value of the given key to group
            the existing pages.

            :param str key: the attribute to group the index on.

            :returns: Will return a dictionary where each entry holds
                a list of pages that share the given attribute.
            :rtype: dict
        """
        pages = {}
        for page in self.index():
            value = getattr(page, key)
            pre = pages.get(value, [])
            pages[value] = pre.append(page)
        return pages

    def get_by_title(self, title):
        pages = self.index(attr='title')
        return pages.get(title)

    def get_tags(self):
        pages = self.index()
        tags = {}
        for page in pages:
            pagetags = page.tags.split(',')
            for tag in pagetags:
                tag = tag.strip()
                if tag == '':
                    continue
                elif tags.get(tag):
                    tags[tag].append(page)
                else:
                    tags[tag] = [page]
        return tags

    def index_by_tag(self, tag):
        pages = self.index()
        tagged = []
        for page in pages:
            if tag in page.tags:
                tagged.append(page)
        return sorted(tagged, key=lambda x: x.title.lower())

    def search(self, term, ignore_case=True, attrs=['title', 'tags', 'body']):
        pages = self.index()
        regex = re.compile(term, re.IGNORECASE if ignore_case else 0)
        matched = []
        for page in pages:
            for attr in attrs:
                if regex.search(getattr(page, attr)):
                    matched.append(page)
                    break
        return matched
    
    # For image uploading
    def allowed_file(self, filename): 
        ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def save_image(self, image):
        path = os.path.join(config.PIC_BASE, image.filename)
        image.save(path)
