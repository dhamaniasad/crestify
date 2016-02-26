# -*- coding: utf-8 -*-
from crestify.models import db, User
import shortuuid


def regenerate_api_key(id):
    user = User.query.get(id)
    user.api_key = shortuuid.ShortUUID().random(length=32)
    db.session.commit()
