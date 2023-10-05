from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('pagination/', views.InsertPageApiData.as_view()),
    # path('asyncio/', views.Asyncio.as_view()),
    path('key/', views.InsertPageApiKeyData().as_view()),
    path('get/', views.Getdata().as_view(), name='data'),
    path('insert/', views.InsertData.as_view())
]