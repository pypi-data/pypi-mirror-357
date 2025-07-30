from setuptools import setup, find_packages

setup(
    name='etude_structure_package',
    version='1.6',
    # package_dir={"": "src"},
    packages=find_packages(),
    description='Un package destiné à montrer la structure d\'un package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Georges CAPLANDE',
    author_email='georges.caplande@gmail.com',
        classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    python_requires='>=3.6',
    install_requires=[],
)