from setuptools import setup, find_packages

setup(
    name='pybcrobot',
    version='0.1.0',
    description='A colorful AI chatbot for the terminal using OpenRouter API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your@email.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'colorama'
    ],
    python_requires='>=3.7',
)