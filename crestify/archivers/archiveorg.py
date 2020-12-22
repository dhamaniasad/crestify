# -*- coding: utf-8 -*-
import requests
from crestify.archivers import ArchiveService, ArchiveException


class ArchiveOrgService(ArchiveService):
    def get_service_name(self):
        return "org.archive"

    def submit(self, url):
        url = "http://web.archive.org/save/%s" % (url)
        response = requests.get(url)
        if response.status_code == 403:
            raise ArchiveException()
        else:
            url = response.headers["Content-Location"]
            return "http://web.archive.org%s" % (url)
