# {{cookiecutter.project_name}}

{{cookiecutter.readme_description}}


## Quickstart

First, set the following in your bashrc:

```
export FLASK_APP=autoapp.py
export FLASK_DEBUG=1
```

Run the following commands to bootstrap your environment

```
mkvirtualenv -p $(which python3) whatever-name-you-want
pip install -r requirements-dev.txt
```

Now set up your database. I have only tested this project with PostgreSQL. It's
the bee's knees. If you run into any issues with other databases let me know :)
You should create your database and then modify the `settings.py` file that was
generated in your project. Update the `SQLALCHEMY_DATABASE_URI` appropriately.

Next run the following to create your app's database tables and perform the
initial migration

```
flask db init
flask db migrate -m "initialize"
flask db upgrade
```

Now run the server with

```
flask run
```

You should be able to access your service [here](http://localhost:5000).

## Shell

To open the interactive shell, run

```
flask shell
```

By default, you will have access to the flask `app`.


## Running Tests

To run all tests, run

```
pytest
```


## Migrations

Whenever a database migration needs to be made. Run the following commands

```
flask db migrate -m "Name your migration"
```

This will generate a new migration script. Then run

```
flask db upgrade
```

To apply the migration.

For a full migration command reference, run `flask db --help`.
