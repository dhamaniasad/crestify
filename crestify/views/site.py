# -*- coding: utf-8 -*-
'''Routes and Views for the front site'''
from flask import render_template, redirect, request, jsonify
from flask_security import current_user
from crestify import app


@app.route('/')
def index():
    '''The Main page'''
    if current_user.is_anonymous:
        return render_template("site/index.html")
    else:
        return redirect("/manager/bookmark")


@app.route('/about')
def about():
    '''About page'''
    return render_template("site/index.html")


@app.route('/features')
def features():
    '''Features page'''
    return render_template("site/index.html")


@app.route('/tos')
def terms_of_service():
    '''Terms and conditions page'''
    return render_template("site/terms.html")
