from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class CachedGeodata(models.Model):
    """Model to save geocoding information locally."""
    key = models.CharField(max_length=255, unique=True)
    lat = models.FloatField('Latitude', null=True)
    lon = models.FloatField('Longitude', null=True)
    expires = models.PositiveIntegerField(null=True)

    class Meta:
        index_together = (
            ('key', 'expires'),
        )


@python_2_unicode_compatible
class CounselingAgency(models.Model):
    # example result can be obtained from
    # http://data.hud.gov/Housing_Counselor/searchByLocation?Lat=38.853231&Long=-77.305097&Distance=10
    #
    agcid = models.CharField(null=False, max_length=9)     # Counseling Agency ID, ex. "80999"
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
    agc_ADDR_LATITUDE = models.CharField(max_length=40)      # ex "39.658075",
    agc_ADDR_LONGITUDE = models.CharField(max_length=40)     # ex "-75.74669",
    languages = models.CharField(max_length=255)            # ex "ENG,SPA",
    # These can get really lengthy, and those agencies won't be installed as a result
    services = models.CharField(max_length=1500)             # ex "DFC,DFW,FBC,NDW,PPC,PPW",
    parentid = models.CharField(max_length=9)               # ex "81219",
    county_nme = models.CharField(max_length=255)           # ex "",
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

    def __str__(self):
        return self.nme


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
