# Cookiecutter Flask With Organizations

A(nother) Flask template for
[cookiecutter](https://github.com/audreyr/cookiecutter)

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Usage](#usage)
- [Features](#features)
- [OAuth Support](#oauth-support)
- [Admin Panel](#admin-panel)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

The "With Organizations" portion of the title refers to the fact that this
project is meant for apps that do not just have users, but those users belong
to one or more organizations. An example is [DbRhino](https://www.dbrhino.com/)
which is the app where I originally wrote the code to manage organizations.

This project was originally derived from
[cookiecutter-flask](https://github.com/sloria/cookiecutter-flask)
but has since diverged significantly. Particularly in that if you don't need
support for organizations, the original project is great and will probably suit
your needs.

## Usage

```
$ pip install cookiecutter
$ cookiecutter https://github.com/b-ryan/cookiecutter-flask-with-organizations
```

## Features

This supports most of the features
[here](https://github.com/sloria/cookiecutter-flask#features) with some notable
exceptions:

- Bootstrap 4
- No npm project dependency. This also means:
  - No JS/CSS minification

There are some additional features as well:

- A built-in OAuth 2 server
- Organization & Organization Membership models
- Registration form that requires the name of an organization
- An invite sending & redemption system for adding users to organizations
- Gravatar support
- Admin panel

## OAuth Support

The rendered project implements an OAuth 2 server. When it grants permissions
to an application, it does so for an organization, not a user. Meaning user A
may belong to organizations B and C. When they authorize an application, they
must choose whether to give authorization to B or C. Once they do, if the user
is deactivated (no longer belongs to the organization granted access), the
application will still have access to the organization. This could be
considered a bug. I am not yet sure whether this should be changed or what the
appropriate authorization model is.

There will be a file called `oauth_client.py` which you can use to test the
authorization flow. To go through the entire flow:

- Create an OAuth application [here](http://localhost:5000/orgs/1/applications)
- Start the client using the generated client ID and secret with

  ```
  ./oauth_client.py [your-client-id] [your-client-secret]
  ```

- Go to http://localhost:8000

## Admin Panel

To access the admin panel:

- Update your user in the database to set the `is_admin` flag:

  ```
  update users set is_admin = true where email = 'you@example.com';
  ```

- Log in to the application
- Visit http://localhost:5000/admin
