"""
This package contains customisations specific to the Girl Effect project.
The technical background can be found here:
https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#additional-optional-configuration
"""
import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import Permission


USERNAME_FIELD = "username"
EMAIL_FIELD = "email"

LOGGER = logging.getLogger(__name__)


def _update_user_from_claims(user, claims):
    """
    Update the user profile with information from the claims.
    This function is called on registration (new user) as well as login events.
    This function provides the mapping from the OIDC claims fields to the
    internal user profile fields.
    We use the role names as the names for Django
    Groups to which a user belongs.
    :param user: The user profile
    :param claims: The claims for the profile
    """
    LOGGER.debug("Updating user {} with claims: {}".format(user, claims))

    user.first_name = claims.get("given_name") or claims.get("nickname", "")
    user.last_name = claims.get("family_name", "")
    user.email = claims.get("email", "")
    user.save()

    # Synchronise the roles that the user has.
    # The list of roles may contain more or less roles
    # than the previous time the user logged in.
    roles = set(claims.get("roles", []))

    # If the user has any role, we assume that it is a superuser while
    # the permissions are being integrated with the Auth Service
    # (Currently all admin users are superusers)
    # This is to get logging in working on Core QA site and will change
    if roles:
        wagtail_permission = Permission.objects.get(
            content_type__app_label='wagtailadmin', codename='access_admin')
        user.user_permissions.add(wagtail_permission)
        user.is_superuser = True
        user.save()


class GirlEffectOIDCBackend(OIDCAuthenticationBackend):

    def filter_users_by_claims(self, claims):
        """
        The default behaviour is to look up users based on their email
        address. However, in the Girl Effect ecosystem the email is optional,
        so we prefer to use the UUID associated with the user profile (
        subject identifier)
        :return: A user identified by the claims, else None
        """
        uuid = claims["sub"]
        try:
            kwargs = {USERNAME_FIELD: uuid}
            user = self.UserModel.objects.get(**kwargs)
            # Update the user with the latest info
            _update_user_from_claims(user, claims)
            return [user]
        except self.UserModel.DoesNotExist:
            LOGGER.debug("Lookup failed based on {}".format(kwargs))

        return self.UserModel.objects.none()

    def create_user(self, claims):
        """Return object for a newly created user account.
        The default OIDC client create_user() function expects an email address
        to be available. This is not the case for Girl Effect accounts, where
        the email field is optional.
        We use the user id (called the subscriber identity in OIDC) as the
        username, since it is always available and guaranteed to be unique.
        """
        username = claims.get("sub")  # The sub field _must_ be in the claims.
        email = claims.get("email", "")  # Email is optional
        # We create the user based on the username and optional email fields.
        if email:
            user = self.UserModel.objects.create_user(username, email)
        else:
            user = self.UserModel.objects.create_user(username)
        _update_user_from_claims(user, claims)
        return user

    def verify_claims(self, claims):
        """
        This function can be used to prevent authorisation of users based
        on claims information.
        """
        verified = super(GirlEffectOIDCBackend, self).verify_claims(claims)
        return verified

    def verify_token(self, token, **kwargs):
        site = self.request.site
        if not hasattr(site, "oidcsettings"):
            raise RuntimeError(
                "Site {} has no settings configured.".format(site))

        self.OIDC_RP_CLIENT_SECRET = site.oidcsettings.oidc_rp_client_secret
        return super(GirlEffectOIDCBackend, self).verify_token(token, **kwargs)

    def authenticate(self, **kwargs):
        if "request" in kwargs:
            site = kwargs["request"].site
            if not hasattr(site, "oidcsettings"):
                raise RuntimeError(
                    "Site {} has no settings configured.".format(site))

            self.OIDC_RP_CLIENT_ID = site.oidcsettings.oidc_rp_client_id
            self.OIDC_RP_CLIENT_SECRET = \
                site.oidcsettings.oidc_rp_client_secret
        return super(GirlEffectOIDCBackend, self).authenticate(**kwargs)
