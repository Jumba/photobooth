from django.shortcuts import render, render_to_response
from frontend.models import Photo

# Create your views here.
def index(request):
    return render_to_response('index.html', {'photos': Photo.objects.order_by('uploaded_at')})