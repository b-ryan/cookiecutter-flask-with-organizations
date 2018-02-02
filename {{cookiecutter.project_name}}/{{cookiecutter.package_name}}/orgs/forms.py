from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired, Email, EqualTo, Length
from ..users.models import User
from .models import Organization


def password_field(label="Password"):
    return wtforms.PasswordField(
        label, validators=[DataRequired(), Length(min=8)])


def verify_password_field(label="Verify password", equal_to="password"):
    return wtforms.PasswordField(
        label, [
            DataRequired(),
            EqualTo(equal_to, message="Passwords must match"),
        ]
    )

PASSWORD_FIELD = password_field()
VERIFY_PASSWORD_FIELD = verify_password_field()


class RegisterForm(FlaskForm):
    organization_name = wtforms.StringField(
        "Organization Name",
        validators=[DataRequired(), Length(min=3)]
    )
    email = wtforms.StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(min=6)]
    )
    password = PASSWORD_FIELD
    verify_password = VERIFY_PASSWORD_FIELD

    def validate(self):
        if not super().validate():
            return False
        org = Organization.query.filter_by(name=self.organization_name.data).first()
        if org:
            self.organization_name.errors.append("Organization is already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class InviteForm(FlaskForm):
    email = wtforms.StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(min=6)]
    )
    is_admin = wtforms.BooleanField("admin", default=False)

    def __init__(self, *args, organization, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization
        self.user = None

    def validate(self):
        if not super().validate():
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            return True
        self.user = user
        if self.user.active_membership(self.organization.id):
            self.email.errors.append("This user is already active in this account ")
            return False
        return True


class DeactivateForm(FlaskForm):
    membership_id = wtforms.IntegerField(
        "membership_id", validators=[DataRequired()])


class RedeemForm(FlaskForm):
    confirm = wtforms.StringField("Confirm", validators=[DataRequired()])


class RedeemWithRegistrationForm(RedeemForm):
    password = PASSWORD_FIELD
    verify_password = VERIFY_PASSWORD_FIELD
