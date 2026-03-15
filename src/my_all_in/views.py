from django.shortcuts import render



def index(request):
    num = [1,2,3,4,5]
    return render(request, "index.html",context={"num":num})

def auth(request):
    return render(request, "auth.html")