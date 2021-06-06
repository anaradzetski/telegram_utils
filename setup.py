import setuptools

setuptools.setup(
    name='telegram-utils',
    version='0.0.1',
    author='Naradzetski Andrey',
    author_email='andrey.naradzetski@gmail.com',
    url='https://github.com/anaradzetski/telegram_recursive_keyboard',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6'
)
