from setuptools import setup, find_packages
 
setup(
    name='django-ilib',
    version='0.1.0',
    description='Django Library with additional fields, widgets and useful chings',
    author='Ildus Kurbangaliev',
    author_email='i.kurbangaliev@gmail.com',
    url='http://github.com/ildus/django-ilib',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools', 'django-treebeard', 'sorl-thumbnail', 'south'],
)
