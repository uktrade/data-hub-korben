from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'ch', views.CHCompanyViewSet)
router.register(r'company', views.CompanyViewSet)

urlpatterns = [
    url(r'^search$', views.search),
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
]
