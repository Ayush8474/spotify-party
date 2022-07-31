from django.shortcuts import render,redirect
from . import INFO
from . import templates
from django.http import JsonResponse,HttpResponse
import requests
import base64
import datetime
from django.template import loader
from pytube import Search
# Create your views here.

def login(req):
        client_id = INFO.CLIENT_ID
        redirect_uri = INFO.REDIRECT_URI
        response_type = "code"
        url = "http://accounts.spotify.com/authorize"
        payload = {'client_id':client_id, 'redirect_uri':redirect_uri,'response_type':response_type}
        return redirect(requests.get(url=url, params=payload).url)




def login_success(req):
    code = req.GET.get("code")
    payload = {'grant_type':'authorization_code',
               'code':code,
               'redirect_uri':INFO.REDIRECT_URI,
               'client_id':INFO.CLIENT_ID,
                'client_secret':INFO.CLIENT_SECRET
               }
    # the following doesn't work, inspite of being directed to do so in the docs
    # headers = {
    #     'Authorization':"Basic "+base64.urlsafe_b64encode(b'INFO.CLIENT_ID+":"+INFO.CLIENT_SECRET').decode("utf-8"),
    #     'Content-Type':'application/x-www-form-urlencoded'
    # }

    res = requests.post(url = "https://accounts.spotify.com/api/token",data=payload)
    res_json = res.json()

    ret_response = JsonResponse(res_json)
    print("ret_response:")
    print(res_json)

    spotify_party_access_token = res_json['access_token']
    spotify_party_refresh_token = res_json['refresh_token']
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=res_json['expires_in']),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    ret_response.set_cookie('spotify_party_access_token', spotify_party_access_token, expires=expires)
    ret_response.set_cookie('spotify_party_refresh_token', spotify_party_refresh_token)
    return ret_response

def get_token_by_refresh(refr):
    payload = {'grant_type': 'refresh_token',
               'refresh_token':refr,
               'client_id': INFO.CLIENT_ID,
               'client_secret': INFO.CLIENT_SECRET
               }
    url = 'https://accounts.spotify.com/api/token'
    res = requests.post(url,data=payload)
    return res.json()


def search(req):
    query = str(req.GET.get("q"))
    retaken = False
    if 'spotify_party_access_token' in req.COOKIES:
        token = str(req.COOKIES.get('spotify_party_access_token'))
    else:
        res_json = get_token_by_refresh(str(req.COOKIES.get('spotify_party_refresh_token')))
        print(res_json)
        spotify_party_access_token = res_json['access_token']
        #spotify_party_refresh_token = res_json['refresh_token']
        expires = datetime.datetime.strftime(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=res_json['expires_in']),
            "%a, %d-%b-%Y %H:%M:%S GMT",
        )

        #ret_response.set_cookie('spotify_party_refresh_token', spotify_party_refresh_token)
        token = spotify_party_access_token
        retaken = True
    url = 'https://api.spotify.com/v1/search'
    payload = {
        "q":query,
        "type":"track",
        "include_external":"audio",
        "market":"IN",
        "limit":"5",
    }
    headers = {
        "Authorization":"Bearer "+token
    }

    res = requests.get(url,params=payload,headers=headers)
    jres =  res.json()
    #return JsonResponse(jres)
    #print(jres)
    track_name = jres['tracks']['items'][0]['name']
    track_artist = jres['tracks']['items'][0]['artists'][0]['name']
    track_url = jres['tracks']['items'][0]['external_urls']['spotify']
    #track_playback(token)

    print(track_name+' '+track_artist)
    yt_search_result = Search(track_name+' '+track_artist)
    print(yt_search_result.results)
    return redirect(track_url)



    # print("track_id: "+track_id)
    # context = {
    #     "track_id":str(track_id)
    # }
    # template = loader.get_template('track_play.html')
    # ret_response = HttpResponse(template.render(context=context))
    # if retaken:
    #     ret_response.set_cookie('spotify_party_access_token', token, expires=expires)
    # return ret_response
    # #return redirect(requests.get(track_url).url)

def track_playback(token):
    while True:
        url = 'https://api.spotify.com/v1/me/player/'
        payload = { }
        headers = {
            "Authorization": "Bearer " + token
        }
        res = requests.get(url, params=payload, headers=headers)
        print(res.json())
        break;



