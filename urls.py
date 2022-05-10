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
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import bokeh
from bokeh.server.django import autoload, directory, document, static_extensions

import traimaocv.bokeh_apps.ts_bokeh as ts_bkh
from . import views

bokeh_app_config = apps.get_app_config('bokeh_server_django')
print("bokeh_app_config=", bokeh_app_config)

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
    path("index/freq_phase", views.freq_phase),
    path("index/freq_phase_slider_change", ts_bkh.SinusFreqPhaseBkh.freq_phase_slider_change),
    path("index/cercle_trigo_bkh", views.cercle_trigo_bkh),
    path("index/theta_slider_change", ts_bkh.CercleTrigoBkh.theta_slider_change),
    path('index/melange_sinus_bkh', views.melange_sinus_bkh,name="melange_sinus"),
    path('index/melange_slider_change', ts_bkh.MelangeSinusBkh.melange_slider_change,name="melange_slider_change"),
    path('index/sinus_amorti_bkh', views.sinus_amorti_bkh,name="sinus_amorti_bkh"),
    path('index/sinus_amorti_slider_change', ts_bkh.SinusAmortiBkh.sinus_amorti_slider_change,name="sinus_amorti_slider_change"),
    path('index/trans_simil_bkh', views.trans_simil_bkh,name="trans_simil_bkh"),
    path('index/trans_simil_slider_change', ts_bkh.TransSimilBkh.trans_simil_slider_change,name="trans_simil_slider_change"),
    path('index/sinus3d', views.sinus_3d,name="trans_simil_slider_change"),
    path('favicon.ico',RedirectView.as_view(url='/static/favicon.ico')),
]
base_path = settings.BASE_PATH

print("base_path=", base_path)

bokeh_apps = [
    #autoload("index/sea_surface", views.sea_surface_handler),
    #document("/bokeh_apps/sea_surface", base_path / "traimaocv" / "bokeh_apps" / "sea_surface.py"),
    #document("shape_viewer", views.shape_viewer_handler),
]

apps_path = base_path / "traimaocv" /  "bokeh_apps" 
bokeh_apps += directory(apps_path)
print("bokeh_apps=", bokeh_apps)

urlpatterns += static_extensions()
urlpatterns += staticfiles_urlpatterns()


