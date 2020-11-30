# Create your views here.
from django.shortcuts import render
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d.axes3d import get_test_data
import io
import urllib, base64
from django.http import HttpResponse
from scipy.io.wavfile import write
from django.views.decorators.clickjacking import xframe_options_exempt



def index(request):
    return render(request,'index.html')

@xframe_options_exempt
def frequence(request):
    print("Frequence ********* ", request.POST)
    freq = 1
    phase = 0
    if len(request.POST) > 0:
        if 'freq' in request.POST:
            try:
            
                freq = float(request.POST['freq'])
            except:
                freq = 1
        if 'phase' in request.POST:
            try:
            
                phase = float(request.POST['phase'])
            except:
                phase = 0
                
    fig, ax = plt.subplots(nrows=1, ncols=1)
    x = np.arange(0, 10, 0.01)
    txt_latex = '$sin(2\pi'+str(freq)+'t - '+str(phase) + ' )$'
    ax.plot(x ,np.sin( 2 * np.pi * freq * x - phase),label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='Sinus')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    plt.close(fig)
    return render(request,'frequence.html',{'data':uri, 'freq':freq, 'phase':phase})

@xframe_options_exempt
def cercle_trigo(request):
    if len(request.POST) > 0:
        if 'angle' in request.POST:
            try:
                a = float(request.POST['angle'])
            except:
                a = 1
    else:
        a = 1
    theta = np.arange(0, 2 * np.pi, 0.01)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    z = np.exp(1j * theta)
    ax.plot(np.real(z), np.imag(z), color='b')
    ax.plot([0, np.cos(a)],[0, np.sin(a)], color='g') 
    ax.plot([0, 1],[0, 0], color='g') 
    theta = np.arange(0, a, np.sign(a) * 0.01)
    z = np.exp(1j * theta)
    ax.plot(np.real(z/2), np.imag(z/2), color='r')
    ax.text(0.6 * np.cos(a/2), 0.6 * np.sin(a/2), r'$\theta = '+ str(a) + '$')
    ax.grid(True)
    plt.show()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    plt.close(fig)
    return render(request,'cercle_trigo.html',{'data':uri, 'angle':a})

def porte(t):
    ind = np.where(np.logical_or(t<-1/2, t>1/2))
    y = np.ones(shape=(t.shape[0], ), dtype = np.float32)
    y[ind]=0
    return y

@xframe_options_exempt    
def exo_trans_simil(request):
    print("exo_trans_simil -> ", request, ' -> ', request.POST)
    var_list = ['a', 't0']
    a_simil, t0 = 1, 0
    if len(request.POST) > 0:
        if all(x  in request.POST for x in var_list):
            print("POST")
            try:
                a_simil = float(request.POST['a'])
                t0 = float(request.POST['t0'])
            except:
                a_simil, t0 = 1, 0
                print("Exception")
    else:
        print("POST VIDE")
    # Génération d'une image à une fréquence spatiale donnée
    fig, ax = plt.subplots(nrows=1, ncols=1)
    t = np.arange(-10, 10, 0.01)
    y = porte(t)
    txt_latex = 'Signal original'
    ax.plot(t , y, label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='f(t)')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf1 = io.BytesIO()
    fig.savefig(buf1,format='png')
    buf1.seek(0)
    string = base64.b64encode(buf1.read())
    uri1 =  urllib.parse.quote(string)
    plt.close(fig)
    y = porte(a_simil * (t-t0))
    fig, ax = plt.subplots(nrows=1, ncols=1)
    txt_latex = 'Signal f('+ str(a_simil) + '(t-('  + str(t0) + ')))'
    ax.plot(t , y, label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='Orignal')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri2 =  urllib.parse.quote(string)
  
    plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
    return render(request,'exoTranslationSimiltude.html',{'data1':uri1, 'data2':uri2, 'a_simil':a_simil, 't0':t0})

@xframe_options_exempt
def freq_spatiale_2d(request):
    if len(request.POST) > 0:
        if 'nu' in request.POST:
            try:
                nu = float(request.POST['nu'])
            except:
                nu = 0.01
    else:
        nu = 0.01
    fig, ax = plt.subplots(nrows=1, ncols=1)
    # Génération d'une image à une fréquence spatiale donnée
    xc, yc  = 150, 150
    x = np.arange(0, 2 * xc, 2) # Largeur en pixel de l'image
    y = np.arange(0, 2 * yc, 2)
    x2d, y2d = np.meshgrid(x, y)
    z = 32+31*np.sin(2 * np.pi * nu * ((x2d - xc) ** 2+(y2d - yc) ** 2) ** (0.5))
    im = ax.imshow(z, cmap=cm.coolwarm, origin='lower', extent=[0, 2 * xc , 0 , 2 * yc],
               vmax=abs(z).max(), vmin=-abs(z).max())

    s = r'$ 32+31\sin{2\pi '+str(nu)+r'\sqrt{(x-150)^2+(y-150)^2 }}$'

    ax.set(title=s, xlabel=' x (m)', ylabel='y (m)')
    plt.show()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf1 = io.BytesIO()
    fig.savefig(buf1,format='png')
    buf1.seek(0)
    string = base64.b64encode(buf1.read())
    uri1 =  urllib.parse.quote(string)
    plt.close(fig)
    fig = plt.figure(figsize=plt.figaspect(1))
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    surf = ax.plot_surface(x2d, y2d, z, rstride=1, cstride=1, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)
    ax.set(title=s, xlabel=' x (m)', ylabel='y (m)')  
    plt.show()   
    buf2 = io.BytesIO()
    fig.savefig(buf2,format='png')
    buf2.seek(0)
    string = base64.b64encode(buf2.read())
    uri2 =  urllib.parse.quote(string)    
    return render(request,'freqSpatiale2d.html',{'data1':uri1, 'data2':uri2, 'nu':nu})
    
@xframe_options_exempt
def melange_sinus(request):
    var_list = ['A1', 'f1', 'A2', 'f2', 'A3', 'f3']
    a1, f1 = 1, 220
    a2, f2 = 0, 0
    a3, f3 = 0, 0
    if len(request.POST) > 0:
        if all(x  in request.POST for x in var_list):
            try:
                a1 = float(request.POST['A1'])
                f1 = float(request.POST['f1'])
                a2 = float(request.POST['A2'])
                f2 = float(request.POST['f2'])
                a3 = float(request.POST['A3'])
                f3 = float(request.POST['f3'])
            except:
                a1, f1 = 1, 220
                a2, f2 = 0, 0
                a3, f3 = 0, 0
    Fe = 11025
    t = np.arange(0, 2, 1 / Fe)
    y = np.zeros(shape=(t.shape[0],2),dtype=np.float32)
    y[:,0] = a1 * np.sin(2 * np.pi * f1 * t)
    y[:,0] += a2 * np.sin(2 * np.pi * f2 * t)
    y[:,0] += a3 * np.sin(2 * np.pi * f3 * t)
    y[:,1] = y[:,0]
    buf = io.BytesIO()
    write(buf, Fe, y)
    string = base64.b64encode(buf.read())
    urs =  urllib.parse.quote(string)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    txt_latex = 'Sinus mixed'
    ax.plot(t[0:1000] ,y[0:1000,0],label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='Sinus')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri1 =  urllib.parse.quote(string)
    plt.close(fig)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    txt_latex = 'Sinus mixed'
    ax.plot(t ,y[:, 1],label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='Sinus')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri2 =  urllib.parse.quote(string)
    plt.close(fig)

    return render(request,'melangeSinusMultiple.html',
                  {'a1': a1, 'f1': f1,
                  'a2': a2, 'f2': f2,
                  'a3': a3, 'f3': f3,
                  'data1': uri1,
                  'data2': uri2,
                  'data_snd': urs})

@xframe_options_exempt
def simul_sf(request):
    var_list = ['am2', 'am1', 'a0', 'ap1', 'ap2', 'bm2', 'bm1', 'b0', 'bp2', 'bp1']
    a0, b0= 0, 0
    ap1, bp1 = 2, 0
    am1, bm1 = 2, 0
    ap2, bp2 = 2, 0
    am2, bm2 = 2, 0
    if len(request.POST) > 0:
        if all(x  in request.POST for x in var_list):
            try:
                a0 = float(request.POST['a0'])
                b0 = float(request.POST['b0'])
                ap1 = float(request.POST['ap1'])
                bp1 = float(request.POST['bp1'])
                am1 = float(request.POST['am1'])
                bm1 = float(request.POST['bm1'])
                ap2 = float(request.POST['ap2'])
                bp2 = float(request.POST['bp2'])
                am2 = float(request.POST['am2'])
                bm2 = float(request.POST['bm2'])
            except:
                a0, b0= 0, 0
                ap1, bp1 = 2, 0
                am1, bm1 = 2, 0
                ap2, bp2 = 2, 0
                am2, bm2 = 2, 0
    T = 1
    c0 = a0 + 1j * b0;
    cp1 = ap1 + 1j * bp1;
    cm1 = am1 + 1j * bm1;
    cp2 = ap2 + 1j * bp2;
    cm2 = am2 + 1j * bm2;
    t = np.arange(-T, 2*T,1/1000)
    z = cm2 * np.exp (1j * 2 * np.pi * (-2) / T * t) + cm1 * np.exp(1j * 2 * np.pi * (-1) / T * t);
    z = z + c0 + cp1 * np.exp(1j * 2 * np.pi * 1 / T * t) + cp2 * np.exp(1j * 2* np.pi * 2 / T * t);
    fig, ax = plt.subplots(nrows=1, ncols=1)
    txt_latex = 'Partie réelle de f(t)'
    ax.plot(t , np.real(z), label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='f(t).x')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri1 =  urllib.parse.quote(string)
    plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
    fig, ax = plt.subplots(nrows=1, ncols=1)
    txt_latex = 'Partie imaginaire de f(t)'
    ax.plot(t , np.imag(z), label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='f(t).y')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri2 =  urllib.parse.quote(string)
    plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
    return render(request,'simulSF.html',
                  {'ap1': ap1, 'bp1': bp1,
                  'ap2': ap2, 'bp2': bp2,
                  'am2': am2, 'bm2': bm2,
                  'am1': am1, 'bm1': bm1,
                  'a0': a0, 'b0': b0,
                  'data1': uri1,
                  'data2': uri2})

@xframe_options_exempt
def tf_signal_amorti(request):
    var_list = ['f1', 'tau']
    f1, tau = 220, 10
    if len(request.POST) > 0:
        if all(x  in request.POST for x in var_list):
            try:
                f1 = float(request.POST['f1'])
                tau = float(request.POST['tau'])
            except:
                f1, tau = 220, 10
    Fe = 11025
    t = np.arange(0, 1, 1 / Fe)
    y = np.zeros(shape=(t.shape[0],2),dtype=np.float32)
    y[:, 0] = np.exp(-t * tau) * np.sin(2 * np.pi * f1 * t)
    y[:, 1] = y[:, 0]
    S = np.fft.fft(y[:, 0], axis=0)
    freq = np.fft.fftfreq(t.shape[0])*Fe
    buf = io.BytesIO()
    write(buf, Fe, y)
    string = base64.b64encode(buf.read())
    urs =  urllib.parse.quote(string)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    txt_latex = '$ s(t)= e^{-a t}\sin(2\pi f_0t) $'
    ax.plot(t ,y[:,0],label=txt_latex)
    ax.set(xlabel='temps', ylabel='u.a.', title='Signal')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri1 =  urllib.parse.quote(string)
    plt.close(fig)
    fig, ax = plt.subplots(nrows=1, ncols=1)
    txt_latex = 'Tf(s(t))'
    ax.plot(t ,np.abs(S),label=txt_latex)
    ax.set(xlabel='Frequency(Hz)', ylabel='u.a.', title='Signal Spectrum')
    ax.grid(True)
    ax.legend()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri2 =  urllib.parse.quote(string)
    plt.close(fig)

    return render(request,'tf_signal_amorti.html',
                  {'tau': tau, 'f1': f1,
                   'data1': uri1,
                   'data2': uri2,
                   'data_snd': urs})
