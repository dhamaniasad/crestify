# -*- coding: utf-8 -*-
from selenium import webdriver
from crestify.archivers import ArchiveService


class ArchiveTodayService(ArchiveService):
    def get_service_name(self):
        return "today.archive"

    def submit(self, url):
        browser = webdriver.PhantomJS(service_args=[
            "--ignore-ssl-errors=true",
            "--ssl-protocol=tlsv1",
            "--load-images=no"])
        browser.get('https://archive.is')
        input = browser.find_element_by_id('url')
        input.send_keys(url)
        input.submit()
        url = browser.current_url
        # archive.today has no restrictions on archivable pages
        # This should only happen on network errors
        if not url:
            raise ArchiveException()
        return url
