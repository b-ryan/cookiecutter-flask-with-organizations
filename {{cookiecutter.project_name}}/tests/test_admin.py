from flask import url_for


def admin_urls(testapp):
    url_map = testapp.app.url_map
    rules = list(url_map.iter_rules())
    return [r.rule for r in rules
            if r.rule.startswith("/admin")
            and not r.rule.startswith("/admin/static")
            and "GET" in r.methods]


def test_non_admins_unauthorized(testapp, logged_in_user):
    for url in admin_urls(testapp):
        print(url)
        res = testapp.get(url, expect_errors=True)
        assert res.status_code == 403


def test_admins_allowed(testapp, db, logged_in_admin_user):
    for url in admin_urls(testapp):
        print(url)
        res = testapp.get(url, expect_errors=True)
        assert res.status_code != 403
