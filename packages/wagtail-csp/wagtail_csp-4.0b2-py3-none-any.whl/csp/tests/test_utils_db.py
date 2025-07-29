import pytest
from wagtail.models import Site

from csp.models import ContentSecurityPolicySettings  # type: ignore
from csp.tests.test_utils import policy_eq
from csp.utils import build_policy

pytestmark = pytest.mark.django_db

# Cases when there is no CSP object present are already implicitly tested in test_utils.py


def test_full_csp_object() -> None:
    csp_object = ContentSecurityPolicySettings()
    test_site = Site.objects.get()
    csp_object.site = test_site

    csp_object.CSP_CONNECT_SRC = "A"
    csp_object.CSP_DEFAULT_SRC = "B"
    csp_object.CSP_FONT_SRC = "C"
    csp_object.CSP_FRAME_SRC = "D"
    csp_object.CSP_FRAME_ANCESTORS = "E"
    csp_object.CSP_IMG_SRC = "F"
    csp_object.CSP_MEDIA_SRC = "G"
    csp_object.CSP_OBJECT_SRC = "H"
    csp_object.CSP_SCRIPT_SRC = "I"
    csp_object.CSP_STYLE_SRC = "J"

    csp_object.save()

    policy = build_policy()
    policy_eq(
        "connect-src A; default-src B; font-src C; frame-ancestors E; frame-src D; img-src F; media-src G; object-src H; script-src I; style-src J",
        policy,
    )


def test_cps_object_set_one_field_default_wagtail() -> None:
    # ContentSecurityPolicySettings provides reasonable defaults for Wagtail.
    # If we only change one field, the rest should stick to those reasonable defaults.

    csp_object = ContentSecurityPolicySettings()
    test_site = Site.objects.get()
    csp_object.site = test_site

    csp_object.CSP_CONNECT_SRC = "A"
    csp_object.save()

    policy = build_policy()
    policy_eq(
        "connect-src A; default-src 'self' 'unsafe-inline'; font-src 'self'; frame-ancestors 'self'; "
        "frame-src 'self'; img-src 'self'; media-src 'self'; object-src 'self'; script-src 'self' "
        "'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        policy,
    )


def test_cps_object_set_all_fields_empty() -> None:
    csp_object = ContentSecurityPolicySettings()
    test_site = Site.objects.get()
    csp_object.site = test_site

    csp_object.CSP_CONNECT_SRC = ""
    csp_object.CSP_DEFAULT_SRC = ""
    csp_object.CSP_FONT_SRC = ""
    csp_object.CSP_FRAME_SRC = ""
    csp_object.CSP_FRAME_ANCESTORS = ""
    csp_object.CSP_IMG_SRC = ""
    csp_object.CSP_MEDIA_SRC = ""
    csp_object.CSP_OBJECT_SRC = ""
    csp_object.CSP_SCRIPT_SRC = ""
    csp_object.CSP_STYLE_SRC = ""

    csp_object.save()

    policy = build_policy()

    policy_eq(
        "connect-src; default-src; font-src; frame-ancestors; frame-src; img-src; media-src; object-src; script-src; style-src",
        policy,
    )
