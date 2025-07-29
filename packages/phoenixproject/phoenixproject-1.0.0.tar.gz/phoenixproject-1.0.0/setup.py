from setuptools import setup, find_packages
import os

setup(
    name='phoenixproject',
    version='1.0.0',
    description='Systeme IA de publication automatique et planification Reddit/Affiliation - Bundle unifie pour la gestion d\'affiliation',
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='PhoenixProject',
    author_email='contact@phonxproject.onmicrosoft.com',
    url='https://github.com/PhoenixGuardianTools/unified_affiliate_bundle',
    license='MIT',
    project_urls={
        'Bug Reports': 'https://github.com/PhoenixGuardianTools/unified_affiliate_bundle/issues',
        'Source': 'https://github.com/PhoenixGuardianTools/unified_affiliate_bundle',
        'Documentation': 'https://github.com/PhoenixGuardianTools/unified_affiliate_bundle#readme',
    },
    packages=find_packages(where="."),
    include_package_data=True,
    install_requires=[
        'flask>=2.0.0'
    ],
    entry_points={
        'console_scripts': [
            'phoenixproject=affiliate_ai.cli:main'
        ]
    },
    keywords=[
        'affiliate', 'reddit', 'automation', 'ai', 'publishing', 
        'scheduling', 'phoenixproject', 'marketing', 'social-media'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Flask',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Email',
        'Topic :: Office/Business :: Financial :: Accounting',
    ],
    python_requires='>=3.8',
    zip_safe=False,
)
