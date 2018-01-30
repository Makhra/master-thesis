from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('stamps.views',
    url(r'^display/$', 'display'),
    url(r'^stamps/$', 'stamps_list'),
    url(r'^upload/$', 'upload'),
    url(r'^signup/$', 'signup'),
    url(r'^login/$', 'user_login'),
    url(r'^home/$', 'user_home'),
    url(r'^finder/$', 'match_finder'),
    url(r'^edit/$', 'user_edit'),
    url(r'^friends/$', 'user_friends'),
    url(r'^collection/$', 'user_collection'),
    url(r'^interest/$', 'trade_interest'),
    url(r'^user/$', 'user_page'),
    url(r'^transaction_review/$', 'transaction_review'),
    url(r'^transaction/$', 'transaction_display'),
    url(r'^messages/$', 'get_messages'),
    url(r'^mailbox/$', 'all_messages'),

    
#redirection url
    url(r'^logout/$', 'user_logout'),
    url(r'^interested/$', 'interested'),
    url(r'^accepted/$', 'interest_confirmed'),
    url(r'^naccepted/$', 'interest_canceled'),
    url(r'^done/$', 'transaction_confirmed'),
    url(r'^ndone/$', 'transaction_canceled'),
    url(r'^friendreq/$', 'request_confirmed'),
    url(r'^nfriendreq/$', 'request_canceled'),
    url(r'^delete/$', 'delete_collection'),
)
