from {{cookiecutter.package_name}}.public.forms import LoginForm
from {{cookiecutter.package_name}}.orgs.forms import RegisterForm


class TestRegisterForm:
    def test_validate_email_already_registered(self, user):
        form = RegisterForm(organization_name="fazz",
                            email=user.email,
                            password="example123",
                            verify_password="example123")
        assert form.validate() is False
        assert "Email already registered" in form.email.errors

    def test_validate_success(self, db):
        form = RegisterForm(organization_name="testy",
                            email="new@test.test",
                            password="example123",
                            verify_password="example123")
        assert form.validate() is True


class TestLoginForm:
    def test_validate_success(self, user, db):
        user.set_password("example")
        db.session.commit()
        form = LoginForm(email=user.email, password="example")
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_email(self, db):
        form = LoginForm(email="unknown@example.com", password="example")
        assert form.validate() is False
        assert "Unknown email" in form.email.errors
        assert form.user is None

    def test_validate_invalid_password(self, user, db):
        user.set_password("example")
        db.session.commit()
        form = LoginForm(email=user.email, password="wrongpassword")
        assert form.validate() is False
        assert "Invalid password" in form.password.errors

    def test_validate_inactive_user(self, user, db):
        user.active = False
        user.set_password("example")
        db.session.commit()
        form = LoginForm(email=user.email, password="example")
        assert form.validate() is False
        assert "User not activated" in form.email.errors
