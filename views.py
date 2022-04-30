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
from django.http import JsonResponse
from .models import cours_ts as cts

from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.themes import Theme
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from bokeh.models import CustomJS, RangeSlider

from .models import shape_viewer

def index(request):
    return render(request,'index.html')

@xframe_options_exempt
def frequence(request):
    a = cts.Frequence(request)()
    return render(request, a[0], a[1])

@xframe_options_exempt
def cercle_trigo(request):
    a = cts.CercleTrigo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt    
def exo_trans_simil(request):
    a = cts.TransSimil(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def freq_spatiale_2d(request):
    a = cts.FreqSpatiale2d(request)()
    return render(request,a[0], a[1])
    
@xframe_options_exempt
def melange_sinus(request):
    a = cts.MelangeSinus(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def simul_sf(request):
    a = cts.SimulSF(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def tf_chirp_lin(request):
    a = cts.TFChirpLin(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def tf_signal_amorti(request):
    a = cts.TFSignalAmorti(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def fonda_harmo(request):
    a = cts.FondaHarmo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def fonda_harmo_amorti(request):
    a = cts.FondaHarmoAmorti(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def echantillonnage_ex1(request):
    a = cts.EchantillonnageEx1(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def echantillonnage_ex2(request):
    a = cts.EchantillonnageEx2(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def echantillonnage_ex3(request):
    a = cts.EchantillonnageEx3(request)()
    print (a[0])
    return render(request,a[0], a[1])

@xframe_options_exempt
def can_exo(request):
    a = cts.CANExo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def cna_exo(request):
    a = cts.CNAExo(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def convol_exo1(request):
    a = cts.ConvolExo1(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def convol_exo2(request):
    a = cts.ConvolExo2(request)()
    return render(request,a[0], a[1])

@xframe_options_exempt
def intercorr_exo1(request):
    a = cts.IntercorrExo1(request)()
    return render(request,a[0], a[1])

    
theme = Theme(filename=join(settings.THEMES_DIR, "theme.yaml"))


def with_request(f):
    def wrapper(doc):
        return f(doc, doc.session_context.request)
    return wrapper



def sinus_bokeh(request: HttpRequest) -> HttpResponse:
    plot = figure()
    slider = Slider(start=0, end=10, step=.1, value=1, title="Stuff")
    slider.js_on_change("value", CustomJS(code="""
    console.log('slider: value=' + this.value, this.toString())
    """))
    x = np.arange(0,3*np.pi,0.5)
    plot.circle(x, np.sin(x))

    html1 = file_html(plot, CDN, "my plot")
    html2 = file_html(slider, CDN, "my plot")
    return render(request, "embed.html", dict(script1=html1,script2=html2))


def get_arg_post(request, list_var):
    """
    Récupération des données POST dans une requète
    request --> objet HTTPrequest
    list-var --> liste des variables à extraire de la requête
    valeur retour --> booléen et liste des valeurs
    booléen False si les valeurs n'ont pas été trouvées
    """
    resultat = []
    if len(request.POST) > 0:
        for v in list_var:  
            if v in request.POST:
                try:   
                    resultat.append(request.POST[v])
                except:
                    return False, []
            else:
                return False, []
    else:
        return False, []
    return True, resultat

nb_call = 0  
@csrf_protect
def sinus_slider(request: HttpRequest) -> HttpResponse:
    freq = 1
    global nb_call
    b_ok, val = get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])

    x = np.linspace(0, 10, 500)
    y = np.sin(freq*x)+freq
    print("Frequence slider= ",freq)
    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = figure(y_range=(-10, 10), width=400, height=400,title="Ma Courbe"+str(nb_call),name="Mes_donnees")

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
    if nb_call%2==0:
        layout = row(plot, column(amp_slider))
    else:
        layout = row(column(amp_slider),plot)
    script1, div1  = components(layout, "Graphique")
    pos = div1.find('data-root-id="')
    id = int(div1[pos+14:pos+18])
    print(div1, id)
    layout.update()
    #script2, div2  = components(amp_slider, "slider freq")
    #html2 = file_html(layout, CDN, "my plot")
    #html2 = html2.replace("</head>","{% csrf_token %}</head>")
    code_html = render(request,"sinus_slider.html", dict(script1=script1, div=div1))
    nb_call = nb_call + 1
    return code_html

@csrf_protect
def sinus_slider_change(request: HttpRequest) -> HttpResponse:
    freq = 1
    b_ok, val = get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])

    x = np.linspace(0, 10, 500)
    y = np.sin(freq*x)+freq
    print("Frequence sinus_slider_change= ",freq)
    source = base64.b64encode(x)
    
    return JsonResponse(dict(x=x.tolist(),y=y.tolist()))