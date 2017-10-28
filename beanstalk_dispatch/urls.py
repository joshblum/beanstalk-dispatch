from django.conf.urls import url

from .views import dispatcher

urlpatterns = [
    url(r'^', dispatcher, name='beanstalk_dispatcher')
]
