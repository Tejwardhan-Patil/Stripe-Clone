from enum import Enum
from typing import List, Dict

class Role(Enum):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'
    GUEST = 'guest'

class Permission(Enum):
    READ = 'read'
    WRITE = 'write'
    DELETE = 'delete'
    UPDATE = 'update'

class AccessControl:
    def __init__(self):
        # Define role-based access control matrix
        self.role_permissions: Dict[Role, List[Permission]] = {
            Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.UPDATE],
            Role.USER: [Permission.READ, Permission.WRITE],
            Role.MODERATOR: [Permission.READ, Permission.UPDATE],
            Role.GUEST: [Permission.READ]
        }

    def get_permissions_for_role(self, role: Role) -> List[Permission]:
        # Return permissions assigned to the role
        return self.role_permissions.get(role, [])

    def add_permission_to_role(self, role: Role, permission: Permission):
        # Add permission to the role
        if role in self.role_permissions:
            if permission not in self.role_permissions[role]:
                self.role_permissions[role].append(permission)

    def remove_permission_from_role(self, role: Role, permission: Permission):
        # Remove permission from the role
        if role in self.role_permissions and permission in self.role_permissions[role]:
            self.role_permissions[role].remove(permission)

    def check_permission(self, role: Role, permission: Permission) -> bool:
        # Check if role has the specific permission
        return permission in self.role_permissions.get(role, [])

class Resource:
    def __init__(self, name: str):
        self.name = name
        self.permissions: Dict[Role, List[Permission]] = {}

    def set_role_permissions(self, role: Role, permissions: List[Permission]):
        # Set permissions for a role on the resource
        self.permissions[role] = permissions

    def get_permissions_for_role(self, role: Role) -> List[Permission]:
        # Get permissions for a role on the resource
        return self.permissions.get(role, [])

class RoleManager:
    def __init__(self):
        # Dictionary to manage users and their roles
        self.user_roles: Dict[str, Role] = {}

    def assign_role_to_user(self, user_id: str, role: Role):
        # Assign a role to a user
        self.user_roles[user_id] = role

    def remove_role_from_user(self, user_id: str):
        # Remove role from a user
        if user_id in self.user_roles:
            del self.user_roles[user_id]

    def get_user_role(self, user_id: str) -> Role:
        # Return the role assigned to a user
        return self.user_roles.get(user_id, Role.GUEST)

class PermissionChecker:
    def __init__(self, access_control: AccessControl, role_manager: RoleManager):
        self.access_control = access_control
        self.role_manager = role_manager

    def has_permission(self, user_id: str, permission: Permission) -> bool:
        # Check if a user has the specific permission
        user_role = self.role_manager.get_user_role(user_id)
        return self.access_control.check_permission(user_role, permission)

class ResourceAccessManager:
    def __init__(self, permission_checker: PermissionChecker):
        self.permission_checker = permission_checker
        self.resources: Dict[str, Resource] = {}

    def add_resource(self, resource: Resource):
        # Add a resource to the system
        self.resources[resource.name] = resource

    def remove_resource(self, resource_name: str):
        # Remove a resource from the system
        if resource_name in self.resources:
            del self.resources[resource_name]

    def has_access(self, user_id: str, resource_name: str, permission: Permission) -> bool:
        # Check if user has access to a resource
        resource = self.resources.get(resource_name)
        if resource:
            user_role = self.permission_checker.role_manager.get_user_role(user_id)
            resource_permissions = resource.get_permissions_for_role(user_role)
            return permission in resource_permissions
        return False

# Initialization
access_control = AccessControl()
role_manager = RoleManager()
permission_checker = PermissionChecker(access_control, role_manager)
resource_manager = ResourceAccessManager(permission_checker)

# Assign roles to users
role_manager.assign_role_to_user("user1", Role.ADMIN)
role_manager.assign_role_to_user("user2", Role.USER)
role_manager.assign_role_to_user("user3", Role.MODERATOR)
role_manager.assign_role_to_user("user4", Role.GUEST)

# Add resources and set permissions for roles on those resources
resource1 = Resource("billing")
resource1.set_role_permissions(Role.ADMIN, [Permission.READ, Permission.WRITE, Permission.DELETE, Permission.UPDATE])
resource1.set_role_permissions(Role.USER, [Permission.READ, Permission.WRITE])
resource1.set_role_permissions(Role.GUEST, [Permission.READ])
resource_manager.add_resource(resource1)

resource2 = Resource("subscriptions")
resource2.set_role_permissions(Role.ADMIN, [Permission.READ, Permission.WRITE, Permission.UPDATE])
resource2.set_role_permissions(Role.MODERATOR, [Permission.READ, Permission.UPDATE])
resource_manager.add_resource(resource2)

# Check access for users on resources
print(f"User1 has access to billing write: {resource_manager.has_access('user1', 'billing', Permission.WRITE)}")
print(f"User2 has access to billing delete: {resource_manager.has_access('user2', 'billing', Permission.DELETE)}")
print(f"User3 has access to subscriptions update: {resource_manager.has_access('user3', 'subscriptions', Permission.UPDATE)}")
print(f"User4 has access to billing read: {resource_manager.has_access('user4', 'billing', Permission.READ)}")

# Modify role permissions dynamically
access_control.add_permission_to_role(Role.USER, Permission.DELETE)
print(f"User2 has access to billing delete after update: {resource_manager.has_access('user2', 'billing', Permission.DELETE)}")

# Remove role or permission
role_manager.remove_role_from_user('user2')
print(f"User2 has access to billing write after role removal: {resource_manager.has_access('user2', 'billing', Permission.WRITE)}")