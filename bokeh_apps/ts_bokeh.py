import os
import numpy as np
#from django.views.decorators.csrf import csrf_protect
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import django.contrib.staticfiles 
from django.views.decorators.clickjacking import xframe_options_exempt

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, Toolbar, Legend, LegendItem, Div
from bokeh.plotting import figure
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import column, row
from bokeh.models import Text, Arc, Line, ColumnDataSource, Slider, Select
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead
from bokeh.plotting import figure
from bokeh.embed import file_html, components
from bokeh.models import CustomJS, RangeSlider, ImageURL
from bokeh.models import BoxSelectTool, LassoSelectTool, BoxZoomTool
from bokeh.models import Ascii

import traimaocv.models.cours_ts as ts_crs
from bokeh.models import MathML
#import traimaocv.bokeh_apps.latex_bokeh as latex_bkh

#theme = Theme(filename=join(settings.THEMES_DIR, "theme.yaml"))

DIR_DFT = os.path.dirname(django.contrib.staticfiles.finders.find("favicon.ico"))
LATEX =r"""\documentclass[border=12pt,12pt,varwidth]{standalone}
\usepackage{amssymb,amsmath}
\usepackage[utf8]{inputenc}
\begin{document}
$$ equation $$
\end{document}
"""
EXT_DVI=".svg"

def latex_cercle_trigo(param):
    idx_file = str(int(param[0]*100))
    nom_fichier = "cercle_"+idx_file
    legende = LATEX.replace("equation",r"\boldsymbol{\theta = "+str(int(param[0]*100)/100)+"}")
    return legende, nom_fichier, idx_file

def latex_sinus_freq_phase(param):
    idx_file = str(int(param[0]*100)) + "_" + str(int(param[1]*100))
    nom_fichier = "sinus_"+idx_file
    legende = LATEX.replace("equation",r"\boldsymbol{sin(2\pi " + 
                            str(int(param[0]*100)/100) + "x - " +
                            str(int(param[1]*100)/100) + ")}" 
                            )
    return legende, nom_fichier, idx_file

def latex_url(param, fct_latex):
    os.chdir(DIR_DFT)
    legende, nom_fichier, idx_file = fct_latex(param)
    if os.path.isfile(nom_fichier+EXT_DVI):
        return "/static/"+nom_fichier+EXT_DVI
    fichier_ltx = open(os.path.join(DIR_DFT,nom_fichier+".tex"),"w",encoding="utf-8")
    fichier_ltx.write(legende)
    fichier_ltx.close()
    cmd = "latex --shell-escape --quiet -output-directory="+DIR_DFT +" "+nom_fichier+".tex"
    os.system(cmd)
    if EXT_DVI == ".png":
        cmd = "dvipng -bg Transparent -D 1200 "+ \
              os.path.join(DIR_DFT,nom_fichier + ".dvi") + \
              " -o "+ nom_fichier +EXT_DVI
    else:
        cmd = "dvisvgm  "+ \
              os.path.join(DIR_DFT,nom_fichier + ".dvi") + \
              " -o "+ nom_fichier +EXT_DVI
    os.system(cmd)
    os.remove(os.path.join(DIR_DFT, nom_fichier+".tex"))
    os.remove(os.path.join(DIR_DFT, nom_fichier+".aux"))
    os.remove(os.path.join(DIR_DFT, nom_fichier+".dvi"))
    os.remove(os.path.join(DIR_DFT, nom_fichier+".log"))
   
    return "/static/"+nom_fichier+EXT_DVI

def melange_sinus(freq, amp, Fe=11025,):
    t = np.arange(0, 2, 1 / Fe)
    y = np.zeros(shape=(t.shape[0],2),dtype=np.float32)
    y = amp[0] * np.sin(2 * np.pi * freq[0] * t)
    y += amp[1] * np.sin(2 * np.pi * freq[1] * t)
    y += amp[2] * np.sin(2 * np.pi * freq[2] * t)
    y = np.clip(y, -1, 1)
    return y, t

def trans_simil(a_simil=1, t0=0, fct='Porte'):
    t = np.arange(-10, 10, 0.01)
    if fct == 'Porte':
        y = ts_crs.porte(a_simil*(t-t0))
    elif fct == 'Triangle':
        y = ts_crs.triangle(a_simil*(t-t0))
    elif fct == 'Sinus':
        y = np.sin(a_simil*(t-t0))
    else:
        y = 0*t
    return y, t

@xframe_options_exempt
def trans_simil_bkh(request: HttpRequest) -> HttpResponse:
    liste_fct = ["Porte","Triangle","Sinus"]
    menu_fct = Select(title="Fonctions", value=liste_fct[0], options=liste_fct)
    a_simil=1
    t0=0
    fct = liste_fct[0]
    b_ok, val = ts_crs.get_arg_post(request, ['a', 't0', 'fct'])
    if b_ok:
        a_simil, t0, fct = float(val[0]), float(val[1]), val[2]
    # Génération d'une image à une fréquence spatiale donnée
    plot_original = figure(width=400,
                           height=200,
                           title="Original : porte(t)",
                           name="Mes_donnees_o")
    plot_simil = figure(width=400,
                        height=200,
                        title="porte(a(t-t0))",
                        name="Mes_donnees_s")
    Fe = 22050
    y, t = trans_simil(1,0)
    y_s, t = trans_simil(a_simil,t0)
    source_1 = ColumnDataSource(dict(x=t, y=y))
    source_2 = ColumnDataSource(dict(a_simil=[a_simil],t0=[t0]))
    source_3 = ColumnDataSource(dict(x=t,y=y_s))
    le_sinus = plot_original.line('x', 'y',
                                  source=source_1,
                                  line_width=3,
                                  line_alpha=0.6,
                                 )
    plot_original.xaxis.axis_label=r"$$t (s)$$"
    plot_original.yaxis.axis_label=r"$$u.a.$$"
    plot_simil.line('x' ,'y',
                       source=source_3,
                       line_width=3,
                       line_alpha=0.6)
    plot_simil.xaxis.axis_label=r"$$t (s)$$"
    plot_simil.yaxis.axis_label=r"$$u.a.$$"
    a_slider = Slider(start=-5., end=5, value=a_simil, step=0.1, title=r"Coefficient a",syncable=True)
    t0_slider = Slider(start=-10., end=10, value=t0, step=1, title="Coefficient t0",syncable=True)
    callback = CustomJS(args=dict(source1=source_1,
                                  source2=source_2,
                                  source3=source_3,
                                  coeff_a=a_slider,
                                  coeff_t0=t0_slider,
                                  menu_fct=menu_fct),
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
        
        xhr.open("POST", "/index/trans_simil_slider_change", true);
        xhr.setRequestHeader('mode', 'same-origin');
        var dataForm = new FormData();
        dataForm.append('csrfmiddlewaretoken', csrfToken);
        dataForm.append('a', coeff_a.value);
        dataForm.append('t0', coeff_t0.value);
        dataForm.append('fct', menu_fct.value);
        
        xhr.responseType = 'json';
        xhr.onload = function() {    
            reponse =  xhr.response
            const plot = Bokeh.documents[0].get_model_by_name('Mes_donnees')
            source1.data.x = reponse['s1_x'];
            source1.data.y = reponse['s1_y'];
            source2.data.a_simil = reponse['s2_a'];
            source2.data.t0 = reponse['s2_t0'];
            source3.data.x = reponse['s3_x'];
            source3.data.y = reponse['s3_y'];
            source1.change.emit();
            source2.change.emit();
            source3.change.emit();
            }
        xhr.send(dataForm);
        """)

    a_slider.js_on_change('value', callback)
    t0_slider.js_on_change('value', callback)
    menu_fct.js_on_change('value', callback)
    layout = column(menu_fct, a_slider, t0_slider,
                    plot_original, plot_simil)
    script1, div1  = components(layout, "Graphique")
    code_html = render(request,"TransSimil_bkh.html", dict(script1=script1, div=div1))
    return code_html

@xframe_options_exempt
def trans_simil_slider_change(request: HttpRequest) -> HttpResponse:
    a_simil=1
    t0=0
    fct = 'Porte'
    b_ok, val = ts_crs.get_arg_post(request, ['a', 't0', 'fct'])
    if b_ok:
        a_simil, t0, fct = float(val[0]), float(val[1]), val[2]
    Fe = 11025 
    y, t = trans_simil(1,0, fct)
    y_s, t = trans_simil(a_simil,t0, fct)
    return JsonResponse(dict(s1_x=t.tolist(),s1_y=y.tolist(),
                             s2_a_simil=a_simil, s2_t0=t0,
                             s3_x=t.tolist(), s3_y= y_s.tolist()))
    
    
def sinus_amorti(freq=220, tau=10, Fe=11025,):
    t = np.arange(0, 1, 1 / Fe)
    y = np.exp(-t * tau) * np.sin(2 * np.pi * freq * t)
    y = np.clip(y, -1, 1)
    S = np.fft.fft(y, axis=0)
    nu = np.fft.fftfreq(t.shape[0])*Fe
    return y, t, nu, np.abs(S)

@xframe_options_exempt
def sinus_amorti_bkh(request: HttpRequest) -> HttpResponse:
    freq= 220
    tau = 10
    b_ok, val = ts_crs.get_arg_post(request,
                                    ['freq','tau'])
    if b_ok:
        freq= float(val[0])
        tau= float(val[1])
    plot_time = figure(width=400,
                       height=200,
                       title="Sinus amorti(utiliser la loupe)",
                       name="Mes_donnees_t")
    plot_fft = figure(width=400,
                       height=200,
                       title="Module du spectre",
                       name="Mes_donnees_f")
    Fe = 22050
    y, t, nu, Y = sinus_amorti(freq, tau, Fe)
    source_1 = ColumnDataSource(dict(x=t, y=y))
    source_2 = ColumnDataSource(dict(freq=[freq],tau=[tau]))
    source_3 = ColumnDataSource(dict(nu=nu,Y=Y))
    le_sinus = plot_time.line('x', 'y',
                              source=source_1,
                              line_width=3,
                              line_alpha=0.6,
                              )
    plot_time.xaxis.axis_label=r"$$t (s)$$"
    plot_time.yaxis.axis_label=r"$$y$$"
    le_spectre = plot_fft.scatter('nu' ,'Y',
                               source=source_3,
                               name="Mon_spectre",
                               line_width=3,
                               line_alpha=0.6)
    plot_fft.xaxis.axis_label=r"$$\nu (Hz)$$"
    plot_fft.yaxis.axis_label=r"$$u.a.$$"
    texte1 = r"$$y(t) =\sin(2\pi f t)  \exp^{-at}$$"
    texte2 = r"$$Y(\nu)=\frac{2\pi f}{(a+i2\pi\nu)^2+(2\pi f)^2}$$"
    div1 = Div(width=400, height=50, background="#fafafa",
              text=texte1)
    div2 = Div(width=400, height=50, background="#fafafa",
              text=texte2)
              

    freq_slider = Slider(start=20., end=4000, value=freq, step=1, title=r"Fréquence f",syncable=True)
    tau_slider = Slider(start=0., end=10, value=tau, step=.1, title="Amortissement a",syncable=True)
    callback = CustomJS(args=dict(source1=source_1,
                                  source2=source_2,
                                  source3=source_3,
                                  freq=freq_slider,
                                  tau=tau_slider),
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
        
        xhr.open("POST", "/index/sinus_amorti_slider_change", true);
        xhr.setRequestHeader('mode', 'same-origin');
        var dataForm = new FormData();
        dataForm.append('csrfmiddlewaretoken', csrfToken);
        dataForm.append('freq', freq.value);
        dataForm.append('tau', tau.value);
        xhr.responseType = 'json';
        xhr.onload = function() {    
            reponse =  xhr.response
            const plot = Bokeh.documents[0].get_model_by_name('Mes_donnees')
            source1.data.x = reponse['s1_x'];
            source1.data.y = reponse['s1_y'];
            source3.data.nu = reponse['s3_nu'];
            source3.data.Y = reponse['s3_Y'];
            source2.data.freq = reponse['freq'];
            source2.data.tau = reponse['tau'];
            var audio_b64 = reponse['base64'];
            const aud = document.getElementById("audio_tag1")
            aud.src="data:audio/wav;base64,"+audio_b64
            source1.change.emit();
            source2.change.emit();
            source3.change.emit();
            }
        xhr.send(dataForm);
        """)

    freq_slider.js_on_change('value_throttled', callback)
    tau_slider.js_on_change('value_throttled', callback)
    layout = column(freq_slider, tau_slider,div1,
                    plot_time, div2, plot_fft)
    urs =  ts_crs.convert_npson_uri(y, Fe)
    script1, div1  = components(layout, "Graphique")
    code_html = render(request,"SinusAmorti_bkh.html", dict(script1=script1, div=div1,data_snd= urs))
    return code_html

@xframe_options_exempt
def sinus_amorti_slider_change(request: HttpRequest) -> HttpResponse:
    freq= 220
    tau = 10
    b_ok, val = ts_crs.get_arg_post(request,
                                    ['freq','tau'])
    if b_ok:
        freq= float(val[0])
        tau= float(val[1])
    Fe = 11025 
    y, t, nu, Y = sinus_amorti(freq, tau, Fe)
    urs =  ts_crs.convert_npson_uri(y, Fe)
    
    return JsonResponse(dict(s1_x=t.tolist(),s1_y=y.tolist(),
                             s2_freq=freq, s2_tau=tau,
                             s3_nu=nu.tolist(), s3_Y= Y.tolist(),                             
                             base64=urs))
    
@xframe_options_exempt
def sin_melange_bkh(request: HttpRequest) -> HttpResponse:
    freq=[220, 0, 0]
    amp = [1, 0, 0]
    b_ok, val = ts_crs.get_arg_post(request,
                                    ['f1','f2', 'f3', 'a1', 'a2', 'a3'])
    if b_ok:
        freq= [float(val[0]), float(val[1]), float(val[2])]
        amp= [float(val[3]), float(val[4]), float(val[5])]
    plot = figure(width=400,
                  height=400,
                  title="Mélange de sinus (utiliser la loupe)",
                  name="Mes_donnees")
    Fe = 11025 
    y, t = melange_sinus(freq, amp, Fe=11025)
    plot.xaxis.axis_label=r"$$t$$"
    plot.yaxis.axis_label=r"$$y$$"
    source_1 = ColumnDataSource(dict(x=t, y=y))
    source_2 = ColumnDataSource(dict(freq=freq,amp=amp))
    le_sinus = plot.line('x', 'y',
                         source=source_1,
                         line_width=3,
                         line_alpha=0.6,
                         name="Mon_sinus")
    
                

    freq1_slider = Slider(start=20., end=1000, value=freq[0], step=1, title="Fréquence 1",syncable=True)
    amp1_slider = Slider(start=0., end=1, value=amp[0], step=.05, title="Amplitude 1",syncable=True)
    freq2_slider = Slider(start=0., end=1000, value=freq[1], step=1, title="Fréquence 2",syncable=True)
    amp2_slider = Slider(start=0., end=1, value=amp[1], step=.05, title="Amplitude 2",syncable=True)
    freq3_slider = Slider(start=0., end=1000, value=freq[2], step=1, title="Fréquence 3",syncable=True)
    amp3_slider = Slider(start=0., end=1, value=amp[2], step=.05, title="Amplitude 3",syncable=True)
    callback = CustomJS(args=dict(source1=source_1,
                                  source2=source_2,
                                  f1=freq1_slider,
                                  a1=amp1_slider,
                                  f2=freq2_slider,
                                  a2=amp2_slider,
                                  f3=freq3_slider,
                                  a3=amp3_slider,
                                  ),
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
        
        xhr.open("POST", "/index/melange_slider_change", true);
        xhr.setRequestHeader('mode', 'same-origin');
        var dataForm = new FormData();
        dataForm.append('csrfmiddlewaretoken', csrfToken);
        dataForm.append('f1', f1.value);
        dataForm.append('f2', f2.value);
        dataForm.append('f3', f3.value);
        dataForm.append('a1', a1.value);
        dataForm.append('a2', a2.value);
        dataForm.append('a3', a3.value);
        xhr.responseType = 'json';
        xhr.onload = function() {    
            reponse =  xhr.response
            const plot = Bokeh.documents[0].get_model_by_name('Mes_donnees')
            source1.data.x = reponse['s1_x'];
            source1.data.y = reponse['s1_y'];
            source2.data.freq = reponse['freq'];
            source2.data.amp = reponse['amp'];
            var audio_b64 = reponse['base64'];
            const aud = document.getElementById("audio_tag1")
            aud.src="data:audio/wav;base64,"+audio_b64
            source1.change.emit();
            source2.change.emit();
            }
        xhr.send(dataForm);
        """)

    freq1_slider.js_on_change('value_throttled', callback)
    amp1_slider.js_on_change('value_throttled', callback)
    freq2_slider.js_on_change('value_throttled', callback)
    amp2_slider.js_on_change('value_throttled', callback)
    freq3_slider.js_on_change('value_throttled', callback)
    amp3_slider.js_on_change('value_throttled', callback)
    layout = column(freq1_slider, amp1_slider,
                    freq2_slider, amp2_slider,
                    freq3_slider, amp3_slider,
                    plot)
    urs =  ts_crs.convert_npson_uri(y, Fe)
    script1, div1  = components(layout, "Graphique")
    code_html = render(request,"melangeSinusMultiple_bkh.html", dict(script1=script1, div=div1,data_snd= urs))
    return code_html

@xframe_options_exempt
def melange_slider_change(request: HttpRequest) -> HttpResponse:
    freq=[220, 0, 0]
    amp = [1, 0, 0]
    b_ok, val = ts_crs.get_arg_post(request,
                                    ['f1','f2', 'f3', 'a1', 'a2', 'a3'])
    if b_ok:
        freq= [float(val[0]), float(val[1]), float(val[2])]
        amp= [float(val[3]), float(val[4]), float(val[5])]
    Fe = 11025 
    y, t = melange_sinus(freq, amp, Fe=Fe)
    urs =  ts_crs.convert_npson_uri(y, Fe)
    
    return JsonResponse(dict(s1_x=t.tolist(),s1_y=y.tolist(),
                             s2_x=freq, s2_y=amp, 
                             base64=urs))
 

@xframe_options_exempt
def cercle_trigo_bkh(request: HttpRequest) -> HttpResponse:
    theta = 1
    b_ok, val = ts_crs.get_arg_post(request, ['theta'])
    if b_ok:
        theta = float(val[0])
    outils = Toolbar(tools=[BoxSelectTool(), LassoSelectTool(),BoxZoomTool()])
    plot = figure(width=600,
                  height=600,
                  title="Cercle trigonométrique",
                  name="Mes_donnees",
                  match_aspect=True,
                  tools="wheel_zoom, reset, save")
     
    plot.circle(0, 0, radius=1,
                fill_color=None,
                line_color='OliveDrab',
                line_width=3,
                )
    plot.line([-1.5, 1.5], [0, 0],line_color='red',line_width=3)
    plot.line( [0, 0],[-1.5, 1.5],line_color='red',line_width=3)
    x = [0]
    y = [0]
    r = [0.5]
    url = latex_url([theta], latex_cercle_trigo)
    source_1 = ColumnDataSource(dict(x=x, y=y, r=r, theta=[theta]))
    source_2 = ColumnDataSource(dict(x=[0,np.cos(theta)], y=[0, np.sin(theta)]))
    source_3 = ColumnDataSource(dict(url=[url],x=[1.5*r[0]*np.cos(theta/2)], y=[1.5*r[0]*np.sin(theta/2)]))
    source_4 = ColumnDataSource(dict(x=[r[0]*np.cos(theta-0.09)], y=[r[0]*np.sin(theta-0.09)], theta=[theta]))
    secteur_arc = Arc(x="x", y="y", radius="r",
                      start_angle=0.0, end_angle="theta",
                      line_color="blue",
                      line_width=3,
                      direction ='anticlock'
                      )
    plot.scatter(source=source_4,x='x',y='y',marker='triangle',size=15,angle='theta')
    secteur_line = Line(x="x", y="y",
                        line_color="blue",
                        line_width=3
                        )
    secteur_text = Text(x="x", y="y",
                        text_color="blue",
                        text="texte"
                        )
                
    plot.add_glyph(source_1, secteur_arc)
    plot.add_glyph(source_2, secteur_line)
    #plot.add_glyph(source_3, secteur_text)
    image1 = ImageURL(url="url", x="x", y="y", w=0.45, h=0.1, anchor="left")
    plot.add_glyph(source_3, image1)

    theta_slider = Slider(start=0., end=np.pi*2, value=theta, step=.1, title="Theta")
    callback = CustomJS(args=dict(source1=source_1,
                                  source2=source_2,
                                  source3=source_3,
                                  source4=source_4,
                                  theta=theta_slider),
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
        
        xhr.open("POST", "/index/theta_slider_change", true);
        xhr.setRequestHeader('mode', 'same-origin');
        var dataForm = new FormData();
        dataForm.append('csrfmiddlewaretoken', csrfToken);
        dataForm.append('theta', theta.value);
        xhr.responseType = 'json';
        xhr.onload = function() {    
            reponse =  xhr.response
            const plot = Bokeh.documents[0].get_model_by_name('Mes_donnees')
            source1.data.x = reponse['s1_x'];
            source1.data.y = reponse['s1_y'];
            source1.data.r = reponse['s1_r'];
            source1.data.theta = reponse['s1_theta'];
            source2.data.x = reponse['s2_x'];
            source2.data.y = reponse['s2_y'];
            source3.data.x = reponse['s3_x'];
            source3.data.y = reponse['s3_y'];
            source3.data.url = reponse['s3_url'];
            source4.data.x = reponse['s4_x']
            source4.data.y = reponse['s4_y']
            source4.data.theta = reponse['s1_theta']
            source1.change.emit();
            source2.change.emit();
            source3.change.emit();
            source4.change.emit();
            }
        xhr.send(dataForm);
        """)

    theta_slider.js_on_change('value', callback)
    layout = column(theta_slider,plot)
    script1, div1  = components(layout, "Graphique")
    code_html = render(request,"cercle_trigo_bkh.html", dict(script1=script1, div=div1))
    return code_html

@xframe_options_exempt
def theta_slider_change(request: HttpRequest) -> HttpResponse:
    theta = 1
    b_ok, val = ts_crs.get_arg_post(request, ['theta'])
    if b_ok:
        theta = float(val[0])

    x = [0]
    y = [0]
    r = [0.5]
    url = latex_url([theta], latex_cercle_trigo)
    #source_1 = ColumnDataSource(dict(x=x, y=y, r=r, theta=[theta]))
    #source_2 = ColumnDataSource(dict(x=[0,np.cos(theta)], y=[0, np.sin(theta)]))
    return JsonResponse(dict(s1_x=x,s1_y=y,s1_r=r,s1_theta=[theta],
                             s2_x=[0,np.cos(theta)], s2_y=[0,np.sin(theta)],
                             s3_x=[1.5*r[0]*np.cos(theta/2)],s3_y=[1.5*r[0]*np.sin(theta/2)],
                             s4_x=[r[0]*np.cos(theta-0.09)],s4_y=[r[0]*np.sin(theta-0.09)],
                             s3_url=[url]))
    
@xframe_options_exempt
def freq_phase(request: HttpRequest) -> HttpResponse:
    freq = 1
    b_ok, val = ts_crs.get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])
    phase = 0
    b_ok, val = ts_crs.get_arg_post(request, ['phase'])
    if b_ok:
        phase = float(val[0])

    x = np.linspace(0, 10, 500)
    y = np.sin(np.pi*2*freq*x-phase)
    url = latex_url([freq, phase], latex_sinus_freq_phase)

    source_1 = ColumnDataSource(data=dict(x=x, y=y))
    #source_2 = ColumnDataSource(data=dict(x=x, y=y,url=[url]))

    plot = figure(y_range=(-1.5, 1.5), width=600, height=600,name="Mes_donnees")
    plot.xaxis.axis_label=r"$$t$$"
    plot.yaxis.axis_label=r"$$y$$"
    le_sinus = plot.line('x', 'y',
                         source=source_1,
                         line_width=3,
                         line_alpha=0.6,
                         name="Mon_sinus")
    legend = Legend(items=[LegendItem(label=r"sin(2.pi.f.t-phi)", renderers=[le_sinus], index=0)])
    plot.add_layout(legend)
    plot.add_tools(BoxSelectTool())
    freq_slider = Slider(start=0., end=10, value=freq, step=.1, title=r"f")
    phase_slider = Slider(start=0., end=2*np.pi, value=phase, step=.1, title="phi")
    callback = CustomJS(args=dict(source=source_1, freq=freq_slider, phase=phase_slider),
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
        dataForm.append('freq', freq.value);
        dataForm.append('phase', phase.value);
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

    freq_slider.js_on_change('value', callback)
    phase_slider.js_on_change('value', callback)
    layout = column(freq_slider, phase_slider,plot)
    script1, div1  = components(layout, "Graphique")
    code_html = render(request,"sinus_slider.html", dict(script1=script1, div=div1))
    return code_html

    
@xframe_options_exempt
def sinus_slider(request: HttpRequest) -> HttpResponse:
    freq = 1
    b_ok, val = ts_crs.get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])

    x = np.linspace(0, 10, 2000)
    y = np.sin(np.pi*2*freq*x-phase)
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
    code_html = render(request,"sinus_slider.html", dict(script1=script1, div=div1))
    return code_html

@xframe_options_exempt
def sinus_slider_change(request: HttpRequest) -> HttpResponse:
    freq = 1
    phase = 0
    b_ok, val = ts_crs.get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])
    b_ok, val = ts_crs.get_arg_post(request, ['phase'])
    if b_ok:
        phase = float(val[0])

    x = np.linspace(0, 10, 2000)
    y = np.sin(np.pi*2*freq*x-phase)
    return JsonResponse(dict(x=x.tolist(),y=y.tolist()))