"""
URL configuration for LBMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home),
    path('home',views.home),
    path('readers',views.reader_tab,name="readers"),
    # path('save',views.save_student),
    path('readers/add',views.save_reader,name="add_reader"),
    path('books',views.book_list,name='book_list'),
    path('issue/',views.issue_book,name="issue"),
    path('returns/', views.return_book, name='returns'),
    path('books/add/', views.add_book, name='add_book'),
    path('issued-books/', views.return_book, name='view_issued_books'),
    path('readers/', views.reader_tab, name='view_readers'),
    path('books/', views.book_list, name='view_books'),
    
]
