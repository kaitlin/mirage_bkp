import logging

import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from vendor.models import Vendor, Pool, SetAside, SamLoad


class Command(BaseCommand):
    """
    Loops through each vendor in database and adds SAM information to its record
    """

    logger = logging.getLogger('sam')

    def get_value(self, obj, key, vendor):
        try:
            return obj[key]
        except KeyError as k:
            self.logger.debug("There was a key error on {0}: {1}".format(vendor.duns, k))
            return None

    def handle(self, *args, **kwargs):

        vendors = Vendor.objects.all()
        for v in vendors:
            #get SAM.gov API response for this vendor
            uri = settings.SAM_API_URL + v.duns_4 + '?api_key=' + settings.SAM_API_KEY
            sam_data = requests.get(uri).json()
   
            if 'sam_data' in sam_data:
                if 'registration' in sam_data['sam_data']:
                    reg = sam_data['sam_data']['registration']
                    v.sam_status = self.get_value(reg, 'status', v)
                    v.sam_activation_date = self.get_value(reg, 'activationDate', v)
                    v.sam_expiration_date = self.get_value(reg, 'expirationDate', v)
                    v.sam_exclusion = self.get_value(reg, 'hasKnownExclusion', v)
                    v.cage = self.get_value(reg, 'cage', v)
                    addr = self.get_value(reg, 'samAddress', v)
                    if addr:
                        v.sam_address = self.get_value(addr, 'Line1', v)
                        v.sam_citystate = "{0}, {1} {2}".format(self.get_value(addr, 'City', v), 
                                                                  self.get_value(addr, 'stateorProvince', v), 
                                                                  self.get_value(addr, 'Zip', v))
                
                    v.sam_url = self.get_value(reg, 'corporateUrl', v)

                    setasides = self.get_value(reg, 'businessTypes', v)
                    for code in setasides:
                        try:
                            sa = SetAside.objects.get(code__iexact=code)
                            if sa not in v.setasides.all():
                                v.setasides.add(sa)

                        except SetAside.DoesNotExist:
                            continue
                    v.save()
                    
                else:
                    self.logger.debug("'registration' key is missing for {}".format(uri))

            elif 'Error' in sam_data:
                self.logger.debug("SAM API returned an error for {0}, and duns {1}".format(uri, v.duns ))
            else:
                self.logger.debug("Could not load data from {} for unknown reason".format(uri))

        sam_load = SamLoad(sam_load=timezone.now())
        sam_load.save()
