"""exemple_ts URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/index'),name="index"),
    path('index/frequence', views.frequence,name="frequence"),
    path('index/cercle_trigo', views.cercle_trigo,name="cercle_trigo"),
    path('index/freq_spatiale_2d', views.freq_spatiale_2d,name="freq_spatiale_2d"),
    path('index/melange_sinus', views.melange_sinus,name="melange_sinus"),
    path('index/exo_trans_simil', views.exo_trans_simil,name="exo_trans_simil"),
    path('index/simul_sf', views.simul_sf,name="simul_sf"),
    path('index/tf_signal_amorti', views.tf_signal_amorti,name="tf_signal_amorti"),
    path('index/tf_chirp_lin', views.tf_chirp_lin,name="tf_chirp_lin"),
    path('index/fonda_harmo', views.fonda_harmo,name="fonda_harmo"),
    path('index/fonda_harmo_amorti', views.fonda_harmo_amorti,name="fonda_harmo_amorti"),
    path('index/echantillonnage_ex1', views.echantillonnage_ex1,name="echantillonnage_ex1"),
    path('index/echantillonnage_ex2', views.echantillonnage_ex2,name="echantillonnage_ex2"),
    path('index/echantillonnage_ex3', views.echantillonnage_ex3,name="echantillonnage_ex3"),
    path('index/can_exo', views.can_exo,name="can_exo"),
    path('index/cna_exo', views.cna_exo,name="cna_exo"),
    path('index/convol_exo1', views.convol_exo1,name="convol_exo1"),
    path('index/convol_exo2', views.convol_exo2,name="convol_exo2"),
    path('index/intercorr_exo1', views.intercorr_exo1,name="intercorr_exo1"),
    path('index/', views.index,name="index"),
    path('favicon.ico',RedirectView.as_view(url='/static/favicon.ico')),
]
