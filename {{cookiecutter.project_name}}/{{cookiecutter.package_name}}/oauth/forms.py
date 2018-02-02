from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, FieldList
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput, ListWidget
from ..users.models import User


class OAuthClientForm(FlaskForm):
    name = StringField("Application Name", validators=[DataRequired()])
    description = StringField("Application Description")
    homepage_url = StringField("Homepage URL", validators=[DataRequired()])
    redirect_uri = StringField("Callback URL", validators=[DataRequired()])


class ConfirmationForm(FlaskForm):
    confirm = StringField("Confirm")
