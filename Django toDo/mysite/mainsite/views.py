from unicodedata import name
from webbrowser import get
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import ToDoList, Item
from .forms import CreateNewList
# Create your views here.


def home(response):
    # return HttpResponse("<h1>WORKING!!!</h1>")
    return render(response, "mainsite/home.html", {})

def getid(response, id):
    ls = ToDoList.objects.get(id=id)
    # item = ls.item_set.get(id=1)

    if response.method == "POST":
        # print(response.POST)
        if response.POST.get("save"):
            for item in ls.item_set.all():
                if response.POST.get("c" + str(item.id)) == "clicked":
                    item.complete = True
                else: 
                    item.complete = False

                item.save()
        
        elif response.POST.get("newItem"):
            txt = response.POST.get("new")

            if len(txt) > 2:
                ls.item_set.create(text=txt, complete=False)
            else:
                print("Invalid input")

        elif response.POST.get("deleteItem"):
            delete_id = response.POST.get("deleteItem")
            t = ls.item_set.get(id=delete_id)
            t.delete()

    return render(response, "mainsite/list.html", {"ls":ls})

def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)
        if form.is_valid():
            n = form.cleaned_data['name']
            t = ToDoList(name=n)
            t.save()
            response.user.todolist.add(t)

        return HttpResponseRedirect("/%i" %t.id)
        
    else:
        form = CreateNewList()
    return render(response, "mainsite/create.html", {"form":form})

def list(response):
    ls = ToDoList.objects.all()
    item = Item.objects.all()
    print(response.POST)
    if response.method == "POST":
        if response.POST.get("deleteList"):
            delete_list = response.POST.get("deleteList")
            l = ToDoList.objects.get(id=delete_list)
            l.delete()
    return render(response, "mainsite/listview.html", {"ls":ls})


