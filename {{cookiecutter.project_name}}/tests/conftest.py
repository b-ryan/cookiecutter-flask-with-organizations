import pytest
from flask import url_for
from webtest import TestApp
from {{cookiecutter.package_name}}.app import create_app
from {{cookiecutter.package_name}}.extensions import db as db_
from {{cookiecutter.package_name}}.settings import TestConfig
from . import factories as fac


@pytest.yield_fixture(scope="function")
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(scope="function")
def testapp(app):
    return TestApp(app)


@pytest.yield_fixture(scope="function")
def db(app):
    db_.app = app
    with app.app_context():
        db_.create_all()
    yield db_
    db_.session.close()
    db_.drop_all()


@pytest.fixture
def membership(db):  # db needed in order to create the tables
    return fac.create_a_membership()


@pytest.fixture
def user(membership):
    return membership.user


@pytest.fixture
def admin_user(db):
    user = fac.UserFactory(password=fac.USER_PW, is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.yield_fixture
def logged_in_user(testapp, user):
    testapp.post(
        url_for("public.login"),
        {"email": user.email, "password": fac.USER_PW}
    )
    yield user
    testapp.get(url_for("main.logout"))


@pytest.yield_fixture
def logged_in_admin_user(testapp, admin_user):
    testapp.post(
        url_for("public.login"),
        {"email": admin_user.email, "password": fac.USER_PW}
    )
    yield admin_user
    testapp.get(url_for("main.logout"))


@pytest.fixture
def organization(membership):
    return membership.organization
