from flask_login import current_user
from flask_wtf import FlaskForm
from ..orgs.forms import password_field, verify_password_field
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])


class ResetPasswordForm(FlaskForm):
    new_password = password_field("New password")
    verify_password = verify_password_field(equal_to="new_password")


class ChangePasswordForm(ResetPasswordForm):
    curr_password = PasswordField(
        "Current password", validators=[DataRequired()])

    def validate(self):
        if not super().validate():
            return False
        if not current_user.check_password(self.curr_password.data):
            self.curr_password.errors.append("Invalid password")
            return False
        if self.curr_password.data == self.new_password.data:
            self.new_password.errors.append(
                "Must be different than the old password")
            return False
        return True
