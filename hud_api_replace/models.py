from django.db import models

import datetime

# Create your models here.
class CounselingAgency( models.Model ):
    # example result can be obtained from
    # http://data.hud.gov/Housing_Counselor/searchByLocation?Lat=38.853231&Long=-77.305097&Distance=100
    #
    agcid = models.CharField( null = False, max_length = 9 )     # Counseling Agency ID, ex. "80961"
    adr1 = models.CharField( max_length = 255 )                 # ex "153 E. Chestnut Hill Road",
    adr2 = models.CharField( max_length = 255 )                 # ex "Robscott Building, Suite 102",
    city = models.CharField( max_length = 255 )                 # ex "NEWARK",
    email = models.CharField( max_length = 100 )                # ex "mwood@ywcade.org",
    fax = models.CharField( max_length = 20 )                   # ex "302-224-4057",
    nme = models.CharField( max_length = 255 )                  # ex "YWCA DELAWARE",
    phone1 = models.CharField( max_length = 20 )                # ex "302-224-4060-202",
    statecd = models.CharField( max_length = 2 )                # ex "DE",
    weburl = models.CharField( max_length = 255 )               # ex "http://www.ywcade.org",
    zipcd = models.CharField( max_length = 10 )                 # ex "19713-4046",
    agc_ADDR_LATITUDE = models.CharField( max_length = 40)      # ex "39.658075",
    agc_ADDR_LONGITUDE = models.CharField( max_length = 40)     # ex "-75.74669",
    languages = models.CharField( max_length = 255 )            # ex "ENG,SPA",
    # These can get really lengthy, and those agencies won't be installed as a result
    services = models.CharField( max_length = 1500 )             # ex "DFC,DFW,FBC,NDW,PPC,PPW",
    parentid = models.CharField( max_length = 9 )               # ex "81210",
    county_nme = models.CharField( max_length = 255 )           # ex "",
    phone2 = models.CharField( max_length = 20)                 # ex " ",
    mailingadr1 = models.CharField( max_length = 255 )          # ex "153 E. Chestnut Hill Road",
    mailingadr2 = models.CharField( max_length = 255 )          # ex "Robscott Building, Suite 102",
    mailingcity = models.CharField( max_length = 255 )          # ex "Newark",
    mailingzipcd = models.CharField( max_length = 10 )          # ex "19713",
    mailingstatecd = models.CharField( max_length = 2 )         # ex "DE",
    state_NME = models.CharField( max_length = 50 )             # ex "Delaware",
    state_FIPS_CODE = models.CharField( max_length = 255 )      # ex null,
    faithbased = models.BooleanField()                          # ex "Y",
    colonias_IND = models.BooleanField()                        # ex "N",
    migrantwkrs_IND = models.BooleanField()                     # ex "N",
    agc_STATUS = models.CharField( max_length = 255 )           # ex "C",
    agc_SRC_CD = models.CharField( max_length = 255 )           # ex "HUD",
    counslg_METHOD = models.CharField( max_length = 255 )       # ex null

    def __unicode__( self ):
        return self.nme

