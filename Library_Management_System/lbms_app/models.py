from django.db import models
from django.utils import timezone

# Create your models here.

class Reader(models.Model):
    def __str__(self):
        return self.reader_name
    
    reference_id=models.CharField(max_length=200)
    reader_name=models.CharField(max_length=200)
    reader_contact=models.CharField(max_length=200)
    reader_address=models.TextField()
    active=models.BooleanField(default=True)

class Book(models.Model):
    title= models.CharField(max_length=200)
    author= models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()

    def __str__(self):
        return self.title

class BookIssue(models.Model):
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE)
    book = models.ForeignKey(Book , on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.book.title} issued to {self.reader.reader_name}"

class ReturnedBook(models.Model):
    book_issue = models.ForeignKey(BookIssue, on_delete=models.CASCADE)
    returned_by = models.CharField(max_length=225)
    return_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.book_issue.book} returned by {self.book_issue.reader.reader_name}"    