# -*- coding: iso-8859-1 -*-
from django.shortcuts import render
from _overlapped import NULL
from gtpros.models import Trabajador

def index(request):
    if 'user' not in request.session:
        return render(request, 'gtpros/login.html', {})
    else:
        return render(request, 'gtpros/index.html', {})
    
def login(request):
    if request.POST:
        user = request.POST['user']
        password = request.POST['password']
        
        user = Trabajador.objects.filter(DNI=user)
        if (user != NULL):
            request.session['user'] = user
            return render(request, 'gtpros/index.html', {})
    else:
        return render(request, 'gtpros/login.html', {})
    
def logout(request):
    del request.session['user']
    return render(request, 'gtpros/logout.html', {})