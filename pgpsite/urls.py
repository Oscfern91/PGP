from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

admin.autodiscover()

urlpatterns = [

    # Admin URL
    url(r'^admin/', include(admin.site.urls), name='admin'),
    
    # Login/Logout URLs
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': '/accounts/login/'}, name='logout'),
    
    # Gtpros pages
    url(r'', include('gtpros.urls'), name='gtpros'),
    
]
