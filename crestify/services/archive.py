# -*- coding: utf-8 -*-
"""Main Archiving Business Logic"""
from crestify.archivers import ArchiveOrgService, ArchiveTodayService, ArchiveException
from crestify.models import db, Archive, Bookmark
from datetime import datetime
from crestify.tasks import celery


def do_archives(bookmark):
    """Takes an object of type Bookmark and creates archives for it"""
    process_archive.delay(bookmark.id, ArchiveOrgService())
    process_archive.delay(bookmark.id, ArchiveTodayService())


@celery.task(name="process_archive")
def process_archive(bookmark_id, archive_service):
    """
    Takes an object of Bookmark and ArchiveService
    and creates a corresponding archive
    """
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
