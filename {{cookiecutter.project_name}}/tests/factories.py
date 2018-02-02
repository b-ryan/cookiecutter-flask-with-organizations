from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory
from {{cookiecutter.package_name}}.extensions import db
from {{cookiecutter.package_name}}.orgs.models import Organization, Membership
from {{cookiecutter.package_name}}.users.models import User


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class OrganizationFactory(BaseFactory):
    name = Sequence(lambda n: "organization {}".format(n))
    class Meta:
        model = Organization


class UserFactory(BaseFactory):
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall("set_password", "example")
    active = True
    class Meta:
        model = User


class MembershipFactory(BaseFactory):
    role = "owner"
    active = True
    class Meta:
        model = Membership


USER_PW = "myprecious"


def create_a_membership():
    org = OrganizationFactory()
    user = UserFactory(password=USER_PW)
    mem = MembershipFactory(organization=org, user=user)
    db.session.add(mem)
    db.session.commit()
    return mem
