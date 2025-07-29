from setuptools import setup, find_packages

setup(
    name='django-proj-chat',
    version='0.1.1',
    description='A reusable Django app for real-time instant messaging',
    author='George',
    author_email='georgedjangodev@gmail.com',
    url='https://github.com/cangeorgecode/django_im',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.0',
        'channels>=4.0',
        'channels-redis>=4.0',
        'daphne>=4.0',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)