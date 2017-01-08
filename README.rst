====
fern
====

You want to be all `12factor`_ and read your config from the environ.

You also deploy your project in a variety of environments (dev, staging,
prod...) and you want to be able to build in sane defaults for some of those
environments (dev especially) so you don't have to carry around huge
boilerplate ``.env`` files that aren't in version control. But you don't want
to risk those built-in dev defaults silently getting used in production.

Fern's got your back.

In the simplest case, a ``fern.Env`` instance lets you call it to read strings
from the environ::

  >>> env = fern.Env()
  >>> env('FOO')
  'bar'

If we tried that and the ``FOO`` env var were not set, we'd get a
``ValueError`` instead. Maybe that's OK, if this is a critical config value
that should always be set explicitly in the environ. If it's less critical, we
can set a default::

  >>> env = fern.Env()
  >>> env('DOES_NOT_EXIST', default='hey')
  'hey'

We can also give a list of names of env vars, and fern will check each one and
give us the first value that's set::

  >>> env = fern.Env()
  >>> env(['DOES_NOT_EXIST', 'DOES_EXIST'])
  'value_of_DOES_EXIST'

All environment values are strings. What if we want to parse this string into a
more structured data type? We can pass any unary coercion function to be
applied to the value; e.g. the ``int`` type itself works as a unary coercion
function: passed one string, it'll return that string parsed as an integer::

  >>> env = fern.Env()
  >>> env('SOME_INT', coerce=int)
  6

You can write any function you like that takes in a string and returns
whatever, and pass it to ``coerce``. For instance,
``fern.parse_dj_database_url`` will parse a database URL like
``'postgres://localhost/dname'`` and return a Django-style database connection
info dictionary.

The ``Env`` class has a few convenience methods for certain common values of
``coerce``::

  >>> env = fern.Env()
  >>> env.integer('SOME_INT')
  6
  >>> env.boolean('SOME_BOOL')
  True
  >>> env.comma_list('SOME_LIST')
  ['a', 'b', 'c']

The ``integer`` method just sets ``int`` as the coercion function.

The ``boolean`` method sets ``fern.parse_boolean`` as the coercion function; it
considers the empty string, ``'0'``, ``'no'``, ``'f'``, ``'n'`` and ``'false'``
to be ``False``; anything else is ``True``.

The ``comma_list`` method sets ``fern.parse_comma_list`` as the coercion
function; it splits the env value on commas and returns the resulting values as
a list.

Now let's make things a bit more complex. Let's say we want two deployment
modes, ``dev`` and ``prod``, and we've got a config value ``SECRET_KEY``. In
dev mode, we want this value to default to ``"dev secret"`` (but still be
overridable via the ``SECRET_KEY`` env var). In prod mode, we want to error out
if the ``SECRET_KEY`` env var is not set explicitly; no hardcoded default could
be safe for production use. We can achieve that like this::

  >>> env = fern.Env('MODE', valid_modes=['dev', 'prod'])
  >>> env('SECRET_KEY', mode_defaults={'dev': "dev secret"})

Let's unpack that a bit.

In the first line, we tell Fern that our valid modes are ``dev`` or ``prod``,
and that an env var named ``MODE`` will tell us which mode we are in. (The
default mode is the first one listed, so if ``MODE`` is not set we'll be in
``dev`` mode. If ``MODE`` is set to something not listed in ``valid_modes``,
we'll get a ``ValueError``).

In the second line, we supply a dictionary for the ``mode_defaults``
argument. The keys in this dictionary are mode names, and the values are
defaults to use for that mode. In this case, we supply a default only for
``dev`` mode; in ``prod`` mode if the ``SECRET_KEY`` env var is not set, you'll
get a ``ValueError``. So for our prod deployments, all we have to make sure to
do is set ``MODE=prod``, and that ensures the server won't start unless we also
supply the rest of the required config. In dev mode, we don't need any env vars
at all.

.. _12factor: https://12factor.net/
