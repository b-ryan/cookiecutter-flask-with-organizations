_owner = ["owner"]
_owner_admin = ["owner", "admin"]
# EVERYBODY should be used sparingly -- normally you should create a new
# variable below and set it to EVERYBODY
EVERYBODY = ["owner", "admin", "standard"]
DELETE_USERS = _owner_admin
INVITE_USERS = _owner_admin
OAUTH_APPLICATIONS = _owner_admin
VIEW_USERS = _owner_admin
