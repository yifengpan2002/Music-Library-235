from flask import Blueprint, render_template,url_for, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
import music.authentication.services as services
import music.adapters.repository as repo
from functools import wraps

authBlueprint = Blueprint('authBp', __name__)


@authBlueprint.route('/login', methods=['GET', 'POST'])
def login():
    '''
    if services.get_user('yifeng123', repo.repo_instance) is None:
        services.add_user('yifeng123', 123, repo.repo_instance)
    '''
    form = LoginForm()
    user_name_not_recognised = None
    password_does_not_match_user_name = None
    if form.validate_on_submit():  # means we have apost method
        try:
            user = services.get_user(form.user_name.data,
                                     repo.repo_instance)  # this user is a dictionary object, we need to perform check
            services.validate_user(user['user_name'], form.password.data, repo.repo_instance)
            session.clear()
            session['user_name'] = user['user_name']
            return redirect(url_for('home_bp.home'))
        except services.UnknownUserException:
            user_name_not_recognised = 'User name not recognised - please supply another'

        except services.AuthenticationException:
            password_does_not_match_user_name = 'Password does not match supplied user name - please check and try ' \
                                                'again '

    return render_template('authentication/authentication.html', form=form,
                           user_name_error_message=user_name_not_recognised,
                           password_error_message=password_does_not_match_user_name)


@authBlueprint.route('/register', methods=['GET', 'POST'])
def register():
    '''
    if services.get_user('yifeng123', repo.repo_instance) is None:
        services.add_user('yifeng123', 123, repo.repo_instance)
    '''
    form = RegistrationForm()
    user_name_not_unique = None
    registed_state = False
    if form.validate_on_submit():
        try:
            user = services.add_user(form.user_name.data, form.password.data, repo.repo_instance)
            registed_state = True
            # return redirect(url_for('authBp.login'))
        except services.NameNotUniqueException:
            user_name_not_unique = 'Your user name is already taken - please supply another'

    return render_template('authentication/authentication.html', form=form,
                           user_name_error_message=user_name_not_unique, state=registed_state)


@authBlueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('home_bp.home'))

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_name' not in session:
            return redirect(url_for('authBp.login'))
        return view(**kwargs)
    return wrapped_view

class RegistrationForm(FlaskForm):
    user_name = StringField('Username', [
        DataRequired(message='Your user name is required'),
        Length(min=3, message='Your user name is too short')])
    password = PasswordField('Password', [
        DataRequired(message='Your password is required')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    user_name = StringField('Username', [
        DataRequired()])
    password = PasswordField('Password', [
        DataRequired()])
    submit = SubmitField('Login')
