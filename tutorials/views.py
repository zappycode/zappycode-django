from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Tutorial

class TutorialListView(ListView):
    model = Tutorial
    template_name = "tutorials/tutorials_list.html"

class TutorialDetailView(DetailView):
    model = Tutorial    
    template_name = "tutorials/tutorials_detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["similar_tutorials"] = Tutorial.objects.get_similar_tutorials(kwargs.get("object"))
        return context