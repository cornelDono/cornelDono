from cgitb import html
from multiprocessing import context
from urllib.request import Request
from django.shortcuts import render
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from .models import Project, Skill, PBI_articles
from .scripts.PBIscraper import get_last_article_name, collect_data, collect_data_increment

# Create your views here.
def homePage(request):
    projects = Project.objects.all()
    detailed_skills = Skill.objects.exclude(body='')
    skills = Skill.objects.filter(body='')
    context = {'projects' : projects, 'skills' : skills, 'detailed_skills' : detailed_skills}
    return render(request, 'base/home.html', context)

def projectPage(request, pk):
    project = Project.objects.get(id=pk)
    context = {'project' : project}
    return render(request, 'base/project.html', context)

def pbiProjectPage(request):
    print(request.POST)
    if request.method == "POST":
        if request.POST.get("refresh"):
            max_id = PBI_articles.objects.aggregate(Max('id'))['id__max']
            last_article = PBI_articles.objects.get(id=max_id).Article_title
            data_dict = collect_data_increment(last_article)
            if data_dict:
                data_dict.reverse()
                for data in data_dict:
                    b = PBI_articles(Article_title=data['Article_title'], Article_date=data['Article_date'], Article_short_text=data['Article_short_text'], 
                                                                    Aricle_list_tags=data['Aricle_list_tags'], Article_post_link=data['Article_post_link'])
                    b.save()
    pbi_articles = PBI_articles.objects.all().order_by('-id')[:10]
    context = {'pbi_articles':pbi_articles}
    return render(request, 'base/pbiProject.html', context)