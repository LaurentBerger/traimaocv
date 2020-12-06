# Create your views here.
from django.shortcuts import render
import io
import urllib, base64
from django.http import HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import cours_ts as cts


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
