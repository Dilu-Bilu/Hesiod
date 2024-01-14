from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from detector.views import TextInputView, FeedbackCreateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from assignment.views import (
    AssignmentListView,
    AssignmentCreateView,
    AssignmentDetailView,
    PriceView,
)

from killgpt.users.views import (
    step_one_signup_teacher,
    step_one_signup_student, 
    step_two_signup,
    subscription_confirm,
    profile_view,
)
class HomeSitemap(Sitemap):
    def items(self):
        return ['home']

    def location(self, item):
        return reverse(item)
sitemaps = {
    'home': HomeSitemap,
}


urlpatterns = [
    path(
        "landing", TemplateView.as_view(template_name="pages/landing.html"), name="landing"
    ),

    path(
        "step2.5", TemplateView.as_view(template_name="steps/twoplan.html"), name="step-2.5"
    ),
    path("subscription-confirm/", subscription_confirm, name="subscription_confirm"),
    path("profile/", profile_view, name="profile"),
    path(
        "step1", step_two_signup, name="step-1"
    ),
    path(
        "step2", TemplateView.as_view(template_name="steps/two.html"), name="step-2"
    ),
    path(
        "step3", PriceView, name="step-3"
    ),
    path(
        "entrance", TemplateView.as_view(template_name="pages/entrance.html"), name="entrance"
    ),
    path(
        "student-info", step_one_signup_student, name="student"
    ),
    path(
        "teacher-info", step_one_signup_teacher, name="teacher"
    ),
    path(
        "", TemplateView.as_view(template_name="pages/landing_real.html"), name="landing2"
    ),
    path(
        "assignment", AssignmentListView.as_view(), name="assignment-list"
    ),
    path("assignment/new/", AssignmentCreateView.as_view(), name="assignment-create"),
    path("detector/", TextInputView, name="home"),
    # path("AI/", TextInputView, name='AI'),
    path(
        "assignment/<int:pk>/",
        AssignmentDetailView.as_view(),
        name="assignment-detail",
    ),
    path(
        "tos/", TemplateView.as_view(template_name="pages/terms.html"), name="terms"
    ),
    path(
        "contact/", TemplateView.as_view(template_name="pages/contact.html"), name="contact"
    ),
    path(
        "pp/", TemplateView.as_view(template_name="pages/privacy.html"), name="pp"
    ),
    path(
        "about/", FeedbackCreateView.as_view(), name="about"
    ),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("robots.txt",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("killgpt.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path('api-auth/', include('rest_framework.urls')),
    # path('detect/', include(detector_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
