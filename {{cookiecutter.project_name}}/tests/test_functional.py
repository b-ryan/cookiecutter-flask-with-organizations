import re
from flask import url_for
from {{cookiecutter.package_name}}.users.models import User
from .factories import UserFactory


class TestLoggingIn:
    def test_can_log_in_returns_200(self, user, testapp):
        res = testapp.get("/login")
        form = res.forms["loginForm"]
        form["email"] = user.email
        form["password"] = "myprecious"
        res = form.submit().follow()
        assert res.status_code == 302
        assert re.search("\/orgs\/\d+$", res.location)

    def test_sees_alert_on_log_out(self, user, testapp):
        res = testapp.get("/login")
        form = res.forms["loginForm"]
        form["email"] = user.email
        form["password"] = "myprecious"
        res = form.submit().follow()
        res = testapp.get(url_for("main.logout")).follow()
        assert "You are logged out." in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        res = testapp.get("/login")
        form = res.forms["loginForm"]
        form["email"] = user.email
        form["password"] = "wrong"
        res = form.submit()
        assert "Invalid password" in res

    def test_sees_error_message_if_email_doesnt_exist(self, user, testapp):
        res = testapp.get("/login")
        form = res.forms["loginForm"]
        form["email"] = "unknown"
        form["password"] = "myprecious"
        res = form.submit()
        assert "Unknown email" in res


class TestRegistering:
    def test_can_register(self, user, testapp):
        old_count = len(User.query.all())
        res = testapp.get(url_for("public.register"))
        form = res.forms["registerForm"]
        form["organization_name"] = "frank"
        form["email"] = "foo@bar.com"
        form["password"] = "secretaaaaa"
        form["verify_password"] = "secretaaaaa"
        res = form.submit()
        assert res.status_code == 302
        assert re.search("\/orgs\/\d+$", res.location)
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        res = testapp.get(url_for("public.register"))
        form = res.forms["registerForm"]
        form["email"] = "foo@bar.com"
        form["password"] = "secret"
        form["verify_password"] = "secrets"
        res = form.submit()
        assert "Passwords must match" in res

    def test_sees_error_message_if_user_already_registered(self, user, testapp, db):
        user = UserFactory(active=True)
        db.session.add(user)
        db.session.commit()
        res = testapp.get(url_for("public.register"))
        form = res.forms["registerForm"]
        form["organization_name"] = "frank"
        form["email"] = user.email
        form["password"] = "secretaaaaa"
        form["verify_password"] = "secretaaaaa"
        res = form.submit()
        assert "Email already registered" in res
