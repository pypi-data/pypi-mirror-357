from setuptools import setup, find_packages

setup(
    name='smtp-py',  
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'requests',
        'dotenv'
    ],
    author='Long Nguyen',
    author_email='nguyenlongdev@proton.me',
    description='Unofficial smtp.dev API written in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nguy3nlong/smtp-py', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
