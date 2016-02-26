import unittest
from crestify.models import User, Bookmark, db
from crestify import app
import datetime
import time
import os
from BeautifulSoup import BeautifulSoup as BeautifulSoup3
from bs4 import BeautifulSoup as BeautifulSoup4
from lxml import html
import ujson as json
from HTMLParser import HTMLParser
from crestify.services.parsers import PinboardParser, ReadabilityParser, InstapaperParser, PocketParser, Parser


class PinboardTestCase(unittest.TestCase):

    def setUp(self):
        query_user = User.query.filter_by(email='pinboard@example.com').first()
        if query_user:
            query_bookmarks = Bookmark.query.filter_by(user=query_user.id)
            for bmark in query_bookmarks:
                db.session.delete(bmark)
            db.session.commit()
            db.session.delete(query_user)
            db.session.commit()
        create_user = User()
        create_user.first_name = 'Pinboard'
        create_user.last_name = 'Test'
        create_user.email = 'pinboard@example.com'
        create_user.password = 'pinboard_pass'
        create_user.active = True
        create_user.confirmed_at = datetime.datetime.utcnow()
        db.session.add(create_user)
        db.session.commit()
        self.user = create_user
        with open('Pinboard.json') as json_file:
            create_file = open(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_pinboard.json'), 'w+')
            self.data = json_file.read()
            self.json_data = json.loads(self.data)
            self.bookmarks = {}
            for bmark in self.json_data:
                url = bmark['href']
                self.bookmarks[url] = bmark
            create_file.write(self.data)
            self.file_path = create_file.name
            create_file.close()
        init_parser = PinboardParser(self.file_path, self.user.id)
        init_parser.process()
        init_parser.add_to_database()
        self.query = Bookmark.query.filter_by(user=self.user.id).all()

    def test_urls(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['href'], bmark.main_url)

    def test_titles(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['description'], bmark.title)

    def test_timestamps(self):
        for bmark in self.query:
            self.assertEqual(datetime.datetime.strptime(self.bookmarks[bmark.main_url]['time'], '%Y-%m-%dT%H:%M:%SZ'),
                             bmark.added_on)

    def test_tags(self):
        for bmark in self.query:
            tags = filter(None, self.bookmarks[bmark.main_url]['tags'].split(' ') + ['Imported'])
            delta_tags = list(set(bmark.tags) - set(tags))
            self.assertEqual([], delta_tags)

    def test_description(self):
        for bmark in self.query:
            self.assertEqual((self.bookmarks[bmark.main_url]['extended'] if self.bookmarks[bmark.main_url]['extended'] != u'' else None), bmark.description)

    def tearDown(self):
        for bmark in self.query:
            db.session.delete(bmark)
        db.session.commit()
        db.session.delete(self.user)
        db.session.commit()
        os.remove(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_pinboard.json'))


class ReadabilityTestCase(unittest.TestCase):

    def setUp(self):
        query_user = User.query.filter_by(email='readability@example.com').first()
        if query_user:
            query_bookmarks = Bookmark.query.filter_by(user=query_user.id)
            for bmark in query_bookmarks:
                db.session.delete(bmark)
            db.session.commit()
            db.session.delete(query_user)
            db.session.commit()
        create_user = User()
        create_user.first_name = 'Readability'
        create_user.last_name = 'Test'
        create_user.email = 'readability@example.com'
        create_user.password = 'readability_pass'
        create_user.active = True
        create_user.confirmed_at = datetime.datetime.utcnow()
        db.session.add(create_user)
        db.session.commit()
        self.user = create_user
        with open('Readability.json') as json_file:
            create_file = open(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_readability.json'), 'w+')
            self.data = json_file.read()
            self.json_data = json.loads(self.data)['bookmarks']
            self.bookmarks = {}
            for bmark in self.json_data:
                url = bmark['article__url']
                self.bookmarks[url] = bmark
            create_file.write(self.data)
            self.file_path = create_file.name
            create_file.close()
        init_parser = ReadabilityParser(self.file_path, self.user.id)
        init_parser.process()
        init_parser.add_to_database()
        self.query = Bookmark.query.filter_by(user=self.user.id).all()
        self.html_parser = HTMLParser()

    def test_urls(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['article__url'], bmark.main_url)

    def test_titles(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['article__title'], bmark.title)

    def test_timestamps(self):
        for bmark in self.query:
            '2015-06-03T16:45:07'
            self.assertEqual(datetime.datetime.strptime(self.bookmarks[bmark.main_url]['date_added'], '%Y-%m-%dT%H:%M:%S'),
                             bmark.added_on)

    def test_tags(self):
        for bmark in self.query:
            tags = ['Imported']
            delta_tags = list(set(bmark.tags) - set(tags))
            self.assertEqual([], delta_tags)

    def test_description(self):
        for bmark in self.query:
            self.assertEqual(self.html_parser.unescape((self.bookmarks[bmark.main_url]['article__excerpt']) if self.bookmarks[bmark.main_url]['article__excerpt'] != u'' else None), bmark.description)

    def tearDown(self):
        for bmark in self.query:
            db.session.delete(bmark)
        db.session.commit()
        db.session.delete(self.user)
        db.session.commit()
        os.remove(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_readability.json'))


class InstapaperTestCase(unittest.TestCase):

    def setUp(self):
        query_user = User.query.filter_by(email='instapaper@example.com').first()
        if query_user:
            query_bookmarks = Bookmark.query.filter_by(user=query_user.id)
            for bmark in query_bookmarks:
                db.session.delete(bmark)
            db.session.commit()
            db.session.delete(query_user)
            db.session.commit()
        create_user = User()
        create_user.first_name = 'Instapaper'
        create_user.last_name = 'Test'
        create_user.email = 'instapaper@example.com'
        create_user.password = 'instapaper_pass'
        create_user.active = True
        create_user.confirmed_at = datetime.datetime.utcnow()
        db.session.add(create_user)
        db.session.commit()
        self.user = create_user
        with open('Instapaper.html') as json_file:
            create_file = open(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_instapaper.html'), 'w+')
            self.data = html.document_fromstring(json_file.read())
            self.data = html.tostring(self.data)
            self.html_data = BeautifulSoup4(self.data)
            self.bookmarks = {}
            for tag in self.html_data.find_all('h1'):
                parent_elem = tag.find_next_sibling('ol')
                links = parent_elem.find_all('a')
                for link in links:
                    title = link.text
                    url = link['href']
                    tags = [tag.text]
                    tags.append('Imported')
                    #  Thanks Instapaper for not adding timestamps
                    self.bookmarks[url] = {
                        'href': url,
                        'title': title,
                        'tags': tags
                    }
            create_file.write(self.data)
            self.file_path = create_file.name
            create_file.close()
        init_parser = InstapaperParser(self.file_path, self.user.id)
        init_parser.process()
        init_parser.add_to_database()
        self.query = Bookmark.query.filter_by(user=self.user.id).all()
        self.html_parser = HTMLParser()

    def test_urls(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['href'], bmark.main_url)

    def test_titles(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['title'], bmark.title)

    def test_tags(self):
        for bmark in self.query:
            tags = self.bookmarks[bmark.main_url]['tags']
            delta_tags = list(set(bmark.tags) - set(tags))
            self.assertEqual([], delta_tags)

    def tearDown(self):
        for bmark in self.query:
            db.session.delete(bmark)
        db.session.commit()
        db.session.delete(self.user)
        db.session.commit()
        os.remove(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_instapaper.html'))


class PocketTestCase(unittest.TestCase):

    def setUp(self):
        query_user = User.query.filter_by(email='pocket@example.com').first()
        if query_user:
            query_bookmarks = Bookmark.query.filter_by(user=query_user.id)
            for bmark in query_bookmarks:
                db.session.delete(bmark)
            db.session.commit()
            db.session.delete(query_user)
            db.session.commit()
        create_user = User()
        create_user.first_name = 'Pocket'
        create_user.last_name = 'Test'
        create_user.email = 'pocket@example.com'
        create_user.password = 'pocket_pass'
        create_user.active = True
        create_user.confirmed_at = datetime.datetime.utcnow()
        db.session.add(create_user)
        db.session.commit()
        self.user = create_user
        with open('Pocket.html') as json_file:
            create_file = open(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_pocket.html'), 'w+')
            self.data = json_file.read()
            self.html_data = BeautifulSoup4(self.data)
            self.bookmarks = {}
            for link in self.html_data.find_all('a'):
                tags = link['tags'].split(',')
                tags.append('Imported')
                dt = datetime.datetime.utcfromtimestamp(float(link['time_added']))
                self.bookmarks[link['href']] = {
                    'href': link['href'],
                    'title': link.text,
                    'tags': tags,
                    'dt': dt
                }
        create_file.write(self.data)
        self.file_path = create_file.name
        create_file.close()
        init_parser = PocketParser(self.file_path, self.user.id)
        init_parser.process()
        init_parser.add_to_database()
        self.query = Bookmark.query.filter_by(user=self.user.id).all()
        self.html_parser = HTMLParser()

    def test_urls(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['href'], bmark.main_url)

    def test_titles(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['title'], bmark.title)

    def test_tags(self):
        for bmark in self.query:
            tags = self.bookmarks[bmark.main_url]['tags']
            delta_tags = list(set(bmark.tags) - set(tags))
            self.assertEqual([], delta_tags)

    def test_timestamps(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['dt'], bmark.added_on)

    def tearDown(self):
        for bmark in self.query:
            db.session.delete(bmark)
        db.session.commit()
        db.session.delete(self.user)
        db.session.commit()
        os.remove(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_pocket.html'))


class NetscapeTestCase(unittest.TestCase):

    def setUp(self):
        query_user = User.query.filter_by(email='netscape@example.com').first()
        if query_user:
            query_bookmarks = Bookmark.query.filter_by(user=query_user.id)
            for bmark in query_bookmarks:
                db.session.delete(bmark)
            db.session.commit()
            db.session.delete(query_user)
            db.session.commit()
        create_user = User()
        create_user.first_name = 'Netscape'
        create_user.last_name = 'Test'
        create_user.email = 'netscape@example.com'
        create_user.password = 'netscape_pass'
        create_user.active = True
        create_user.confirmed_at = datetime.datetime.utcnow()
        db.session.add(create_user)
        db.session.commit()
        self.user = create_user
        self.html_parser = HTMLParser()
        with open('Netscape.html') as json_file:
            create_file = open(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_netscape.html'), 'w+')
            self.data = json_file.read()
            self.html_data = BeautifulSoup3(self.data)
            self.bookmarks = {}
            urls = self.html_data.findAll('a')
            for link in urls:
                url = link['href']
                if url in self.bookmarks:
                    pass
                else:
                    tags = ['Imported']
                    if link.has_key('add_date'):
                        added_timestamp = int(link['add_date'])
                    else:
                        added_timestamp = time.time()
                    self.bookmarks[url] = {
                        'href': self.html_parser.unescape(url),
                        'title': self.html_parser.unescape(link.text),
                        'tags': tags,
                        'added_on': datetime.datetime.utcfromtimestamp(
                            added_timestamp)
                    }
        create_file.write(self.data)
        self.file_path = create_file.name
        create_file.close()
        init_parser = Parser(self.file_path, self.user.id)
        init_parser.process()
        init_parser.add_to_database()
        self.query = Bookmark.query.filter_by(user=self.user.id).all()

    def test_urls(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['href'], bmark.main_url)

    def test_titles(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['title'], bmark.title)

    def test_tags(self):
        for bmark in self.query:
            tags = self.bookmarks[bmark.main_url]['tags']
            delta_tags = list(set(bmark.tags) - set(tags))
            self.assertEqual([], delta_tags)

    def test_timestamps(self):
        for bmark in self.query:
            self.assertEqual(self.bookmarks[bmark.main_url]['added_on'], bmark.added_on)

    def tearDown(self):
        for bmark in self.query:
            db.session.delete(bmark)
        db.session.commit()
        db.session.delete(self.user)
        db.session.commit()
        os.remove(os.path.join(app.config['CRESTIFY_UPLOAD_DIRECTORY'], 'test_netscape.html'))

# suite = unittest.TestLoader().loadTestsFromTestCase(NetscapeTestCase)
# unittest.TextTestRunner(verbosity=2).run(suite)

suite1 = unittest.TestLoader().loadTestsFromTestCase(NetscapeTestCase)
suite2 = unittest.TestLoader().loadTestsFromTestCase(PinboardTestCase)
suite3 = unittest.TestLoader().loadTestsFromTestCase(ReadabilityTestCase)
suite4 = unittest.TestLoader().loadTestsFromTestCase(PocketTestCase)
suite5 = unittest.TestLoader().loadTestsFromTestCase(InstapaperTestCase)
all_tests = unittest.TestSuite([suite1, suite2, suite3, suite4, suite5])
unittest.TextTestRunner(verbosity=2).run(all_tests)
