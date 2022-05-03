import os
import numpy as np
from django.views.decorators.csrf import csrf_protect
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import django.contrib.staticfiles 
from django.views.decorators.clickjacking import xframe_options_exempt

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider, Toolbar
from bokeh.plotting import figure
from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import column, row
from bokeh.models import Text, Arc, Line, ColumnDataSource, Slider
from bokeh.models import Arrow, OpenHead, NormalHead, VeeHead
from bokeh.plotting import figure
from bokeh.embed import file_html, components
from bokeh.models import CustomJS, RangeSlider, ImageURL
from bokeh.models import BoxSelectTool, LassoSelectTool, BoxZoomTool

import traimaocv.models.cours_ts as ts_crs
from bokeh.models import MathML
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


@xframe_options_exempt
def latex_url(theta):
    
    os.chdir(DIR_DFT)
    idx_file = str(int(theta*100))
    nom_fichier = "equation"+idx_file
    if os.path.isfile(nom_fichier+EXT_DVI):
        return "/static/equation"+idx_file+EXT_DVI
    legende = LATEX.replace("equation",r"\boldsymbol{\theta = "+str(int(theta*100)/100)+"}")
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
   
    return "/static/equation"+idx_file+EXT_DVI

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
    source_1 = ColumnDataSource(dict(x=x, y=y, r=r, theta=[theta]))
    source_2 = ColumnDataSource(dict(x=[0,np.cos(theta)], y=[0, np.sin(theta)]))
    url = latex_url(theta)
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
    layout = row(plot,theta_slider)
    script1, div1  = components(layout, "Graphique")
    code_html = render(request,"cercle_trigo_bkh.html", dict(script1=script1, div=div1))
    return code_html

@csrf_protect
def theta_slider_change(request: HttpRequest) -> HttpResponse:
    theta = 1
    b_ok, val = ts_crs.get_arg_post(request, ['theta'])
    if b_ok:
        theta = float(val[0])

    x = [0]
    y = [0]
    r = [0.5]
    url = latex_url(theta)
    #source_1 = ColumnDataSource(dict(x=x, y=y, r=r, theta=[theta]))
    #source_2 = ColumnDataSource(dict(x=[0,np.cos(theta)], y=[0, np.sin(theta)]))
    return JsonResponse(dict(s1_x=x,s1_y=y,s1_r=r,s1_theta=[theta],
                             s2_x=[0,np.cos(theta)], s2_y=[0,np.sin(theta)],
                             s3_x=[1.5*r[0]*np.cos(theta/2)],s3_y=[1.5*r[0]*np.sin(theta/2)],
                             s4_x=[r[0]*np.cos(theta-0.09)],s4_y=[r[0]*np.sin(theta-0.09)],
                             s3_url=[url]))
    
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
    y = np.sin(np.pi*2*freq*x+phase)
    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = figure(y_range=(-1.5, 1.5), width=600, height=600,title="Ma Courbe",name="Mes_donnees")

    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6,name="Mon_sinus")
    plot.add_tools(BoxSelectTool())
    freq_slider = Slider(start=0., end=10, value=freq, step=.1, title="Frequence")
    phase_slider = Slider(start=0., end=2*np.pi, value=phase, step=.1, title="Phase")
    callback = CustomJS(args=dict(source=source, freq=freq_slider, phase=phase_slider),
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
    layout = row(plot, column(freq_slider, phase_slider))
    script1, div1  = components(layout, "Graphique")
    code_html = render(request,"sinus_slider.html", dict(script1=script1, div=div1))
    return code_html

    
@csrf_protect
def sinus_slider(request: HttpRequest) -> HttpResponse:
    freq = 1
    b_ok, val = ts_crs.get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])

    x = np.linspace(0, 10, 500)
    y = np.sin(np.pi*2*freq*x+phase)
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

@csrf_protect
def sinus_slider_change(request: HttpRequest) -> HttpResponse:
    freq = 1
    phase = 0
    b_ok, val = ts_crs.get_arg_post(request, ['freq'])
    if b_ok:
        freq = float(val[0])
    b_ok, val = ts_crs.get_arg_post(request, ['phase'])
    if b_ok:
        phase = float(val[0])

    x = np.linspace(0, 10, 500)
    y = np.sin(freq*x+phase)
    return JsonResponse(dict(x=x.tolist(),y=y.tolist()))