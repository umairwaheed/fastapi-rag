# Who will be performing actions in our application.
actor User {}

# What will actors be acting upon.
resource Organization {}

# A rule stating that users have permission to edit an organization
# if they have the admin role on that organization.
has_permission(user: User, "edit", organization: Organization) if
  has_role(user, "admin", organization);

has_permission(user: User, "read", organization: Organization) if
  has_role(user, "user", organization);
