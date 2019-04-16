"""
   Copyright 2019 Datacom Systems Limited

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from setuptools import setup
from setuptools import find_packages

version = '1.0.0'

install_requires = [
    'certbot',
    'zope.interface',
    'setuptools',
    'azure-mgmt-dns',
]

setup(
    name='datacom-dns-azure',
    version = version,
    description = 'Azure DNS Authenticator plugin for Certbot',
    url = 'https://www.datacom.co.nz/',
    license = 'Apache License 2.0',
    author = "Craig McGeachie",
    python_requires = '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    package_dir = {'':'src'},
    packages = find_packages('src'),

    install_requires = install_requires,
    keywords = ['certbot', 'azure'],
    entry_points = {
        'certbot.plugins': [
            'dns-azure = datacom_dns_azure.dns_azure:Authenticator'
        ]
    }
)