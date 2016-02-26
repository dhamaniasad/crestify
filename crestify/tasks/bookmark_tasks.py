from __future__ import absolute_import
import urlparse
import os
import ujson
import requests
from bs4 import BeautifulSoup as BeautifulSoup4
from selenium import webdriver
from readability.readability import Document
from crestify import app
from crestify.models import db, Bookmark
from crestify.tasks import celery
from crestify.services.parsers import ParserChooser
from crestify.services.archive import Archive, ArchiveException
from datetime import datetime


@celery.task(name='fetch_description')
def fetch_description(bookmark):
    desc_bookmark = Bookmark.query.get(bookmark.id)
    r = requests.get(desc_bookmark.main_url)
    soup = BeautifulSoup4(r.content)
    desc = soup.find(attrs={"name": "description"})
    if desc is not None:
        desc = desc['content']
        desc_bookmark.description = desc[:256].encode('utf-8')
        db.session.commit()


@celery.task(name='fetch_title')
def fetch_title(bookmark):
    title_bookmark = Bookmark.query.get(bookmark.id)
    r = requests.get(title_bookmark.main_url)
    soup = BeautifulSoup4(r.content)
    title = soup.title.string
    title_bookmark.title = title.encode('utf-8')
    db.session.commit()


@celery.task(name='fulltext_extract')
def fulltext_extract(bookmark):
    browser = webdriver.PhantomJS(service_args=[
        "--ignore-ssl-errors=true",
        "--ssl-protocol=tlsv1",
        "--load-images=no"])
    fulltext_bookmark = Bookmark.query.get(bookmark.id)
    browser.get(fulltext_bookmark.main_url)
    body = browser.find_element_by_tag_name('body')
    bodytext = body.text
    soup = BeautifulSoup4(bodytext)
    full_text = soup.text
    full_text = " ".join(full_text.split())
    full_text = full_text.replace('\n', '')
    full_text = full_text.encode('utf-8')
    fulltext_bookmark.full_text = full_text
    db.session.commit()
    browser.quit()


ignored_netlocs = {'google.', 'reddit.com', 'youtube.com', 'www.facebook.com', 'news.ycombinator.com',
                   'slashdot.org', 'apple.com', 'github.com'}


@celery.task(name='readable_extract')
def readable_extract(bookmark):
    bookmark_readify = Bookmark.query.get(bookmark.id)
    url = bookmark_readify.main_url
    parsed_url = urlparse.urlparse(url)
    for netloc in ignored_netlocs:
        if netloc in parsed_url.netloc:
            return
    r = requests.get(bookmark_readify.main_url)
    soup = BeautifulSoup4(r.content, "lxml")
    make_links_absolute(soup, bookmark_readify.main_url)
    html_self_closing_tags = ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link',
                              'meta', 'param', 'source', 'track', 'wbr']
    """ Above list from http://xahlee.info/js/html5_non-closing_tag.html"""
    empty_tags = soup.findAll(lambda tag: tag.name not in html_self_closing_tags and not tag.contents and (
        tag.string is None or not tag.string.strip()))
    [empty_tag.extract() for empty_tag in empty_tags]
    cleanhtml = soup.encode_contents()
    readable_article = Document(cleanhtml).summary()
    bookmark_readify.readability_html = readable_article
    db.session.commit()


def make_links_absolute(soup, url):
    for tag in soup.findAll('a', href=True):
        if urlparse.urlparse(tag['href']).scheme == '':
            tag['href'] = urlparse.urljoin(url, tag['href'])
    for img in soup.findAll('img', src=True):
        if urlparse.urlparse(img['src']).scheme == '':
            img['src'] = urlparse.urljoin(url, img['src'])


@celery.task(name='import_bookmarks')
def import_bookmarks(filename, user):
    x = ParserChooser(filename, user)


@celery.task(name='process_archive')
def process_archive(bookmark_id, archive_service):
    '''
    Takes an object of Bookmark and ArchiveService
    and creates a corresponding archive
    '''
    bookmark = Bookmark.query.get(bookmark_id)
    if bookmark is not None:
        archive = Archive()
        archive.web_page = bookmark.id
        archive.service = archive_service.get_service_name()
        archive.archived_on = datetime.utcnow()
        archive.status = Archive.ARCHIVE_IN_PROGRESS

        db.session.add(archive)
        db.session.commit()
        try:
            archive.archive_url = archive_service.submit(bookmark.main_url)
            archive.archived_on = datetime.utcnow()
            archive.status = Archive.ARCHIVE_SUCCESSFUL
        except ArchiveException:
            archive.archive_url = ""
            archive.archived_on = None
            archive.status = Archive.ARCHIVE_FAILURE
        except Exception:
            archive.archive_url = ""
            archive.archived_on = None
            archive.status = Archive.ARCHIVE_ERROR
        finally:
            db.session.add(archive)
            db.session.commit()
