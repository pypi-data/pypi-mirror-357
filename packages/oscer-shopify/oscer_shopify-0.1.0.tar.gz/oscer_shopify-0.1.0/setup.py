from setuptools import setup, find_packages

setup(
    name='oscer-shopify',
    version='0.1.0',
    description='Python wrapper to fetch Shopify product images and export as CSV',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Usman Shahid',
    author_email='usman@example.com',
    url='https://github.com/oscerpk/oscer_shopify',
    license='MIT',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)