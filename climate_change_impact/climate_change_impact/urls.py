"""climate_change_impact URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin
from Remote_User import views as remoteuser
from climate_change_impact import settings
from Service_Provider import views as serviceprovider
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', remoteuser.base, name="base"),

    
    path('login', remoteuser.login, name="login"),
    path('Register1/$', remoteuser.Register1, name="Register1"),
    path('Prediction_Of_Climate_Change_Impact/$', remoteuser.Prediction_Of_Climate_Change_Impact, name="Prediction_Of_Climate_Change_Impact"),
    path('ViewYourProfile/$', remoteuser.ViewYourProfile, name="ViewYourProfile"),
    path('userhome/', remoteuser.userhome, name="userhome"),

    path('serviceproviderlogin/$',serviceprovider.serviceproviderlogin, name="serviceproviderlogin"),
    path('iew_Remote_Users/$',serviceprovider.View_Remote_Users,name="View_Remote_Users"),
    path('charts/(?P<chart_type>\w+)', serviceprovider.charts,name="charts"),
    path('charts1/(?P<chart_type>\w+)', serviceprovider.charts1, name="charts1"),
    path('likeschart/(?P<like_chart>\w+)', serviceprovider.likeschart, name="likeschart"),
    path('Find_Prediction_Of_Climate_Change_Impact_Ratio/', serviceprovider.Prediction_Of_Climate_Change_Impact, name='Find_Prediction_Of_Climate_Change_Impact_Ratio'),
    path('train_model/$', serviceprovider.train_model, name="train_model"),
    path('View_Prediction_Of_Climate_Change_Impact/$', serviceprovider.View_Prediction_Of_Climate_Change_Impact, name="View_Prediction_Of_Climate_Change_Impact"),
    path('view_dataset/', serviceprovider.view_dataset, name="view_dataset"),
    path('model_performance/', serviceprovider.model_performance, name="model_performance"),
    path('adminhome/', serviceprovider.adminhome, name="adminhome"),
    path('approve_user/<int:id>/', serviceprovider.approve_user, name='approve_user'),
    path('delete_user/<int:id>/', serviceprovider.delete_user, name='delete_user'),

# optional toggle (recommended)
    path('toggle_user/<int:id>/', serviceprovider.toggle_user_status, name='toggle_user'),





]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
