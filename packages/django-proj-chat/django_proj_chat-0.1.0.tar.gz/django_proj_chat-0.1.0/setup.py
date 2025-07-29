from setuptools import setup, find_packages

setup(
    name='django-proj-chat',
    version='0.1.0',
    description='A reusable Django app for real-time instant messaging',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/django-proj-chat',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=5.0',
        'channels>=4.0',
        'channels-redis>=4.0',
        'daphne>=4.0',  # Added
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)