# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask import redirect, render_template, render_template_string, request, url_for, flash
from flask_user import current_user, login_required, roles_required
from docassemble.webapp.app_and_db import app, db
from docassemble.webapp.users.forms import UserProfileForm, MyRegisterForm
from docassemble.webapp.users.models import UserAuth, User
from docassemble.base.util import word
import random
import string

#
# User Profile form
#
@app.route('/userlist', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def user_list():
    output = "";
    for user in db.session.query(User):
        output += "<p>" + user.email + "</p>"
    return render_template('users/userlist.html', userlist=output)

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, current_user)

    # Process valid POST
    if request.method=='POST' and form.validate():

        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        flash(word('Your information was saved.'), 'success')
        # Redirect to home page
        return redirect(url_for('index'))

    # Process GET or invalid POST
    return render_template('users/user_profile_page.html',
        form=form)

