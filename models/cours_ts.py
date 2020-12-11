from django.shortcuts import render
from django.utils.safestring import mark_safe
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

def TableauHtml(titreTab, titre_lig, titreCol, x):
    nbl, nbc = x.shape
    texte = '<table align=center border=1><caption>' + titreTab + '<caption><tr>'
    if len(titreCol)>0:
        ligne = '<tr>'
        for j in range(0, nbc+1):
            ligne = ligne + '<td>' + titreCol[j] + '</td>';
    texte = texte + ligne + '</tr>'
    for i in range(0, nbl):
        ligne='<tr>';
        if titre_lig and len(titre_lig)>0:
            ligne = ligne + '<td>' + titre_lig[i] + '</td>'
        for j in range(0, nbc):
            ligne = ligne + '<td>' +str(x[i,j]) + '</td>'
        texte = texte + ligne + '</tr>'
    texte = texte + '</table>'
    return texte

    
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

def  reconstruction(tpsContinu,taille,Fe,x):
    N = x.shape[0]
    tr = tpsContinu
    k = np.array([*range(0,N)])
    f = []
    for t_ext in tr:
        k2 = np.argmin(abs(t_ext-k / Fe))
        k1 = np.array([*range(max( k2-taille,0), min(k2+taille,N-1))])
        yr =  Fe * (t_ext - k1 / Fe)
        sincy = np.sinc(yr)
        f.append(np.sum(x[k1] * sincy))
    return np.array(f)
    
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
        b_ok, val = get_arg_post(self.request, ['nu'])
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
                                          
class EchantillonnageEx1:
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        self.nu1 = 220
        self.nu2 = 220 * 2 **(1/3)
        
    def genere_ref(self, Fe):
        N = min(np.log(Fe) / np.log(2), 1024)
        te = np.arange(0, Fe) / Fe
        t = np.arange(0, 22050) / 22050
        
        y = 30 * (np.sin( 2 * np.pi * self.nu1 * t) + np.sin( 2 * np.pi * self.nu2 * t))
        ye = 30* (np.sin( 2 * np.pi * self.nu1 * te) + np.sin( 2 * np.pi * self.nu2 * te))
        x = np.zeros(shape=(3, te.shape[0]),dtype=np.float32)
        x[0, :] = te
        x[1, :] = ye
        x[2, :] = np.floor(ye)
        return t, x, y
        
    def graphique1(self, x, y, t, indte, indt):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Signal continu'
        ax.plot(t[indt] , y[indt], label=txt_latex)
        txt_latex = 'Signal échantillonné'
        ax.scatter(x[0, indte] , np.floor(x[1, indte]), label=txt_latex,marker="o", color='r')
        ax.set(xlabel='temps', ylabel='u.a.')
        for v in indte: 
            ax.vlines(x[0, v], 0, np.floor(x[1, v]), colors='red', linestyles='dashed')
        ax.grid(True)
        ax.legend()
        uri1 = convert_figure_uri(fig)
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        return uri1
        
    def __call__(self):
        var_list = ['Fe']
        Fe = 1000
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            Fe = np.int(max(np.abs(float(val[0])),100))
        t, x, y = self.genere_ref(Fe)
        
        indte = np.where(np.logical_and(x[0, :] > 3 / self.nu1, x[0, :] < 6 / self.nu1))
        indt = np.where(np.logical_and(t > 3 / self.nu1, t < 6 / self.nu1))
        uri1 = self.graphique1(x, y, t, indte, indt)
        urs = convert_npson_uri(x[1, :]/80, Fe)
        titre_col =[str(v) for v in indte[0]]
        titre_col.insert(0,'k')
        tableau = TableauHtml(' ',['temps',' valeurs analogiques',' valeurs échantillonnées'],titre_col,x[:, indte[0]])
        
        return 'echantillonnage_ex1.html', {'Fe': Fe, 'data1': uri1, 'data_snd': urs, 'tableau':mark_safe(tableau)}

class EchantillonnageEx2(EchantillonnageEx1):
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        self.nu1 = 220
        self.nu2 = 220 * 2 **(1/3)

    def __call__(self):
        var_list = ['Fe']
        Fe = 1000
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            Fe = np.int(max(np.abs(float(val[0])),100))
        t, x, y = self.genere_ref(Fe)
        indte = np.where(np.logical_and(x[0, :] > 3 / self.nu1, x[0, :] < 6 / self.nu1))
        indt = np.where(np.logical_and(t > 3 / self.nu1, t < 6 / self.nu1))
        uri1 = self.graphique1(x, y, t, indte, indt)
        urs1 = convert_npson_uri(y / 80 , 22050)
        urs2 = convert_npson_uri(x[1, :]/80, Fe)
        yr = reconstruction(t[indt[0]],40,Fe,x[1,:])
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Signal reconstruit'
        ax.plot(t[indt] , yr, label=txt_latex)
        txt_latex = 'Signal échnatillonné'
        ax.scatter(x[0, indte] , np.floor(x[1, indte]), label=txt_latex,marker="o", color='r')
        ax.set(xlabel='temps', ylabel='u.a.')
        for v in indte: 
            ax.vlines(x[0, v], 0, np.floor(x[1, v]), colors='red', linestyles='dashed')
        ax.grid(True)
        ax.legend()
        uri2 = convert_figure_uri(fig)
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        histo_donnees, position_classe = np.histogram(yr - y[indt], 20)
        fig, ax = plt.subplots(nrows=1, ncols=1)
        # tracer de l'histogramme en appelant hist
        ax.hist(position_classe[:-1], position_classe, weights=histo_donnees,edgecolor='black')
        uri3 = convert_figure_uri(fig)
        plt.close(fig)
        return 'reconstruction.html', {'Fe': Fe, 'data1': uri1, 'data2': uri2, 'data3':uri3,
                                       'data_snd1': urs1, 'data_snd2': urs2}

class EchantillonnageEx3(EchantillonnageEx1):
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        self.nu1 = 220
        self.nu2 = np.int(220 * 2 **(1/3)*100)/100

    def __call__(self):
        var_list = ['Fe']
        Fe = 1000
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            Fe = np.int(max(np.abs(float(val[0])),100))
        x1 = []
        x2 = []
        x3 = []
        x4 = []
        titre_col = ['k']
        for k in range(-3,4):
            titre_col.append(str(k))
            x1.append(np.int((self.nu1 + k * Fe)*100)/100)
            x2.append(self.nu2 + k * Fe)
            x3.append(-self.nu1 + k * Fe)
            x4.append(-self.nu2 + k * Fe)
        x1.sort()    
        x2.sort()   
        x = np.array([x1, x2, x3, x4])
        print(x.shape)
        print(len(titre_col))
        tableau = TableauHtml(' ',
                              ['position de la raie ' + str(self.nu1) + 'Hz pour k*Fe',
                               'position de la raie ' + str(self.nu2) + 'Hz pour k*Fe',
                               'position de la raie ' + str(-self.nu1) + 'Hz pour k*Fe',
                               'position de la raie ' + str(-self.nu2) + 'Hz pour k*Fe',
                               ],
                              titre_col, x)
        return 'echantillonnage_ex3.html', {'Fe': Fe, 'tableau':mark_safe(tableau)}

class CNAExo():
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def __call__(self):
        var_list = ['n', 'UMin', 'UMax', 'N']
        n = 13107
        umin = -5
        umax = 5
        N = 16
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            n = float(val[0])
            umin = float(val[1])
            umax = float(val[2])
            N = int(val[3])
            n = max(min(n, 2 **(N-1) - 1), -2 ** (N - 1))
        vout = n / 2 ** N * (umax - umin)
        x = np.array([[N, umin, umax, n, vout]])
        tableau = TableauHtml(' ',
                              ['',''],
                              ['','N',
                               'UMin',
                               'UMax',
                               "Valeur numérique d'entrée",
                               "Valeur de sortie du CNA en V"
                               ], x)
        return 'cna_exo.html', {'n': n, 'UMin': umin, 'UMax': umax, 'N':N, 'tableau':mark_safe(tableau)}

class CANExo():
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory

    def __call__(self):
        var_list = ['vin', 'UMin', 'UMax', 'N']
        vin = 2
        umin = -5
        umax = 5
        N = 16
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            vin = float(val[0])
            umin = float(val[1])
            umax = float(val[2])
            N = int(val[3])
        n = max(min(np.floor(2**N*vin/(umax-umin)),2**(N-1)-1),-2**(N-1))
        x = np.array([[N, umin, umax, vin, n]])
        tableau = TableauHtml(' ',
                              ['',''],
                              ['','N',
                               'UMin',
                               'UMax',
                               "Tension d'entrée",
                               "Valeur en sortie du CAN"
                               ], x)
        return 'can_exo.html', {'vin': vin, 'UMin': umin, 'UMax': umax, 'N':N, 'tableau':mark_safe(tableau)}

class ConvolExo1():
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        self.h =  np.array([1,3, 2])

    def __call__(self):
        var_list = ['N']
        N = 10
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            N = int(val[0])
        x = np.random.randint(11, size=N)-5
        y = np.convolve(self.h,x)
        xx =  np.zeros((3,y.shape[0]))
        xx[0,0:N] = x 
        xx[1,0:self.h.shape[0]] = self.h
        xx[2] = y
        titre_col = ['k']
        for k in range(0,y.shape[0]):
            titre_col.append(str(k))
        tableau = TableauHtml(' ',
                              ['x','h','x*h'],
                              titre_col,
                              xx)
        fig, ax = plt.subplots(nrows=1, ncols=1)
        txt_latex = 'Signal x'
        ax.scatter(range(0,x.shape[0]) , x, label=txt_latex, color='red')
        txt_latex = '(x*h)(i)'
        ax.scatter(range(0,y.shape[0]) , y, label=txt_latex, color='blue')
        for idx, v in enumerate(x): 
            ax.vlines(idx, 0, v, color='red', linestyles='dashed')
        for idx, v in enumerate(y): 
            ax.vlines(idx, 0, v, color='blue', linestyles='dashed')
        ax.grid(True)
        ax.legend()
        uri = convert_figure_uri(fig)
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        return 'convol_exo1.html', {'N':N, 'tableau':mark_safe(tableau), 'data':uri}

class ConvolExo2(ConvolExo1):
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        self.h =  np.array([1, -1])

class IntercorrExo1():
    def __init__(self, request=None, buf_memory=True):
        self.request = request
        self.memory = buf_memory
        self.ori_x = 0
        self.ori_y = 0
        self.x = np.array([[*range(self.ori_x, 8 + self.ori_x)],[1, 1, -1, -1, 1, 1, -1, -1]])
        self.y = np.array([[*range(self.ori_y, 4 + self.ori_y)],
                          [1, 1, -1, -1]])
 
    def intercorr(self, x,y):
        """
        Intercorrélation de x par y
        Si x et y ont deux lignes 
        la premère ligne représente le temps
        la seconde ligne la valeur au temps donné
        dans les autres cas l'origine des temps est supposé 0
        """
        nblx, nbcx = x.shape
        nbly, nbcy = y.shape
        if min(nblx,nbcx) == min(nbcy,nbly) and min(nblx,nbcx)==2:
            cxy = np.correlate(x[1,:], y[1,:], "full")
            t_cxy = np.zeros((2,cxy.shape[0]))
            t_cxy[1,:] = cxy
            indx = np.where(x[1,:] != 0)
            indy = np.where(y[1,:] != 0)
            t_cxy[0, :] = np.arange(x[0,min(indx[0])] - y[0, max(indy[0])],
                                    x[0,max(indx[0])] - y[0, min(indy[0])] + 1)
        elif min(nblx,nbcx) == min(nbcy,nbly) and min(nblx,nbcx) == 1:
            cxy = np.correlate(x, y, "full")
            t_cxy = np.zeros((2,cxy.shape[0]))
            t_cxy[1,:] = cxy
            t_cxy[0,:] = np.arange(-y.shape[0], x.shape[0]);
        else:
            t_cxy = None
        return t_cxy


    def __call__(self):
        var_list = ['ori_x', 'ori_y']
        N = 10
        b_ok, val = get_arg_post(self.request, var_list)
        if b_ok:
            self.ori_x = int(val[0])
            self.ori_y = int(val[1])
        self.x[0,:] = self.x[0,:] + self.ori_x
        self.y[0,:] = self.y[0,:] + self.ori_y
        cxy = self.intercorr(self.x, self.y)
        titre_col = ['k']
        xx = [[],[],[]]
        deb = int(min(cxy[0,0],self.x[0,0],self.y[0,0]))
        fin = int(max(cxy[0,-1],self.x[0,-1],self.y[0,-1]))
        for k in range(deb,fin+1):
            titre_col.append(str(k))
            ind = np.where(self.x[0,:]==k)
            if ind[0].shape[0]:
                xx[0].append((self.x[1,ind[0][0]]))
            else:
                xx[0].append(0)
            ind = np.where(self.y[0,:]==k)
            if ind[0].shape[0]:
                xx[1].append((self.y[1,ind[0][0]]))
            else:
                xx[1].append(0)
            ind = np.where(cxy[0,:]==k)
            if ind[0].shape[0]:
                xx[2].append((cxy[1,ind[0][0]]))
            else:
                xx[2].append(0)
        xx = np.array(xx)
        tableau = TableauHtml(' ',
                              ['x','y','cxy'],
                              titre_col,
                              np.array(xx))
        fig, ax = plt.subplots(nrows=3, ncols=1)
        txt_latex = 'Signal x'
        val_abs = [*range(deb,fin+1)]
        ax[0].scatter(val_abs , xx[0, :], label=txt_latex, color='red')
        for idx, v in enumerate(xx[0, :]): 
            ax[0].vlines(val_abs[idx], 0, v, color='red', linestyles='dashed')
        ax[0].grid(True)
        ax[0].legend()
        txt_latex = 'Signal y'
        ax[1].scatter(val_abs , xx[1, :], label=txt_latex, color='blue')
        for idx, v in enumerate(xx[1, :]): 
            ax[1].vlines(val_abs[idx], 0, v, color='blue', linestyles='dashed')
        ax[1].grid(True)
        ax[1].legend()
        txt_latex = '$ c_{xy} $'
        ax[2].scatter(val_abs , xx[2, :], label=txt_latex, color='green')
        for idx, v in enumerate(xx[2, :]): 
            ax[2].vlines(val_abs[idx], 0, v, color='green', linestyles='dashed')
        ax[2].grid(True)
        ax[2].legend()
        ax[2].set(xlabel='temps', ylabel='u.a.')
        plt.tight_layout()
        uri = convert_figure_uri(fig)
        plt.close(fig)    #convert graph into dtring buffer and then we convert 64 bit code into image
        return 'intercorr_exo1.html', {'ori_x':self.ori_x, 'ori_y':self.ori_y,
                                       'tableau':mark_safe(tableau), 'data':uri}
