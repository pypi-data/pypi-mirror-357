from setuptools import setup, find_packages

setup(
    name='netgraphix',
    version='0.1.0',
    author='Adam Alcander et Eden',
    author_email='aeden6877@gmail.com',
    description='A real-time local network connection analyzer with live graphs, stats, and CLI.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/EdenGithhub/netgraphix',
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'numpy',
        'colorama',
        'psutil',
        'requests',
        'tqdm',
        'pyfiglet',
        'scapy',
        'rich',
        'pandas',
        'click',
        'tabulate',
        'py-cpuinfo'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: System :: Networking',
        'Topic :: Utilities',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'netgraphix=netgraphix.core:main'
        ],
    },
    include_package_data=True,
)
