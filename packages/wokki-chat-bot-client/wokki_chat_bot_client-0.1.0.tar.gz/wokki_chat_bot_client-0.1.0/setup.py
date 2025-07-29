from setuptools import setup, find_packages

setup(
    name='wokki_chat_bot_client',
    version='0.1.0',
    description='Python client for wokki chat bots',
    author='wokki20',
    packages=find_packages(include=['wokki_chat_bot', 'wokki_chat_bot.*']),
    install_requires=[
        'python-socketio[client]'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
