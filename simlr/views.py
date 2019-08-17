from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import mainapp

def index(request):
    if request.session.get('redirected') is None:
        context = {
            'current_playlist_url': None,
            'seed_artist': None,
        }
    else:
        request.session['redirected'] = None
        context = {
            'current_playlist_url': request.session.get('playlisturl', None),
            'seed_artist': request.session.get('seedartist', None),
        }
    return render(request, 'simlr/index.html', context)

def playlist(request):
    
    seedartist = request.POST['seedartist']
    request.session['seedartist'] = seedartist
    request.session['playlisturl'] = mainapp.get_youtube_playlist(seedartist)
    request.session['redirected'] = True
    return HttpResponseRedirect(reverse('simlr:index'))
