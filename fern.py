import os
from urllib.parse import urlparse


__version__ = '0.1'
__author__ = "Carl Meyer"


class Env:
    """Utility for getting settings from the OS environ.

    Instantiate with the name of an env var to get the current mode from (that
    env var should be set to one of VALID_MODES, or not set), then call the
    instantiated Env to read individual settings from the environ (see
    docstring for ``__call__``).

    """
    DEFAULT_VALID_MODES = ['dev', 'prod']
    NOT_PROVIDED = object()

    def __init__(self, mode_env_var=None, valid_modes=None, default_mode=None):
        self.mode_env_var = mode_env_var
        self.valid_modes = valid_modes or self.DEFAULT_VALID_MODES
        self.default_mode = default_mode or self.valid_modes[0]
        if self.mode_env_var:
            self.mode = os.environ.get(self.mode_env_var, self.default_mode)
        else:
            self.mode = self.default_mode
        if self.mode not in self.valid_modes:
            raise ValueError(
                "Mode from %s env var must be one of %s, not %r."
                % (self.mode_env_var, self.valid_modes, self.mode)
            )

    def __call__(self, keys, default=NOT_PROVIDED, mode_defaults=None, coerce=str):
        """Get a value from the OS environ.

        First argument is either a string (an environment variable to get) or a
        list of strings (a list of environment variables, where the first one
        that is set will be used).

        The ``default`` argument can be set to a value to use if the given
        environment variable(s) are not found. The ``coerce`` function is still
        applied to the default value, unless the default is ``None``.

        The ``mode_defaults`` argument can also be a dictionary where the keys
        are mode names (e.g. 'dev', 'prod') and the values are the default to
        use for that mode. If both ``mode_defaults`` and ``defaults`` are
        given, ``mode_defaults`` is checked first, and then ``default`` is used
        as fallback if the current mode is not found there. If
        ``mode_defaults`` is given and ``default`` is not, and no mode default
        is given for the current mode, and the environment variable is not set,
        ``ValueError`` is raised.

        The ``coerce`` argument should be a unary function to convert the
        environment variable's value (which will always be a string) into the
        appropriate Python data type (the default is to leave it as a string).

        """
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            val = os.environ.get(key)
            if val is not None:
                break

        if val is None:
            if mode_defaults is not None:
                default = mode_defaults.get(self.mode, default)

            if default is self.NOT_PROVIDED:
                raise ValueError(
                    "Environment variable %r is required." % keys)
            val = default

        return coerce(val) if val is not None else val

    def boolean(self, keys, default=NOT_PROVIDED):
        """Shortcut to set ``coerce=fern.parse_boolean``."""
        return self(keys, default=default, coerce=parse_boolean)

    def comma_list(self, keys, default=NOT_PROVIDED):
        """Shortcut to set ``coerce=fern.parse_comma_list``."""
        return self(keys, default=default, coerce=parse_comma_list)

    def integer(self, keys, default=NOT_PROVIDED):
        """Shortcut to set ``coerce=int``."""
        return self(keys, default=default, coerce=int)


def parse_boolean(s):
    """Parse an environment variable string into a boolean.

    Considers empty string, '0', 'no', or 'false' (case insensitive) to be
    ``False``; all other values are ``True``.

    """
    return s.lower() not in {'', '0', 'n', 'f', 'no', 'false'}


def parse_comma_list(s):
    """Parse comma-separated list in env var to Python list."""
    if not s.strip():
        return []
    return [b.strip() for b in s.split(',')]


def parse_dj_database_url(url):
    """Parse a database URI into a Django db config dictionary.

    Also adds an ``ENGINE`` key: ``django.db.backends.postgresql_psycopg2`` for
    Postgres. No other database is supported.

    E.g. parses ``postgres://user:pass@host:port/dbname`` into::

        {
            'NAME': 'dbname',
            'USER': 'user',
            'PASSWORD': 'pass',
            'HOST': 'host',
            'PORT': 'port',
            'ENGINE': 'django_postgrespool',
        }

    """
    url_parts = urlparse(url)
    return {
        'NAME': url_parts.path[1:],
        'USER': url_parts.username,
        'PASSWORD': url_parts.password,
        'HOST': url_parts.hostname,
        'PORT': url_parts.port,
        'ENGINE': {
            'postgres': 'django.db.backends.postgresql_psycopg2',
        }[url_parts.scheme],
    }
