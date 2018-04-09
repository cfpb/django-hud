import time

from django.test import TestCase

from hud_api_replace.models import CachedGeodata
from hud_api_replace.views import get_counsel_list


class GetCounselListTests(TestCase):
    def setUp(self):
        CachedGeodata.objects.create(
            key='20006',
            lat=38.898609,
            lon=-77.041461,
            expires=time.time() + 24 * 3600
        )

    def test_no_results_returns_empty_list(self):
        results = get_counsel_list(zipcode='20006', GET={})
        self.assertEqual(results['counseling_agencies'], [])
