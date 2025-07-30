import os
import setuptools

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

def read_requirements():
    return [
        'brotli',
        'uvicorn',
        'fastapi',
        'aiohttp',
        'aiocache',
        'pydantic',
        'user-agent',
        'cache-fastapi',
        'python-dotenv',
        'beautifulsoup4',
        'aiohttp[brotli]'
    ]
setuptools.setup(
    name='llm-pricing',
    version='0.1.3',
    description='A library for scraping and managing LLM pricing information',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='fswair',
    author_email='contact@tomris.dev',
    url='https://github.com/fswair/llm-pricing',
    project_urls={
        'Bug Reports': 'https://github.com/fswair/llm-pricing/issues',
        'Source': 'https://github.com/fswair/llm-pricing'
    },
    packages=['llm_pricing'],
    include_package_data=True,
    package_data={
        'llm-pricing': ['data/*.json'],
    },
    install_requires=read_requirements(),
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='llm pricing, llm api, llm api cost'
)
