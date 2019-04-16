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

from zope import interface

from certbot import interfaces
from certbot.plugins import dns_common
from certbot import errors

from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.dns import DnsManagementClient
from azure.mgmt.dns.models import ZoneType

@interface.implementer(interfaces.IAuthenticator)
@interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    '''
    This authenticator solves a DNS01 challenge by uploading the answer to Azure DNS.
    '''

    description = ("Obtain certificates using a DNS TXT record (if you are using Microsoft Azure for "
                   "DNS).")

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        super(Authenticator, self).__init__(*args, **kwargs)
        self.dnsMgtClient = get_client_from_auth_file(DnsManagementClient)

    @classmethod
    def add_parser_arguments(cls, add):  # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add)
        add('resource-goup',
            action='append',
            help='A resource group to search for DNS zones.')

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return "Solve a DNS01 challenge using Azure DNS"


    def _setup_credentials(self):  # pragma: no cover
        pass
    
    def _perform(self, domain, validation_domain_name, validation):  # pragma: no cover
        """
        Performs a dns-01 challenge by creating a DNS TXT record.

        :param str domain: The domain being validated.
        :param str validation_domain_name: The validation record domain name.
        :param str validation: The validation record content.
        :raises errors.PluginError: If the challenge cannot be performed
        """
        self.dnsMgtClient.record_sets.create_or_update(
            *self._find_record_set(validation_domain_name),
            'TXT',
            {
                "ttl": 60,
                "txt_records": [
                    { "value": [validation] }
                ]
            }
        )
    
    def _cleanup(self, domain, validation_domain_name, validation):  # pragma: no cover
        """
        Deletes the DNS TXT record which would have been created by `_perform_achall`.

        :param str domain: The domain being validated.
        :param str validation_domain_name: The validation record domain name.
        :param str validation: The validation record content.
        """
        self.dnsMgtClient.record_sets.delete(
            *self._find_record_set(validation_domain_name),
            'TXT'
        )

    def _find_record_set(self, validation_domain_name):
        """Find the resource group, zone and record set for a given FQDN.
        
        :param str validation_domain_name: The validation record domain.
        :return: A 3-tuple (Resource group, Zone name, TXT resource name)
        """
        if not self.conf('resource-goup'):
            raise errors.PluginError("No resource groups specified.")

        zones = []
        for resourceGroup in self.conf('resource-goup'):
            for zone in self.dnsMgtClient.zones.list_by_resource_group(resourceGroup):
                if zone.zone_type != ZoneType.public:
                    continue
                if validation_domain_name.rstrip('.').endswith(zone.name.rstrip('.')):
                    zones.append((resourceGroup, zone.name))

        if not zones:
            raise errors.PluginError("Unable to find an Azure hosted zone for {0}".format(validation_domain_name))

        zones.sort(key=lambda z: len(z[1]), reverse=True) # Use the longest matching DNS zone.
        resourceGroup, zone = zones[0]
        record = validation_domain_name[0:len(validation_domain_name)- len(zone)].rstrip('.')
        return resourceGroup, zone, record

