import pytest

import fern


class TestEnv:
    def test_mode(self, monkeypatch):
        """Instantiate with name of env var whose value contains the mode."""
        monkeypatch.setenv('MY_MODE', 'dev')

        assert fern.Env('MY_MODE').mode == 'dev'

    def test_invalid_mode(self, monkeypatch):
        """Invalid mode raises ValueError."""
        monkeypatch.setenv('SOME_MODE', 'foo')

        with pytest.raises(ValueError) as cm:
            fern.Env('SOME_MODE')

        assert str(cm.value) == (
            "Mode from SOME_MODE env var must be one of ['dev', 'prod'], not 'foo'.")

    def test_default_mode(self, monkeypatch):
        """Default mode is 'dev'."""
        monkeypatch.delenv('MODE', raising=False)

        assert fern.Env('MODE').mode == 'dev'

    def test_specify_valid_modes(self, monkeypatch):
        monkeypatch.setenv('A_MODE', 'good')

        assert fern.Env('A_MODE', ['good', 'bad']).mode == 'good'

    def test_specify_valid_modes_and_default(self, monkeypatch):
        monkeypatch.delenv('MODE', raising=False)

        assert fern.Env('MODE', ['good', 'bad'], 'bad').mode == 'bad'

    def test_no_mode_env_var(self):
        assert fern.Env().mode == 'dev'

    @pytest.fixture
    def env(self, monkeypatch):
        """Get an Env instance with default mode."""
        monkeypatch.delenv('MODE', raising=False)

        return fern.Env('MODE')

    def test_call_single_key(self, env, monkeypatch):
        """Calling with single env var name gets value of that env var."""
        monkeypatch.setenv('FOO', 'bar')

        assert env('FOO') == 'bar'

    def test_fallback_key(self, env, monkeypatch):
        """Can provide a list of env vars; will use first one set."""
        monkeypatch.delenv('BAZ', raising=False)
        monkeypatch.setenv('FOO', 'bar')

        assert env(['BAZ', 'FOO']) == 'bar'

    def test_default(self, env, monkeypatch):
        """Can provide a default in case env var is not set."""
        monkeypatch.delenv('FOO', raising=False)

        assert env('FOO', default='bar') == 'bar'

    def test_per_mode_default(self, env, monkeypatch):
        """Can provide per-mode defaults dict."""
        monkeypatch.delenv('FOO', raising=False)

        assert env('FOO', mode_defaults={'dev': 'one', 'prod': 'two'}) == 'one'

    def test_per_mode_default_with_fallback_default(self, env, monkeypatch):
        """Can provide per-mode defaults dict."""
        monkeypatch.delenv('FOO', raising=False)

        assert env('FOO', default='def', mode_defaults={'prod': 'two'}) == 'def'

    def test_per_mode_default_with_no_fallback_default(self, env, monkeypatch):
        """Can provide per-mode defaults dict."""
        monkeypatch.delenv('FOO', raising=False)

        with pytest.raises(ValueError):
            env('FOO', mode_defaults={'prod': 'two'})

    def test_no_default_raises(self, env, monkeypatch):
        """If no default given, missing env var raises ValueError."""
        monkeypatch.delenv('FOO', raising=False)

        with pytest.raises(ValueError):
            env('FOO')

    def test_coerce(self, env, monkeypatch):
        """Can provide a coerce function for the eventual value."""
        monkeypatch.setenv('FOO', '10')

        assert env('FOO', coerce=int) == 10

    def test_coerce_default(self, env, monkeypatch):
        """Coercion function applies to default values, too."""
        monkeypatch.delenv('FOO', raising=False)

        assert env('FOO', coerce=int, default='10') == 10

    def test_no_coerce_none(self, env, monkeypatch):
        """Won't attempt to call the coerce function on None."""
        monkeypatch.delenv('FOO', raising=False)

        assert env('FOO', coerce=int, default=None) is None

    def test_boolean(self, env, monkeypatch):
        """Can parse boolean from env."""
        monkeypatch.setenv('GOOD', 'true')
        monkeypatch.delenv('BAD', raising=False)

        assert env.boolean('GOOD') is True
        assert env.boolean('BAD', default='1') is True
        assert env.boolean('BAD', mode_defaults={env.mode: 't'}) is True

    def test_integer(self, env, monkeypatch):
        """Can parse int from env."""
        monkeypatch.setenv('QUANTITY', '6')
        monkeypatch.delenv('QTY', raising=False)

        assert env.integer('QUANTITY') == 6
        assert env.integer('QTY', default='3') == 3
        assert env.integer('QTY', mode_defaults={env.mode: '4'}) == 4

    def test_comma_list(self, env, monkeypatch):
        """Can parse comma separated list from env."""
        monkeypatch.setenv('HOSTS', 'a,b,c')
        monkeypatch.delenv('HOSTZ', raising=False)

        assert env.comma_list('HOSTS') == ['a', 'b', 'c']
        assert env.comma_list('HOSTZ', default='a,b') == ['a', 'b']
        assert env.comma_list('HOSTZ', mode_defaults={env.mode: 'a,b'}) == ['a', 'b']


@pytest.mark.parametrize(
    'inv,outv',
    [
        ('', False),
        ('0', False),
        ('no', False),
        ('FALSE', False),
        ('F', False),
        ('n', False),
        ('t', True),
        ('True', True),
        ('1', True),
    ]
)
def test_parse_boolean(inv, outv):
    assert fern.parse_boolean(inv) == outv


@pytest.mark.parametrize(
    'inv,outv',
    [
        ('foo, bar, baz', ['foo', 'bar', 'baz']),
        ('', []),
        ('foo', ['foo']),
    ]
)
def test_parse_comma_list(inv, outv):
    assert fern.parse_comma_list(inv) == outv


@pytest.mark.parametrize(
    'inv,outv',
    [
        (
            'postgres:///foo',
            {
                'NAME': 'foo',
                'USER': None,
                'PASSWORD': None,
                'HOST': None,
                'PORT': None,
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
            }
        ),
        (
            'postgres://user:password@somehost:5432/foo',
            {
                'NAME': 'foo',
                'USER': 'user',
                'PASSWORD': 'password',
                'HOST': 'somehost',
                'PORT': 5432,
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
            }
        ),
    ]
)
def test_parse_dj_database_url(inv, outv):
    assert fern.parse_dj_database_url(inv) == outv
