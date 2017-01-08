from setuptools import setup


def get_long_description():
    return open('README.rst').read() + "\n\n" + open('CHANGES.rst').read()


def get_version():
    with open('fern.py') as f:
        for line in f:
            if line.startswith('__version__ ='):
                return line.split('=')[1].strip().strip('"\'')


setup(
    name='fern',
    version=get_version(),
    description="Read config from the environment.",
    long_description=get_long_description(),
    author='Carl Meyer',
    author_email='carl@oddbird.net',
    url='https://github.com/carljm/fern/',
    py_modules=['fern.py'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    zip_safe=False,
)
