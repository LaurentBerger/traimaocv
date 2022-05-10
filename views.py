# Create your views here.
from os.path import join
import numpy as np

from typing import Any
from django.conf import settings

from django.shortcuts import render
import io
import urllib, base64
from django.http import HttpRequest, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_protect


import traimaocv.bokeh_apps.ts_bokeh as ts_bkh
import traimaocv.models.cours_ts as ts_crs

def index(request):
    return render(request,'index.html')

@xframe_options_exempt
def frequence(request):
    a = ts_crs.Frequence(request)()
    return render(request, a[0], a[1])

@xframe_options_exempt
def cercle_trigo(request):
    a = ts_crs.CercleTrigo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def cercle_trigo_bkh(request):
    a = ts_bkh.CercleTrigoBkh(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt    
def trans_simil_bkh(request):
    a = ts_bkh.TransSimilBkh(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt    
def melange_sinus_bkh(request):
    a = ts_bkh.MelangeSinusBkh(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt    
def sinus_amorti_bkh(request):
    a = ts_bkh.SinusAmortiBkh(request)()
    return render(request,a[0], a[1])
    
    
@xframe_options_exempt    
def exo_trans_simil(request):
    a = ts_crs.TransSimil(request)()
    return render(request,a[0], a[1])


@xframe_options_exempt
def freq_spatiale_2d(request):
    a = ts_crs.FreqSpatiale2d(request)()
    return render(request,a[0], a[1])
    
@xframe_options_exempt
def melange_sinus(request):
    a = ts_crs.MelangeSinus(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def simul_sf(request):
    a = ts_crs.SimulSF(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def tf_chirp_lin(request):
    a = ts_crs.TFChirpLin(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def tf_signal_amorti(request):
    a = ts_crs.TFSignalAmorti(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def fonda_harmo(request):
    a = ts_crs.FondaHarmo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def fonda_harmo_amorti(request):
    a = ts_crs.FondaHarmoAmorti(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def echantillonnage_ex1(request):
    a = ts_crs.EchantillonnageEx1(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def echantillonnage_ex2(request):
    a = ts_crs.EchantillonnageEx2(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def echantillonnage_ex3(request):
    a = ts_crs.EchantillonnageEx3(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def can_exo(request):
    a = ts_crs.CANExo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def cna_exo(request):
    a = ts_crs.CNAExo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def convol_exo1(request):
    a = ts_crs.ConvolExo1(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def convol_exo2(request):
    a = ts_crs.ConvolExo2(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def intercorr_exo1(request):
    a = ts_crs.IntercorrExo1(request)()
    return render(request,a[0], a[1])

    



@csrf_protect
def sinus_slider(request: HttpRequest) -> HttpResponse:
    freq = 1
    b_ok, val = cts.get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])

    x = np.linspace(0, 10, 500)
    y = np.sin(freq*x)+freq
    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = figure(y_range=(-10, 10), width=400, height=400,title="Ma Courbe",name="Mes_donnees")

    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6,name="Mon_sinus")

    amp_slider = Slider(start=0.1, end=10, value=freq, step=.1, title="Amplitude")
    callback = CustomJS(args=dict(source=source, amp=amp_slider),
                        code="""
        var csrfToken = '';
        var i=0;
        var inputElems = document.querySelectorAll('input');
        var reponse='';
        for (i = 0; i < inputElems.length; ++i) {
            if (inputElems[i].name === 'csrfmiddlewaretoken') {
                csrfToken = inputElems[i].value;
                break;
                }
            }
        var xhr = new XMLHttpRequest();
        
        xhr.open("POST", "/index/slider_change", true);
        xhr.setRequestHeader('mode', 'same-origin');
        var dataForm = new FormData();
        dataForm.append('csrfmiddlewaretoken', csrfToken);
        dataForm.append('freq', amp.value);
        xhr.responseType = 'json';
        xhr.onload = function() {    
            reponse =  xhr.response
            source.data.x = reponse['x'];
            source.data.y = reponse['y'];
            const plot = Bokeh.documents[0].get_model_by_name('Mes_donnees')
            source.change.emit();
            }
        xhr.send(dataForm);
        """)

    amp_slider.js_on_change('value', callback)
    layout = row(plot, column(amp_slider))
    script1, div1  = components(layout, "Graphique")
    pos = div1.find('data-root-id="')
    id = int(div1[pos+14:pos+18])
    code_html = render(request,"sinus_slider.html", dict(script1=script1, div=div1))
    return code_html

@csrf_protect
def sinus_slider_change(request: HttpRequest) -> HttpResponse:
    freq = 1
    b_ok, val = get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])

    x = np.linspace(0, 10, 500)
    y = np.sin(freq*x)+freq
    source = base64.b64encode(x)
    
    return JsonResponse(dict(x=x.tolist(),y=y.tolist()))