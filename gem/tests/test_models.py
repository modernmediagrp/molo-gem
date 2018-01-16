# coding=utf-8
import pytest
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings

from wagtail.wagtailcore.models import Site

from molo.core.models import (
    SiteLanguageRelation, Main, Languages, SiteSettings)
from molo.core.tests.base import MoloTestCaseMixin
from molo.surveys.models import (
    MoloSurveyPage, MoloSurveyFormField, SurveysIndexPage)
from gem.models import GemSettings


@pytest.mark.django_db
class TestModels(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)
        self.survey_index = SurveysIndexPage.objects.first()
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.yourmind_sub = self.mk_section(
            self.yourmind, title='Your mind subsection')
        self.site_settings = SiteSettings.for_site(self.main.get_site())
        self.site_settings.enable_tag_navigation = True
        self.site_settings.save()

    def test_partner_credit(self):
        response = self.client.get('/')
        self.assertNotContains(response, 'Thank You')
        self.assertNotContains(response, 'https://www.google.co.za/')

        default_site = Site.objects.get(is_default_site=True)
        setting = GemSettings.for_site(default_site)
        setting.show_partner_credit = True
        setting.partner_credit_description = "Thank You"
        setting.partner_credit_link = "https://www.google.co.za/"
        setting.save()

        response = self.client.get('/')
        self.assertContains(response, 'Thank You')
        self.assertContains(response, 'https://www.google.co.za/')

    def test_show_join_banner(self):
        from os.path import join
        temp_dir = [
            {
                'DIRS': [join(
                    settings.PROJECT_ROOT, 'gem', 'templates',
                    'springster'), ],
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                        'molo.core.context_processors.locale',
                        'wagtail.contrib.settings.context_processors.settings',
                        'gem.context_processors.default_forms',
                        'gem.processors.compress_settings',
                    ],
                    "loaders": [
                        "django.template.loaders.filesystem.Loader",
                        "mote.loaders.app_directories.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ]
                }, }]
        with self.settings(TEMPLATES=temp_dir):
            molo_survey_page = MoloSurveyPage(
                title='survey title',
                slug='survey-slug',
                intro='Introduction to Test Survey ...',
                thank_you_text='Thank you for taking the Test Survey',
            )

            self.survey_index.add_child(instance=molo_survey_page)
            MoloSurveyFormField.objects.create(
                page=molo_survey_page,
                sort_order=1,
                label='Your favourite animal',
                field_type='singleline',
                required=True
            )
            response = self.client.get('%s?next=%s' % (
                reverse('molo.profiles:auth_logout'),
                reverse('molo.profiles:user_register')))
            response = self.client.get('/')
            self.assertNotContains(response, 'profiles-join-banner')
            setting = GemSettings.for_site(self.main.get_site())
            setting.show_join_banner = True
            setting.save()

            response = self.client.get('/')
            self.assertContains(response, 'profiles-join-banner')
