# -*- coding: utf-8 -*-
from wtforms import TextField, StringField, HiddenField, Field, SelectField, \
    RadioField
from wtforms.widgets import TextInput
from wtforms.fields.html5 import URLField
from flask_security.forms import Required, RegisterForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import Form


class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''


class ExtendedRegisterForm(RegisterForm):
    '''
    Extended user registration form with added fields for First and Last name
    '''
    first_name = TextField('First Name', [Required()])
    last_name = TextField('Last Name', [Required()])


class NewBookmarkForm(Form):
    '''
    A Form to add new bookmarks.
    Takes only the url for the bookmark.
    '''
    title = StringField('Title')
    main_url = URLField('URL', [Required()])
    description = StringField('Description')
    tags = TagListField('Tags')

    class Meta:
        '''
        We expect new bookmarks to come externally through the Bookmarklet,
        thus we don't want CSRF even though it's set up on the base form.
        '''
        csrf = False


class SearchForm(Form):
    '''
    Form for searching
    '''
    query = StringField('Search', [Required()])
    parameter = RadioField('Type', choices=[('basic', 'basic'), ('ft', 'fulltext'), ('url', 'url')], default='basic')


class DeleteForm(Form):
    id = HiddenField([Required()])


class EditBookmarkForm(Form):
    main_url = URLField('URL', [Required()])
    title = StringField('Title', [Required()])
    description = StringField('Description')
    tags_1 = TagListField('Tags')


class PerPageForm(Form):
    bookmarks_per_page = SelectField('Bookmarks per page', choices=[('10', '10'), ('20', '20'), ('40', '40'), ('80', '80')], validators=[Required()])


class BookmarkImportForm(Form):
    import_file = FileField('Bookmark HTML/JSON file', validators=[
        FileRequired(),
        FileAllowed(['html', 'json'], 'HTML or JSON files only!')
    ])


class NewTabSetForm(Form):
    uuid = HiddenField([Required()])
    title = StringField('Title', [Required()])

class RegenerateApiKeyForm(Form):
    pass
