from django.shortcuts import render,redirect
from django.contrib import admin
from django.http import HttpResponse
from . models import *
from django.utils import timezone
from django.db.models import Q

def home(request):
    return render(request,'home.html',context={"current_tab":"home"}) 


def readers(request):
    return render(request,'readers.html',context={"current_tab":"readers"}) 



def save_student(request):
    student_name=request.POST['student_name']

    return render(request,"welcome.html",context={'student_name':student_name})

def reader_tab(request):
    query = request.POST.get('query', '')  # Initialize query at the start

    if request.method == "POST":
        readers = Reader.objects.all()
    else:
        readers = Reader.objects.raw("SELECT * FROM lbms_app_reader WHERE reader_name LIKE %s", ['%' + query + '%'])

    # Pagination
    paginator = Paginator(readers, 10)  # Show 10 readers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "readers.html", {
        "current_tab": "readers",
        "readers": page_obj,
        "query": query
    })

def save_reader(request):
    reader_item=Reader(reference_id=request.POST['reader_ref_id'],
                       reader_name=request.POST['reader_name'],
                       reader_contact=request.POST['reader_contact'],
                       reader_address=request.POST['reader_address'],
                       active=True
                       )
    reader_item.save()
    return redirect('/readers')

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

def book_list(request):
    search_query = request.GET.get('search_query', '')
    
    # Check if search query is being processed
    print("Search Query:", search_query)

    # Filter books based on search query
    if search_query:
        books = Book.objects.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    else:
        books = Book.objects.all()

    # Print the number of books retrieved
    print("Number of books retrieved:", books.count())
    
    # Implement pagination
    paginator = Paginator(books, 10)  # Show 10 books per page
    page_number = request.GET.get('page')  # Get the page number from the URL
    page_obj = paginator.get_page(page_number)  # Get the paginated object

    return render(request, 'book_list.html', {
        'page_obj': page_obj,
        'search_query': search_query  # Pass the search query for preserving it in the search form
    })


def issue_book(request):

    search_reader = request.GET.get('search_reader', '')
    search_book = request.GET.get('search_book', '')

    readers = Reader.objects.filter(reader_name__icontains=search_reader)
    books = Book.objects.filter(title__icontains=search_book, available_copies__gt=0)

    if request.method == 'POST':
        reader_id = request.POST['reader_id']
        book_id = request.POST['book_id']

        try:
            reader = Reader.objects.get(id=reader_id)
            book = Book.objects.get(id=book_id)

            # Check if book has available copies
            if book.available_copies > 0:
                # Issue the book
                BookIssue.objects.create(reader=reader, book=book)

                # Update available copies
                book.available_copies -= 1
                book.save()
                return redirect('book_list')  
            else:
                return render(request, 'issue_book.html', {
                    'readers': readers,
                    'books': books,
                    'error': 'No copies available.'
                })

        except Reader.DoesNotExist:
            return render(request, 'issue_book.html', {
                'readers': readers,
                'books': books,
                'error': 'Reader not found.'
            })

        except Book.DoesNotExist:
            return render(request, 'issue_book.html', {
                'readers': readers,
                'books': books,
                'error': 'Book not found.'
            })

    return render(request, 'issue_book.html', {
        'readers': readers,
        'books': books
    })

def return_book(request):
    search_query = request.GET.get('search_query', '')

    if request.method == 'POST':
        issue_id = request.POST['issue_id']
        try:
            book_issue = BookIssue.objects.get(id=issue_id)
            if not book_issue.is_returned:
                # Mark the book as returned
                book_issue.is_returned = True
                book_issue.return_date = timezone.now()
                book_issue.save()

                # Update the number of available copies
                book = book_issue.book
                book.available_copies += 1
                book.save()

                # Create a record for the returned book
                ReturnedBook.objects.create(
                    book_issue=book_issue,
                    returned_by=book_issue.reader.reader_name,
                    return_date=timezone.now()
                )

                return redirect('returns')
        except BookIssue.DoesNotExist:
            pass  

    # Search filter for issued books
    issued_books = BookIssue.objects.filter(is_returned=False)
    returned_books = ReturnedBook.objects.all()

    if search_query:
        # Filter both issued and returned books by title or reader's name
        issued_books = issued_books.filter(
            models.Q(book__title__icontains=search_query) | models.Q(reader__reader_name__icontains=search_query)
        )
        returned_books = returned_books.filter(
            models.Q(book_issue__book__title__icontains=search_query) | models.Q(returned_by__icontains=search_query)
        )

    # Pagination for issued books
    issued_paginator = Paginator(issued_books, 10)  # Show 10 issued books per page
    issued_page_number = request.GET.get('issued_page')
    issued_page_obj = issued_paginator.get_page(issued_page_number)

    # Pagination for returned books
    returned_paginator = Paginator(returned_books, 10)  # Show 10 returned books per page
    returned_page_number = request.GET.get('returned_page')
    returned_page_obj = returned_paginator.get_page(returned_page_number)

    return render(request, 'return.html', {
        'issued_books': issued_page_obj,
        'returned_books': returned_page_obj,
        'search_query': search_query
    })
                


def add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        isbn = request.POST['isbn']
        total_copies = int(request.POST['total_copies'])
        
        # Create a new book record
        Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            total_copies=total_copies,
            available_copies=total_copies
        )
        
        return redirect('book_list')  

    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

def view_issued_books(request):
    return render(request, 'issued_books.html', {'issued_books': issued_books})