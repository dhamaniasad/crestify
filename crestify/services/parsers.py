import HTMLParser
import time
from bs4 import BeautifulSoup as BeautifulSoup4
from BeautifulSoup import BeautifulSoup as BeautifulSoup3
import re
import datetime
from lxml import html
import arrow
import ujson
from crestify.models import db, Bookmark, Tag
import os
from crestify import app


class Parser:
    def __init__(self, file_name, user_id):
        with open(file_name, 'r') as self.opened_file:
            self.html = self.opened_file.read()
        self.user = user_id
        self.soup = BeautifulSoup3(self.html)
        self.urls = dict()  # Store processed bookmarks in this dict
        self.check_duplicates = dict()  # Store all current bookmarks for the user
        self.check_duplicates_query = Bookmark.query.filter(Bookmark.user == self.user,
                                                            Bookmark.deleted == False).all()
        for bookmark in self.check_duplicates_query:
            self.check_duplicates[bookmark.main_url] = bookmark
        self.tags_dict = dict()  # Store tag objects for imported bookmarks
        self.tags_set = set()  # Keep track of all tags in the import file
        """
        There is a trade-off here. Only bookmarks that existed
        before the import function is called will be considered
        duplicates.
        Doing otherwise required getting back ids from created
        bookmarks, which required doing a session.flush(),
        which caused speed to drop considerably.
        If a import has multiple duplicate urls, only one will
        be added, due to dict keys being unique.
        """
        self.html_parser = HTMLParser.HTMLParser()
        self.valid_url = re.compile(
            r'^(?:[a-z0-9\.\-]*)://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def process(self):
        tags_query = Tag.query.all()  # Get all the tags
        tags_dictionary = {}  # Storing objects for existing tags in this dict
        for this_tag in tags_query:
            tags_dictionary[this_tag.text] = this_tag  # Store all existing tags in dict
        created_tags = {}  # Store all tags that had to be created
        urls = self.soup.findAll('a')
        for link in urls:
            url = link['href']
            if not self.valid_url.match(url):
                pass
            else:
                if url in self.urls:
                    pass
                else:
                    tags = ['Imported']
                    if link.has_key('add_date'):
                        added_timestamp = int(link['add_date'])
                    else:
                        added_timestamp = time.time()
                    self.urls[url] = {
                        'title': link.text,
                        'tags': tags,
                        'added_on': datetime.datetime.utcfromtimestamp(
                            added_timestamp)
                    }
        self.tags_set.add('Imported')
        for tag in self.tags_set:
            if tag in self.tags_dict:  # Tag has already been processed
                pass
            elif tag in created_tags:
                pass
            elif tag in tags_dictionary:
                self.tags_dict[tag] = {'obj': tags_dictionary[tag]}
            else:
                created_tags[tag] = ''
                new_tag = Tag()
                new_tag.text = tag
                db.session.add(new_tag)
        db.session.commit()
        q = Tag.query.all()
        for tag in q:
            if tag.text in created_tags:
                self.tags_dict[tag.text] = {'obj': tag}

    def add_to_database(self):
        len_urls = len(self.urls.items())
        if len_urls > 400000:
            print "Sorry, cannot import, way too many bookmarks."
            return
        counter = 0
        for url, metadata in self.urls.items():
            counter += 1
            if counter != len_urls:
                if not url in self.check_duplicates:
                    self.transfer(title=self.html_parser.unescape(metadata['title']),
                                  url=self.html_parser.unescape(url),
                                  date=metadata['added_on'],
                                  user=self.user,
                                  tags=metadata['tags'])
                else:
                    self.edit(obj=self.check_duplicates[url],
                              tags=metadata['tags'])
            else:
                self.transfer(title=self.html_parser.unescape(metadata['title']),
                              url=self.html_parser.unescape(url),
                              date=metadata['added_on'],
                              user=self.user,
                              tags=metadata['tags'],
                              commit=True)

    def transfer(self,
                 title,
                 url,
                 date,
                 user,
                 tags,
                 commit=False):
        with db.session.no_autoflush:
            import_bookmark = Bookmark()
            import_bookmark.main_url = url[:2000]
            import_bookmark.title = title[:1024]
            import_bookmark.user = user
            import_bookmark.added_on = date
            import_bookmark.description = None
            import_bookmark.deleted = False
            for tag in tags:
                import_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])
            db.session.add(import_bookmark)
            if commit is True:
                db.session.commit()

    def edit(self, obj, tags):
        with db.session.no_autoflush:
            edit_bookmark = obj
            for tag in tags:
                if tag not in edit_bookmark.tags:
                    edit_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])


class PinboardParser:
    def __init__(self, file_name, user_id):
        """
        Reads data from file, loads it as JSON
        """
        with open(file_name, 'r') as self.opened_file:
            self.data = self.opened_file.read()
        self.user = user_id
        self.data = ujson.loads(self.data)
        self.urls = dict()  # Keeps track of all the urls in the import file, used when adding to db
        self.tags_dict = dict()  # Store tag objects for imported bookmarks
        self.tags_set = set()  # Keeps track of all the tags in the import file
        self.check_duplicates = dict()  # Store all current bookmarks for the user
        self.check_duplicates_query = Bookmark.query.filter(Bookmark.user == self.user,
                                                            Bookmark.deleted == False).all()
        for x in self.check_duplicates_query:
            self.check_duplicates[x.main_url] = x  # Add bookmark object to dict
        self.html_parser = HTMLParser.HTMLParser()
        self.valid_url = re.compile(
            r'^(?:[a-z0-9\.\-]*)://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)  # We only want valid URLs in the database

    def process(self):
        tags_query = Tag.query.all()  # Get all the tags
        tags_dictionary = {}  # Storing objects for existing tags in here.
        for individ_tag in tags_query:
            tags_dictionary[individ_tag.text] = individ_tag  # Store all existing tags in dict
        created_tags = {}  # Store all tags that had to be created
        for link in self.data:
            url = link['href']
            if not self.valid_url.match(url):  # If the url is not valid, burn it
                pass
            else:
                try:
                    title = link['description']
                except KeyError:
                    title = link['href']
                try:
                    tags = link['tags'].split(' ')
                except KeyError:
                    tags = []
                tags = filter(None, tags)  # Remove empty strings from tag list
                tags.append('Imported')  # This is used as a way of keeping track of Imported bookmarks in the db
                try:
                    # Pinboard stores timestamps in ISO format in UTC
                    added_timestamp = datetime.datetime.strptime(link['time'], '%Y-%m-%dT%H:%M:%SZ')
                except KeyError:
                    added_timestamp = datetime.datetime.utcnow()  # This should never happen, but just in case
                try:
                    # Don't want empty strings in the database, creates need for extra logic in the templates
                    description = link['extended'] if link['extended'] != '' else None
                except KeyError:
                    description = None
                self.urls[url] = {
                    'title': title,
                    'tags': tags,
                    'added_on': added_timestamp,
                    'description': description
                }
                for tag in tags:
                    self.tags_set.add(tag)  # Add all tags from current bookmark to the master tag set. No dupes.
        for tag in self.tags_set:
            if tag in self.tags_dict:  # This tag has already been processed, and is in dict
                pass
            elif tag in created_tags:  # We won't be handle created tags in this loop
                pass
            elif tag in tags_dictionary:  # This tag already exists in the database
                self.tags_dict[tag] = {'obj': tags_dictionary[tag]}  # Add the tag to the main tags object dictionary
            else:  # If all else fails, create this tag
                created_tags[tag] = ''
                new_tag = Tag()
                new_tag.text = tag
                db.session.add(new_tag)
        db.session.commit()  # This takes pretty long
        q = Tag.query.all()
        for tag in q:  # Here we check if this was one of the tags that had to be created, and add to main tags dict
            if tag.text in created_tags:
                self.tags_dict[tag.text] = {'obj': tag}

    def add_to_database(self):
        len_urls = len(self.urls.items())
        if len_urls > 400000:
            print "Sorry, cannot import, way too many bookmarks."
            return
        counter = 0
        for url, metadata in self.urls.items():
            counter += 1
            if counter != len_urls:
                if url not in self.check_duplicates:
                    self.transfer(title=self.html_parser.unescape(metadata['title']),
                                  url=self.html_parser.unescape(url),
                                  date=metadata['added_on'],
                                  user=self.user,
                                  tags=metadata['tags'], description=metadata['description'])
                else:
                    self.edit(obj=self.check_duplicates[url], tags=metadata['tags'])
            else:  # won't do duplicate check for last bookmark. 1 duplicate is not too much of a problem.
                self.transfer(title=self.html_parser.unescape(metadata['title']),
                              url=self.html_parser.unescape(url), date=metadata['added_on'], user=self.user,
                              tags=metadata['tags'], description=metadata['description'], commit=True)

    def transfer(self,
                 title,
                 url,
                 date,
                 user,
                 tags,
                 description=None,
                 commit=False):
        with db.session.no_autoflush:  # F-SA has autoflush on by default, which causes severe performance degradation
            import_bookmark = Bookmark()
            import_bookmark.main_url = url[:2000]
            import_bookmark.title = title[:1024]
            import_bookmark.description = None
            import_bookmark.user = user
            import_bookmark.added_on = date
            if description is None:
                import_bookmark.description = None
            else:
                import_bookmark.description = description[:256]
            import_bookmark.deleted = False
            for tag in tags:  # Append the tag object from the tags dict.
                # Doing append on the assoc. proxy causes new tags to be created
                import_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])
            db.session.add(import_bookmark)
            if commit is True:
                db.session.commit()

    def edit(self, obj, tags=None):
        with db.session.no_autoflush:  # F-SA has autoflush on by default, which causes severe performance degradation
            edit_bookmark = obj  # Will be modifying the stored bookmark object here, to avoid extra queries
            for tag in tags:
                if tag not in edit_bookmark.tags:
                    edit_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])


class InstapaperParser:
    def __init__(self, file_name, user_id):
        with open(file_name, 'r') as self.opened_file:
            #  So Instapaper doesn't close <li> tags
            #  This was causing infinite recursion when using BS directly
            #  Hence why the stuff below is being done, so that the <li> tags get closed
            self.html = html.document_fromstring(self.opened_file.read())
            self.html = html.tostring(self.html)
        self.soup = BeautifulSoup4(self.html)
        self.user = user_id
        self.urls = dict()
        self.check_duplicates = dict()
        self.check_duplicates_query = Bookmark.query.filter(Bookmark.user == self.user,
                                                            Bookmark.deleted == False).all()
        for bmark in self.check_duplicates_query:
            self.check_duplicates[bmark.main_url] = bmark
        self.tags_dict = dict()
        self.tags_set = set()
        self.valid_url = re.compile(
            r'^(?:[a-z0-9\.\-]*)://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def process(self):
        tags_query = Tag.query.all()
        tags_dictionary = dict()
        for this_tag in tags_query:
            tags_dictionary[this_tag.text] = this_tag
        created_tags = dict()
        for tag in self.soup.find_all('h1'):
            self.tags_set.add(tag.text)
            parent_elem = tag.find_next_sibling('ol')
            links = parent_elem.find_all('a')
            for link in links:
                if not self.valid_url.match(link['href']):
                    pass
                else:
                    title = link.text
                    url = link['href']
                    tags = [tag.text]
                    tags.append('Imported')
                    #  Thanks Instapaper for not adding timestamps
                    added_timestamp = datetime.datetime.utcnow()
                    self.urls[url] = {
                        'title': title,
                        'tags': tags,
                        'added_on': added_timestamp
                    }
        self.tags_set.add('Imported')
        for tag in self.tags_set:
            if tag in self.tags_dict:
                pass
            elif tag in created_tags:
                pass
            elif tag in tags_dictionary:
                self.tags_dict[tag] = {'obj': tags_dictionary[tag]}
            else:
                created_tags[tag] = ''
                new_tag = Tag()
                new_tag.text = tag
                db.session.add(new_tag)
        db.session.commit()
        q = Tag.query.all()
        for tag in q:
            if tag.text in created_tags:
                self.tags_dict[tag.text] = {'obj': tag}

    def add_to_database(self):
        len_urls = len(self.urls.items())
        if len_urls > 400000:
            print "Sorry, cannot import, way too many bookmarks."
            return
        counter = 0
        for url, metadata in self.urls.items():
            counter += 1
            if counter != len_urls:
                if url not in self.check_duplicates:
                    self.transfer(title=metadata['title'],
                                  url=url,
                                  date=metadata['added_on'],
                                  user=self.user,
                                  tags=metadata['tags'])
                else:
                    self.edit(obj=self.check_duplicates[url],
                              tags=metadata['tags'])
            else:
                self.transfer(title=metadata['title'],
                              url=url,
                              date=metadata['added_on'],
                              user=self.user,
                              tags=metadata['tags'],
                              commit=True
                              )

    def transfer(self,
                 title,
                 url,
                 date,
                 user,
                 tags,
                 commit=False):
        with db.session.no_autoflush:
            import_bookmark = Bookmark()
            import_bookmark.main_url = url[:2000]
            import_bookmark.title = title[:1024]
            import_bookmark.description = None
            import_bookmark.user = user
            import_bookmark.added_on = date
            import_bookmark.deleted = False
            for tag in tags:
                import_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])
            db.session.add(import_bookmark)
            if commit is True:
                db.session.commit()

    def edit(self, obj, tags):
        with db.session.no_autoflush:
            edit_bookmark = obj
            for tag in tags:
                if tag not in edit_bookmark.tags:
                    edit_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])


class PocketParser:
    def __init__(self, file_name, user_id):
        with open(file_name, 'r') as self.opened_file:
            self.html = self.opened_file.read()
        self.soup = BeautifulSoup4(self.html)
        self.user = user_id
        self.urls = dict()
        self.check_duplicates = dict()
        self.check_duplicates_query = Bookmark.query.filter(Bookmark.user == self.user,
                                                            Bookmark.deleted == False).all()
        for bmark in self.check_duplicates_query:
            self.check_duplicates[bmark.main_url] = bmark
        self.tags_dict = dict()
        self.tags_set = set()
        self.html_parser = HTMLParser.HTMLParser()
        self.valid_url = re.compile(
            r'^(?:[a-z0-9\.\-]*)://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def process(self):
        tags_query = Tag.query.all()
        tags_dictionary = dict()
        for this_tag in tags_query:
            tags_dictionary[this_tag.text] = this_tag
        created_tags = dict()
        for link in self.soup.find_all('a'):
            title = link.text
            url = link['href']
            dt = arrow.get(link['time_added']).naive
            tags = link['tags'].split(',')
            tags.append('Imported')
            tags = filter(None, tags)
            for tag in tags:
                self.tags_set.add(tag)
            self.urls[url] = {
                'title': title,
                'tags': tags,
                'added_on': dt
            }
        for tag in self.tags_set:
            if tag in self.tags_dict:  # Tag has already been processed
                pass
            elif tag in created_tags:
                pass
            elif tag in tags_dictionary:
                self.tags_dict[tag] = {'obj': tags_dictionary[tag]}
            else:
                created_tags[tag] = ''
                new_tag = Tag()
                new_tag.text = tag
                db.session.add(new_tag)
        db.session.commit()
        q = Tag.query.all()
        for tag in q:
            if tag.text in created_tags:
                self.tags_dict[tag.text] = {'obj': tag}

    def add_to_database(self):
        len_urls = len(self.urls.items())
        if len_urls > 400000:
            print "Sorry, cannot import, way too many bookmarks."
            return
        counter = 0
        for url, metadata in self.urls.items():
            counter += 1
            if counter != len_urls:
                if url not in self.check_duplicates:
                    self.transfer(title=self.html_parser.unescape(metadata['title']),
                                  url=self.html_parser.unescape(url),
                                  date=metadata['added_on'],
                                  user=self.user,
                                  tags=metadata['tags'])
                else:
                    self.edit(obj=self.check_duplicates[url], tags=metadata['tags'])
            else:  # won't do duplicate check for last bookmark. 1 duplicate is not too much of a problem.
                self.transfer(title=self.html_parser.unescape(metadata['title']),
                              url=self.html_parser.unescape(url), date=metadata['added_on'], user=self.user,
                              tags=metadata['tags'], commit=True)

    def transfer(self,
                 title,
                 url,
                 date,
                 user,
                 tags,
                 commit=False):
        with db.session.no_autoflush:
            import_bookmark = Bookmark()
            import_bookmark.main_url = url[:2000]
            import_bookmark.title = title[:1024]
            import_bookmark.user = user
            import_bookmark.added_on = date
            import_bookmark.description = None
            import_bookmark.deleted = False
            for tag in tags:
                import_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])
            db.session.add(import_bookmark)
            if commit is True:
                db.session.commit()

    def edit(self, obj, tags):
        with db.session.no_autoflush:
            edit_bookmark = obj
            for tag in tags:
                if tag not in edit_bookmark.tags:
                    edit_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])


class ReadabilityParser:
    def __init__(self, file_name, user_id):
        with open(file_name, 'r') as self.opened_file:
            self.data = self.opened_file.read()
        self.user = user_id
        self.data = ujson.loads(self.data)
        self.urls = dict()
        self.tags_dict = dict()
        self.tags_set = set()
        self.check_duplicates = dict()
        self.check_duplicates_query = Bookmark.query.filter(Bookmark.user == self.user,
                                                            Bookmark.deleted == False).all()
        for x in self.check_duplicates_query:
            self.check_duplicates[x.main_url] = x
        self.html_parser = HTMLParser.HTMLParser()
        self.valid_url = re.compile(
            r'^(?:[a-z0-9\.\-]*)://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def process(self):
        tags_query = Tag.query.all()
        tags_dictionary = {}
        for individ_tag in tags_query:
            tags_dictionary[individ_tag.text] = individ_tag
        created_tags = {}
        bookmarks = self.data['bookmarks']
        for bookmark in bookmarks:
            title = bookmark['article__title']
            url = bookmark['article__url']
            dt = arrow.get(bookmark['date_added']).naive
            tags = ['Imported']
            if bookmark['article__excerpt'] is not None:
                description = self.html_parser.unescape(bookmark['article__excerpt'])
            else:
                description = None
            self.urls[url] = {
                'title': title,
                'added_on': dt,
                'tags': tags,
                'description': description
            }
        if 'Imported' in tags_dictionary:
            self.tags_dict['Imported'] = {'obj': tags_dictionary['Imported']}
        else:
            new_tag = Tag()
            new_tag.text = 'Imported'
            db.session.add(new_tag)
            db.session.commit()
            self.tags_dict[new_tag.text] = {'obj': new_tag}

    def add_to_database(self):
        len_urls = len(self.urls.items())
        if len_urls > 400000:
            print "Sorry, cannot import, way too many bookmarks."
            return
        counter = 0
        for url, metadata in self.urls.items():
            counter += 1
            if counter != len_urls:
                if url not in self.check_duplicates:
                    self.transfer(title=self.html_parser.unescape(metadata['title']),
                                  url=self.html_parser.unescape(url),
                                  date=metadata['added_on'],
                                  user=self.user,
                                  tags=metadata['tags'], description=metadata['description'])
                else:
                    self.edit(obj=self.check_duplicates[url], tags=metadata['tags'])
            else:  # won't do duplicate check for last bookmark. 1 duplicate is not too much of a problem.
                self.transfer(title=self.html_parser.unescape(metadata['title']),
                              url=self.html_parser.unescape(url), date=metadata['added_on'], user=self.user,
                              tags=metadata['tags'], description=metadata['description'], commit=True)

    def transfer(self,
                 title,
                 url,
                 date,
                 user,
                 tags,
                 description=None,
                 commit=False):
        with db.session.no_autoflush:  # F-SA has autoflush on by default, which causes severe performance degradation
            import_bookmark = Bookmark()
            import_bookmark.main_url = url[:2000]
            import_bookmark.title = title[:1024]
            import_bookmark.description = None
            import_bookmark.user = user
            import_bookmark.added_on = date
            if description is None:
                import_bookmark.description = None
            else:
                import_bookmark.description = description[:256]
            import_bookmark.deleted = False
            for tag in tags:  # Append the tag object from the tags dict.
                # Doing append on the assoc. proxy causes new tags to be created
                import_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])
            db.session.add(import_bookmark)
            if commit is True:
                db.session.commit()

    def edit(self, obj, tags=None):
        with db.session.no_autoflush:  # F-SA has autoflush on by default, which causes severe performance degradation
            edit_bookmark = obj  # Will be modifying the stored bookmark object here, to avoid extra queries
            for tag in tags:
                if tag not in edit_bookmark.tags:
                    edit_bookmark.tags_relationship.append(self.tags_dict[tag]['obj'])

class ParserChooser:
    def __init__(self, filename, user):
        with open(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], filename)) as bookmark_file:
            data = bookmark_file.read()
            try:
                doc = ujson.loads(data)
                if type(doc) == list:
                    if doc[0].has_key('extended'):
                        """
                        Pinboard exports look like this:
                        [{"href":"https:\/\/google.com\/",
                        "description":"Search Engine",
                        "extended":"Google Inc. is an American multinational technology company specializing in Internet-related services and products.",
                        "meta":"416fd0fdb32bf55ad8hdh3393e28f24d",
                        "hash":"424324adbc3a767548d01df2f6578163",
                        "time":"2015-04-04T02:05:09Z","shared":"no",
                        "toread":"no","tags":"search abcd"}
                        Its basically a list of dicts, and each dict will have a extended key, which can be en empty str.
                        """
                        x = PinboardParser(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], filename), user)
                        x.process()
                        x.add_to_database()
                elif type(doc) == dict:
                    if doc.has_key('bookmarks'):
                        """
                                            {
                        "bookmarks": [
                            {
                                "article__excerpt": "April 3, 1979 9:35 a.m. Los Angeles International The truth was, flying commercial could be boring work. The old philosophy among pilots, starting in the days when the DC-3 was the biggest thing&hellip;",
                                "favorite": false,
                                "date_archived": null,
                                "article__url": "http://reprints.longform.org/flight-bissinger",
                                "date_added": "2015-06-03T16:45:07",
                                "date_favorited": null,
                                "article__title": "The Plane That Fell From the Sky",
                                "archive": false
                            },
                        """
                        x = ReadabilityParser(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], filename), user)
                        x.process()
                        x.add_to_database()
            except ValueError:
                doc = data.splitlines()
                if doc[0] == "<!DOCTYPE NETSCAPE-Bookmark-file-1>" and doc[5] == "<TITLE>Bookmarks</TITLE>":
                    """
                    This calls the generic Netscape parser used by Chrome and Firefox.
                    These files look like this:
                    <!DOCTYPE NETSCAPE-Bookmark-file-1>
                    <!-- This is an automatically generated file.
                         It will be read and overwritten.
                         DO NOT EDIT! -->
                    <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
                    <TITLE>Bookmarks</TITLE>
                    """
                    x = Parser(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], filename), user)
                    x.process()
                    x.add_to_database()
                elif doc[4] == "<title>Instapaper: Export</title>":
                    """
                    This calls the Instapaper Parser.
                    These files look like this:
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                    <title>Instapaper: Export</title>
                    </head>
                    <body>
                    """
                    x = InstapaperParser(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], filename), user)
                    x.process()
                    x.add_to_database()
                elif doc[5].strip("	") == "<title>Pocket Export</title>":
                    """
                    <!DOCTYPE html>
                    <html>
                        <!--So long and thanks for all the fish-->
                        <head>
                            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
                            <title>Pocket Export</title>
                        </head>
                        <body>
                    """
                    x = PocketParser(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], filename), user)
                    x.process()
                    x.add_to_database()
