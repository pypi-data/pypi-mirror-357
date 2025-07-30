from setuptools import setup, find_packages

setup(
    name='constructor_groups',
    version='0.2.5',
    author='Constructor Groups Dev Team',
    author_email='python+ozan@constructor.tech',
    description='Constructor Groups Python Software Development Kit',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    packages=['constructor_groups'],
    package_dir={'constructor_groups':'constructor_groups'},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'python-dotenv==1.0.1',
        'requests==2.32.3',
        'urllib3==2.2.2'
    ],
)