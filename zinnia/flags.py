"""
Comment flags for Zinnia

This module defines constants and a utility function related to
flagging comments as `pingback` or `trackback` within the Zinnia
blogging platform.

It supports associating these flags with a system-defined user (flagger)
used internally by Zinnia to mark such comments automatically.
"""

from django.contrib.auth import get_user_model
from django.utils.lru_cache import lru_cache

from zinnia.settings import COMMENT_FLAG_USER_ID

# Constants representing types of automatic comment flags
PINGBACK = 'pingback'
TRACKBACK = 'trackback'

# Default username for the system flagger account
FLAGGER_USERNAME = 'Zinnia-Flagger'


@lru_cache(1)
def get_user_flagger():
    """
    Retrieve or create the system user responsible for flagging comments.

    This user is used by Zinnia internally to mark comments as `pingback` or
    `trackback`, representing automatic external interactions like linkbacks.

    The function tries the following in order:
    1. Fetch the user by a specific user ID defined in `COMMENT_FLAG_USER_ID`
    2. If not found, fetch the user by the default username `Zinnia-Flagger`
    3. If still not found, create a new user with that username

    Returns:
        User (Django user model): The system flagger user instance.

    Note:
        This function is cached using `lru_cache` to prevent multiple
        database hits during a single runtime session.
    """
    user_klass = get_user_model()
    try:
        # Try to get user by primary key (usually set in settings)
        user = user_klass.objects.get(pk=COMMENT_FLAG_USER_ID)
    except user_klass.DoesNotExist:
        try:
            # Try to get user by default flagger username
            user = user_klass.objects.get(
                **{user_klass.USERNAME_FIELD: FLAGGER_USERNAME})
        except user_klass.DoesNotExist:
            # Create the user if none exists
            user = user_klass.objects.create_user(FLAGGER_USERNAME)
    return user
