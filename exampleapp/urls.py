from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


# Examples:
# url(r'^$', 'exampleapp.views.home', name='home'),
# url(r'^exampleapp/', include('exampleapp.foo.urls')),

# Uncomment the admin/doc line below to enable admin documentation:
# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

# Uncomment the next line to enable the admin:
# url(r'^admin/', include(admin.site.urls)),

urlpatterns = patterns(
    '',
    (r'^findfriend/', include('contactstore.urls')),
)
