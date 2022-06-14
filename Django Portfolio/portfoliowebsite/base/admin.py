from django.contrib import admin

# Register your models here.
from .models import Skill, Tag, Project, PBI_articles

admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(Tag)
admin.site.register(PBI_articles)