from django.urls import re_path

from .views import dispatcher

urlpatterns = [re_path(r"^", dispatcher, name="beanstalk_dispatcher")]
