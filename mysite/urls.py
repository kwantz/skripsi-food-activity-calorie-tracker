"""mysite URL Configuration

The `urlpatterns` list routes URLs to temp. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function temp
    1. Add an import:  from my_app import temp
    2. Add a URL to urlpatterns:  path('', temp.home, name='home')
Class-based temp
    1. Add an import:  from other_app.temp import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fact/', include('fact.urls'))
]
