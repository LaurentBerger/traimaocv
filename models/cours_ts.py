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
from scipy.signal import chirp

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
    
def convert_figure_uri(fig):
    """
    conversion d'une figure matplot en uri
    fig --> objet créé par fig,_ = plt.subplots
    valeur de retour --> uri
    """
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    return uri

def convert_npson_uri(x, Fe):
    """
    conversion d'un tableau numpy en uri wav
    x --> tableau numpy
    valeur de retour --> uri
    """
    if len(x.shape) == 1:
        y = np.zeros(shape=(x.shape[0],2),dtype=np.float32)
        y[:,0] = x
        y[:,1] = x
    else:
        if x.shape[1] != 2:
            y = x.transpose()
        else:
            y = x
    buf = io.BytesIO()
    write(buf, Fe, y)
    string = base64.b64encode(buf.read())
    urs =  urllib.parse.quote(string)
    return urs
    
    
def porte(t):
    ind = np.where(np.logical_or(t<-1/2, t>1/2))
    y = np.ones(shape=(t.shape[0], ), dtype = np.float32)
    y[ind]=0
    return y

class Frequence:
    """
    Affichage du graphique d'un sinus en fonction 
    de la fréquence et de la phase
    """
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
    
    def __call__(self):
        freq = 1
        phase = 0
        b_ok, val = get_arg_post(self.request, ['freq', 'phase'])
        if b_ok:
            freq = float(val[0])
            phase = float(val[1])
                    
        fig, ax = plt.subplots(nrows=1, ncols=1)
        x = np.arange(0, 10, 0.01)
        txt_latex = '$sin(2\pi'+str(freq)+'t - '+str(phase) + ' )$'
        ax.plot(x ,np.sin( 2 * np.pi * freq * x - phase),label=txt_latex)
        ax.set(xlabel='temps', ylabel='u.a.', title='Sinus')
        ax.grid(True)
        ax.legend()
        uri =  convert_figure_uri(fig)
        plt.close(fig)
        return 'frequence.html',{'data':uri, 'freq':freq, 'phase':phase}

class CercleTrigo:
    """
    Affichage du cercle trigonmétrique en fonction 
    d'un angle en radian
    """
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        
    def __call__(self):
        a = 1
        b_ok, val = get_arg_post(self.request, ['angle'])
        if b_ok:
            a = float(val[0])
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
        plt.close(fig)
        #convert graph into dtring buffer and then we convert 64 bit code into image
        uri =  convert_figure_uri(fig)
        return 'cercle_trigo.html',{'data':uri, 'angle':a}

        
class TransSimil:
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def __call__(self):
        a_simil, t0 = 1, 0
        b_ok, val = get_arg_post(self.request, ['a', 't0'])
        if b_ok:
            a_simil, t0 = float(val[0]), float(val[1])
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
        uri1 =  convert_figure_uri(fig)
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        y = porte(a_simil * (t-t0))
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Signal f('+ str(a_simil) + '(t-('  + str(t0) + ')))'
        ax.plot(t , y, label=txt_latex)
        ax.set(xlabel='temps', ylabel='u.a.', title='Orignal')
        ax.grid(True)
        ax.legend()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        uri2 =  convert_figure_uri(fig)      
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        return 'exoTranslationSimiltude.html',{'data1':uri1, 'data2':uri2, 'a_simil':a_simil, 't0':t0}

class FreqSpatiale2d:
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def __call__(self):
        nu = 0.01
        b_ok, val = get_arg_post(self.request, ['a', 't0'])
        if b_ok:
            nu = float(val[0])
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
        uri1 =  convert_figure_uri(fig)      
        plt.close(fig)
        fig = plt.figure(figsize=plt.figaspect(1))
        ax = fig.add_subplot(1, 1, 1, projection='3d')
        surf = ax.plot_surface(x2d, y2d, z, rstride=1, cstride=1, cmap=cm.coolwarm,
                           linewidth=0, antialiased=False)
        ax.set(title=s, xlabel=' x (m)', ylabel='y (m)')  
        uri2 =  convert_figure_uri(fig)
        plt.close(fig)   
        return 'freqSpatiale2d.html',{'data1':uri1, 'data2':uri2, 'nu':nu}
    
class MelangeSinus:
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def __call__(self):
        nu = 0.01
        var_list = ['A1', 'f1', 'A2', 'f2', 'A3', 'f3']
        a1, f1 = 1, 220
        a2, f2 = 0, 0
        a3, f3 = 0, 0
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            a1 = float(val[0])
            f1 = float(val[1])
            a2 = float(val[2])
            f2 = float(val[3])
            a3 = float(val[4])
            f3 = float(val[5])
        Fe = 11025
        t = np.arange(0, 2, 1 / Fe)
        y = np.zeros(shape=(t.shape[0],2),dtype=np.float32)
        y = a1 * np.sin(2 * np.pi * f1 * t)
        y += a2 * np.sin(2 * np.pi * f2 * t)
        y += a3 * np.sin(2 * np.pi * f3 * t)
        urs =  convert_npson_uri(y, Fe)
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Sinus mixed'
        ax.plot(t[0:1000] ,y[0:1000],label=txt_latex)
        ax.set(xlabel='temps', ylabel='u.a.', title='Sinus')
        ax.grid(True)
        ax.legend()
        uri1 = convert_figure_uri(fig)
        plt.close(fig)
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Sinus mixed'
        ax.plot(t ,y,label=txt_latex)
        ax.set(xlabel='temps', ylabel='u.a.', title='Sinus')
        ax.grid(True)
        ax.legend()
        uri2 = convert_figure_uri(fig)
        plt.close(fig)

        return 'melangeSinusMultiple.html',{'a1': a1, 'f1': f1,
                                            'a2': a2, 'f2': f2,
                                            'a3': a3, 'f3': f3,
                                            'data1': uri1,
                                            'data2': uri2,
                                            'data_snd': urs}

class SimulSF:
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def __call__(self):
        var_list = ['am2', 'am1', 'a0', 'ap1', 'ap2', 'bm2', 'bm1', 'b0', 'bp1', 'bp2']
        a0, b0= 0, 0
        ap1, bp1 = 2, 0
        am1, bm1 = 2, 0
        ap2, bp2 = 2, 0
        am2, bm2 = 2, 0
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            am2 = float(val[0])
            am1 = float(val[1])
            a0 = float(val[2])
            ap1 = float(val[3])
            ap2 = float(val[4])
            bm2 = float(val[5])
            bm1 = float(val[6])
            b0 = float(val[7])
            bp1 = float(val[8])
            bp2 = float(val[9])
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
        uri1 = convert_figure_uri(fig)
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Partie imaginaire de f(t)'
        ax.plot(t , np.imag(z), label=txt_latex)
        ax.set(xlabel='temps', ylabel='u.a.', title='f(t).y')
        ax.grid(True)
        ax.legend()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        uri2 = convert_figure_uri(fig)
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        return 'simulSF.html', {'ap1': ap1, 'bp1': bp1,
                                'ap2': ap2, 'bp2': bp2,
                                'am2': am2, 'bm2': bm2,
                                'am1': am1, 'bm1': bm1,
                                'a0': a0, 'b0': b0,
                                'data1': uri1,
                                'data2': uri2}


class TFSignalAmorti:
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def graphique1(self, t, y, nom_signal):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(t ,y,label=nom_signal)
        ax.set(xlabel='temps', ylabel='u.a.', title='Signal')
        ax.grid(True)
        ax.legend()
        #convert graph into dtring buffer and then we convert 64 bit code into image
        uri1 = convert_figure_uri(fig)
        plt.close(fig)
        return uri1
        
    def graphique2(self, t, y, Fe):
        S = np.fft.fft(y, axis=0)
        freq = np.fft.fftfreq(t.shape[0])*Fe
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Tf(s(t))'
        ax.plot(freq ,np.abs(S),label=txt_latex)
        ax.set(xlabel='Frequency(Hz)', ylabel='u.a.', title='Signal Spectrum')
        ax.grid(True)
        ax.legend()
        uri2 = convert_figure_uri(fig)
        plt.close(fig)
        return uri2
        
    def __call__(self):
        var_list = ['f1', 'tau']
        f1, tau = 220, 10
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            f1 = float(val[0])
            tau = float(val[1])
        Fe = 11025
        t = np.arange(0, 1, 1 / Fe)
        y = np.exp(-t * tau) * np.sin(2 * np.pi * f1 * t)
        uri1 = self.graphique1(t, y, '$ s(t)= e^{-a t}\sin(2\pi f_0t) $')
        uri2 = self.graphique1(t, y, Fe)
        urs =  convert_npson_uri(y, Fe)

        return 'tf_signal_amorti.html', {'tau': tau, 'f1': f1,
                                         'data1': uri1,
                                         'data2': uri2,
                                         'data_snd': urs}

class TFChirpLin(TFSignalAmorti):
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

        
    def __call__(self):
        var_list = ['f0', 'f1']
        f0, f1 = 100, 1000
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            f0 = float(val[0])
            f1 = float(val[1])
        Fe = 11025
        t = np.arange(0, 1, 1 / Fe)
        y = chirp(t, f0=f0, f1=f1, t1=max(t), method='linear')
        uri1 = self.graphique1(t, y, '$ chirp$')
        uri2 = self.graphique2(t, y, Fe)
        urs =  convert_npson_uri(y, Fe)

        return 'tf_chirp_lin.html', {'f0': f0, 'f1': f1,
                                         'data1': uri1,
                                         'data2': uri2,
                                         'data_snd': urs}

                                         
class FondaHarmo:
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def graphique1(self, t, y, idx=None):        
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Fréquence et harmonique'
        if idx:
            ax.plot(t[idx] ,y[idx],label=txt_latex)
        else:
            ax.plot(t ,y,label=txt_latex)
        ax.set(xlabel='temps', ylabel='u.a.', title='Sinus')
        ax.grid(True)
        ax.legend()
        uri1 = convert_figure_uri(fig)
        plt.close(fig)
        return uri1
     
    def graphique2(self, t, y, Fe):
        S = np.fft.fft(y, axis=0)
        freq = np.fft.fftfreq(t.shape[0])*Fe
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Tf(s(t))'
        ax.plot(freq ,np.abs(S),label=txt_latex)
        ax.set(xlabel='Frequency(Hz)', ylabel='u.a.', title='Signal Spectrum')
        ax.grid(True)
        ax.legend()
        uri2 = convert_figure_uri(fig)
        return uri2
        
    def __call__(self):
        var_list = ['A1', 'f1', 'A2', 'A3', 'A4', 'A5']
        A1, f1 = 1, 220
        A2, A3 = 0, 0
        A4, A5 = 0, 0
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            A1 = float(val[0])
            f1 = float(val[1])
            A2 = float(val[2])
            A3 = float(val[3])
            A4 = float(val[4])
            A5 = float(val[5])
        Fe = 11025
        t = np.arange(0, 2, 1 / Fe)
        y = A1 * np.sin(2 * np.pi * f1 * t)
        y += A2 * np.sin(2 * np.pi * 2 *f1 * t)
        y += A3 * np.sin(2 * np.pi * 3 *f1 * t)
        y += A4 * np.sin(2 * np.pi * 4 *f1 * t)
        y += A5 * np.sin(2 * np.pi * 5 *f1 * t)
        urs =  convert_npson_uri(y, Fe)
        uri1 = self.graphique1(t, y, range(0,1000))
        uri2 = self.graphique2(t, y, Fe)
        return 'fonda_harmo.html',{'A1': A1, 'f1': f1,
                                   'A2': A2, 'A3': A3, 
                                   'A3': A3, 'A4': A4,
                                   'A5': A5,
                                   'data1': uri1,
                                   'data2': uri2,
                                   'data_snd': urs}

class FondaHarmoAmorti(FondaHarmo):
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        
    
    def __call__(self):
        var_list = [ 'A1', 'f1', 'A2', 'A3', 'A4', 'A5', 'tau']
        A1, f1 = 1, 220
        A2, A3 = 0, 0
        A4, A5 = 0, 0
        tau = 10
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            A1 = float(val[0])
            A1 = float(val[0])
            f1 = float(val[1])
            A2 = float(val[2])
            A3 = float(val[3])
            A4 = float(val[4])
            A5 = float(val[5])
            tau = float(val[6])
        Fe = 11025
        t = np.arange(0, 2, 1 / Fe)
        y = A1 * np.sin(2 * np.pi * f1 * t)
        y += A2 * np.sin(2 * np.pi * 2 *f1 * t)
        y += A3 * np.sin(2 * np.pi * 3 *f1 * t)
        y += A4 * np.sin(2 * np.pi * 4 *f1 * t)
        y += A5 * np.sin(2 * np.pi * 5 *f1 * t)
        y = y * np.exp(-tau * t)
        urs =  convert_npson_uri(y, Fe)
        uri1 = self.graphique1(t, y)
        uri2 = self.graphique2(t, y, Fe)
        return 'fonda_harmo_amorti.html',{'A1': A1, 'f1': f1,
                                          'A2': A2, 'A3': A3, 
                                          'A3': A3, 'A4': A4,
                                          'A5': A5, 'tau': tau,
                                          'data1': uri1,
                                          'data2': uri2,
                                          'data_snd': urs}