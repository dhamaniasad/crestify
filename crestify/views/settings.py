"""Routes and Views for the Settings"""
from flask import render_template, request, redirect, url_for
from flask_security import login_required, current_user
from flask_security.forms import ChangePasswordForm
from crestify import app
from crestify.models import User
from crestify.forms import PerPageForm, BookmarkImportForm, RegenerateApiKeyForm
from crestify.services import bookmark, user_service
from crestify.tasks import bookmark_tasks
from werkzeug.utils import secure_filename
import shortuuid
import os


@app.route("/settings", methods=["GET"])
@login_required
def settings():
    user_details = User.query.get(current_user.id)
    bookmarks_per_page_form = PerPageForm(obj=user_details)
    import_bookmark_file_form = BookmarkImportForm()
    regenerate_api_key_form = RegenerateApiKeyForm()
    change_password_form = ChangePasswordForm()
    return render_template(
        "manager/settings.html",
        per_page=bookmarks_per_page_form,
        import_form=import_bookmark_file_form,
        regenerate_api_key_form=regenerate_api_key_form,
        change_password_form=change_password_form,
        user_api_key=user_details.api_key,
        user_email=user_details.email,
    )


@app.route("/settings/bookmarks_per_page", methods=["POST"])
@login_required
def bookmarks_per_page():
    form = PerPageForm(request.form)
    if form.validate_on_submit():
        bookmark.per_page(
            user_id=current_user.id, per_page=form.bookmarks_per_page.data
        )
        return redirect(url_for("settings"))


@app.route("/settings/import_bookmark_file", methods=["POST"])
@login_required
def import_bookmark_file():
    form = BookmarkImportForm()
    if form.validate_on_submit():
        filename = secure_filename(form.import_file.data.filename)
        filename = shortuuid.uuid() + filename  # Prevent filename collisions
        form.import_file.data.save(
            os.path.join(app.config["CRESTIFY_UPLOAD_DIRECTORY"], filename)
        )
        bookmark_tasks.import_bookmarks.delay(filename=filename, user=current_user.id)
        return redirect(url_for("bookmark_list"))
    else:
        app.logger.debug(form.errors)
        return redirect(url_for("settings"))


@app.route("/settings/regenerate_api_key", methods=["POST"])
@login_required
def regenerate_api_key():
    form = RegenerateApiKeyForm(request.form)
    if form.validate_on_submit():
        user_service.regenerate_api_key(current_user.id)
    return redirect(url_for("settings"))
