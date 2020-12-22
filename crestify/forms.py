# -*- coding: utf-8 -*-
from flask_wtf.form import Form
from wtforms import (
    TextField,
    StringField,
    HiddenField,
    Field,
    SelectField,
    BooleanField,
    FieldList,
    RadioField,
    IntegerField,
)
from wtforms.widgets import TextInput, HiddenInput
from wtforms.fields.html5 import URLField
from wtforms.validators import ValidationError
from flask_security.forms import Required, ConfirmRegisterForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import Form, RecaptchaField


""" Validators """


def validate_invite_code(form, field):
    from crestify.models import Invite, db

    code = field.data
    query = Invite.query.filter_by(text=code).first()
    if not query:
        raise ValidationError("Sorry, but this invite code is invalid :(")
    else:
        if query.id == form.invite_id.data:
            if query.single_use is True and query.used is True:
                raise ValidationError(
                    "Sorry, but this invite code has already been used :("
                )
            elif query.single_use is True and query.used is False:
                query.used = True
                db.session.commit()
            elif query.single_use is False:
                query.used = True
                db.session.commit()
        else:
            raise ValidationError(
                "Sorry, but the invite code validation failed. Please try again."
            )


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ", ".join(self.data)
        else:
            return ""


class ExtendedRegisterForm(ConfirmRegisterForm):
    """
    Extended user registration form with added fields for First and Last name
    """

    first_name = TextField("First Name", [Required()])
    last_name = TextField("Last Name", [Required()])
    recaptcha = RecaptchaField()
    invite_code = TextField("Invite Code", [Required(), validate_invite_code])
    invite_id = IntegerField([Required()], widget=HiddenInput())


class NewBookmarkForm(Form):
    """
    A Form to add new bookmarks.
    Takes only the url for the bookmark.
    """

    title = StringField("Title")
    main_url = URLField("URL", [Required()])
    description = StringField("Description")
    tags = TagListField("Tags")

    class Meta:
        """
        We expect new bookmarks to come externally through the Bookmarklet,
        thus we don't want CSRF even though it's set up on the base form.
        """

        csrf = False


class SearchForm(Form):
    """
    Form for searching
    """

    query = StringField("Search", [Required()])
    parameter = RadioField(
        "Type",
        choices=[("basic", "basic"), ("ft", "fulltext"), ("url", "url")],
        default="basic",
    )


class DeleteForm(Form):
    id = HiddenField([Required()])


class EditBookmarkForm(Form):
    main_url = URLField("URL", [Required()])
    title = StringField("Title", [Required()])
    description = StringField("Description")
    tags_1 = TagListField("Tags")


class PerPageForm(Form):
    bookmarks_per_page = SelectField(
        "Bookmarks per page",
        choices=[("10", "10"), ("20", "20"), ("40", "40"), ("80", "80")],
        validators=[Required()],
    )


class BookmarkImportForm(Form):
    import_file = FileField(
        "Bookmark HTML/JSON file",
        validators=[
            FileRequired(),
            FileAllowed(["html", "json"], "HTML or JSON files only!"),
        ],
    )


class NewTabSetForm(Form):
    uuid = HiddenField([Required()])
    title = StringField("Title", [Required()])


class RegenerateApiKeyForm(Form):
    pass
