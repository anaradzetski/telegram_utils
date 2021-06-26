import setuptools

setuptools.setup(
    name='telegram-utils',
    version='0.0.1',
    author='Naradzetski Andrey',
    author_email='andrey.naradzetski@gmail.com',
    url='https://github.com/anaradzetski/telegram_recursive_keyboard',
    packages=['telegram_utils'],
    install_requires=[
        'python-telegram-bot>=13.5'
    ],
    python_requires='>=3.6'
)
