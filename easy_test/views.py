# Create your views here.
from django.shortcuts import render

def show_index( request ):
    return render( request, 'easy_test/index.html' )
