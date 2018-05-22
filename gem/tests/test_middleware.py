from django.test import RequestFactory, TestCase
from django.test.client import Client

from gem.middleware import GemMoloGoogleAnalyticsMiddleware
from gem.models import GemSettings

from mock import patch

from molo.core.models import SiteSettings
from gem.tests.base import GemTestCaseMixin


class TestCustomGemMiddleware(TestCase, GemTestCaseMixin):

    submit_tracking_method = (
        "gem.middleware.GemMoloGoogleAnalyticsMiddleware.submit_tracking"
    )

    def setUp(self):
        self.main = self.mk_main(
            title='main1', slug='main1', path='00010002', url_path='/main1/')
        self.client = Client(HTTP_HOST=self.main.get_site().hostname)

        self.site_settings = SiteSettings.for_site(self.main.get_site())
        self.site_settings.local_ga_tracking_code = 'local_ga_tracking_code'
        self.site_settings.save()

        GemSettings.objects.create(
            site_id=self.main.get_site().id,
            bbm_ga_account_subdomain='bbm',
            bbm_ga_tracking_code='bbm_tracking_code',
        )

        self.response = self.client.get('/')

    @patch(submit_tracking_method)
    def test_submit_to_additional_ga_account(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL contains the
        bbm_ga_account_subdomain, info should be sent to
        the additional GA account.
        '''

        request = RequestFactory().get('/', HTTP_HOST='bbm.localhost')
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'bbm_tracking_code', request, self.response)

    @patch(submit_tracking_method)
    def test_submit_to_bbm_analytics_if_cookie_set(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the BBM cookie is set, info
        should be sent to the additional GA account.
        '''

        request = RequestFactory().get('/', HTTP_HOST='localhost')
        request.COOKIES['bbm'] = 'true'
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'bbm_tracking_code', request, self.response)

    @patch(submit_tracking_method)
    def test_submit_to_local_ga_account(self, mock_submit_tracking):
        '''
        Given that bbm_ga_account_subdomain and bbm_ga_tracking_code
        are set in Gem Settings, and the URL does not contain the
        bbm_ga_account_subdomain, info should be sent to
        the local GA account, not the additional GA account.
        '''

        request = RequestFactory().get('/', HTTP_HOST='localhost')
        request.site = self.main.get_site()

        middleware = GemMoloGoogleAnalyticsMiddleware()
        middleware.submit_to_local_account(
            request, self.response, self.site_settings)

        mock_submit_tracking.assert_called_once_with(
            'local_ga_tracking_code', request, self.response)
