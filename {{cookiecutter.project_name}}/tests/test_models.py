import datetime as dt
import pytest
from {{cookiecutter.package_name}}.users.models import User
from .factories import UserFactory


@pytest.mark.usefixtures("db")
class TestUser:
    def test_get_by_id(self, db):
        user = User("foo", "foo@bar.com")
        db.session.add(user)
        db.session.commit()
        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self, db):
        user = User(email="foo@bar.com")
        db.session.add(user)
        db.session.commit()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self, db):
        user = User(email="foo@bar.com")
        db.session.add(user)
        db.session.commit()
        assert user.password is None

    def test_factory(self, db):
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password("myprecious")

    def test_check_password(self):
        user = User.create(email="foo@bar.com",
                           password="foobarbaz123")
        assert user.check_password("foobarbaz123") is True
        assert user.check_password("barfoobaz") is False

    def test_full_name(self):
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"
