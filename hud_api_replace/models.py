import logging

from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

logger = logging.getLogger(__name__)


class ZipCode(models.Model):
    """known zip codes"""
    zip = models.CharField(max_length=5, primary_key=True)
    lat = models.FloatField('Latitude', null=True)
    lon = models.FloatField('Longitude', null=True)


@python_2_unicode_compatible
class CounselingAgency(models.Model):
    # example result can be obtained from
    # http://data.hud.gov/Housing_Counselor/searchByLocation?Lat=38.853231&Long=-77.305097&Distance=10
    #
    agcid = models.CharField(null=False, max_length=9)     # Counseling Agency ID, ex. "80999"
    source_data_hash = models.CharField(max_length=65, blank=True)      # ex "78fffe8593ee3ec447d03395b3609da2ae55036f1e84f25de858a024755f61bc"
    geocode_address_override = models.CharField(max_length=255, blank=True)
    adr1 = models.CharField(max_length=255)                 # ex "153 E. Chestnut Hill Street",
    adr2 = models.CharField(max_length=255)                 # ex "Robscott Building, Suite 122",
    city = models.CharField(max_length=255)                 # ex "NEWARK",
    email = models.CharField(max_length=100)                # ex "johndoe@example.com",
    fax = models.CharField(max_length=20)                   # ex "302-224-4088",
    nme = models.CharField(max_length=255)                  # ex "YWCA DELAWARE",
    phone1 = models.CharField(max_length=20)                # ex "302-224-4060-292",
    statecd = models.CharField(max_length=2)                # ex "DE",
    weburl = models.CharField(max_length=255)               # ex "http://www.example.com",
    zipcd = models.CharField(max_length=10)                 # ex "19713-4946",
    agc_ADDR_LATITUDE = models.FloatField(null=True)
    agc_ADDR_LONGITUDE = models.FloatField(null=True)     # ex "-75.74669",
    languages = models.CharField(max_length=255)            # ex "ENG,SPA",
    # These can get really lengthy, and those agencies won't be installed as a result
    services = models.CharField(max_length=1500)             # ex "DFC,DFW,FBC,NDW,PPC,PPW",
    parentid = models.CharField(max_length=9)               # ex "81219",
    county_NME = models.CharField(max_length=255)           # ex "",
    phone2 = models.CharField(max_length=20)                 # ex " ",
    mailingadr1 = models.CharField(max_length=255)          # ex "154 E. Chestnut Hill Road",
    mailingadr2 = models.CharField(max_length=255)          # ex "Robscott Building, Suite 122",
    mailingcity = models.CharField(max_length=255)          # ex "Newark",
    mailingzipcd = models.CharField(max_length=10)          # ex "19713",
    mailingstatecd = models.CharField(max_length=2)         # ex "DE",
    state_NME = models.CharField(max_length=50)             # ex "Delaware",
    state_FIPS_CODE = models.CharField(max_length=255)      # ex null,
    faithbased = models.BooleanField()                          # ex "Y",
    colonias_IND = models.BooleanField()                        # ex "N",
    migrantwkrs_IND = models.BooleanField()                     # ex "N",
    agc_STATUS = models.CharField(max_length=255)           # ex "C",
    agc_SRC_CD = models.CharField(max_length=255)           # ex "HUD",
    counslg_METHOD = models.CharField(max_length=255)       # ex null
    updated = models.DateTimeField(auto_now=True)
    correction_needed = models.DateTimeField(null=True)

    def __str__(self):
        return self.nme

    @property
    def address(self):
        components = [self.adr1, ]
        return ' '.join(components)

    def update(self, data, save=False):
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
            elif value is None and key in ('agc_ADDR_LATITUDE',
                                           'agc_ADDR_LONGITUDE'):
                continue  # never null out coordinates
            else:
                raise AttributeError("CounselingAgency has no %s field" % key)
        if save:
            self.save()

    def has_coords(self):
        return bool(self.agc_ADDR_LATITUDE and self.agc_ADDR_LONGITUDE)

    def geocode(self, geocoder):
        if self.geocode_address_override:
            address = self.geocode_address_override
        else:
            address = ",".join([self.adr1, self.adr2, self.city, self.statecd])

        result = geocoder(address)

        if result.quality > .9:
            self.agc_ADDR_LATITUDE = result.lat
            self.agc_ADDR_LONGITUDE = result.lng
            self.correction_needed = None
        else:
            logger.warning("oh no")
            self.correction_needed = timezone.now()

    def updated_since_last_failure(self):
        return self.updated > self.correction_needed

    def geocode_if_needed(self, geocoder):
        if (not self.has_coords() or self.updated_since_last_failure):
            self.geocode(geocoder)

@python_2_unicode_compatible
class Language(models.Model):
    abbr = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Service(models.Model):
    abbr = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
