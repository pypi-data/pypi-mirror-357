from setuptools import setup, find_packages

setup(
    name='xamppfixer',
    version='1.0.0',
    author='Sumit Poudel',
    author_email='sumitpoudel79@gmail.com',
    description='Automatic XAMPP fixer tool for Windows',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xfix = xamppfixer.fixer:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.6',
)
