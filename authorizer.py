from nio.modules.security.authorizer import Unauthorized
from nio.modules.security.user import User, CoreServiceAccount
from nio.modules.security.task import SecureTask
from nio.modules.security.permissions import Permissions

from .first_gen_security import handle_backwards_compatibility


class Authorizer(object):

    _permissions = {}
    _no_permissions = Permissions()

    @classmethod
    def _configure_permissions(cls, permissions):
        # handle old permissions style backwards compatibility
        handle_backwards_compatibility(permissions)

        # store the resulting parsed permissions for each username
        cls._permissions = \
            {username: Permissions(user_permissions)
             for username, user_permissions in permissions.items()}

    @classmethod
    def authorize(cls, user, task):
        if not isinstance(user, User) or not isinstance(task, SecureTask):
            raise Unauthorized()

        # Assume the core service account is authorized
        if isinstance(user, CoreServiceAccount):
            return

        perms = cls._get_permissions_for_user(user.name)
        # See if the permission we are checking is in the user's
        # permission set
        if perms.get(task.resource, task.permission):
            # The permission matches, return indicating they are
            # authorized
            return

        # Didn't find the permission, guess we're not authorized
        raise Unauthorized()

    @classmethod
    def _get_permissions_for_user(cls, username):
        """ Function to return permissions for a user
        """
        return cls._permissions.get(username, cls._no_permissions)
