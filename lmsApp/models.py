# from distutils.command.upload import upload
from email.policy import default

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from PIL import Image


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250)
    status = models.CharField(
        max_length=2, choices=(("1", "Active"), ("2", "Inactive")), default=1
    )
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Categories"

    def __str__(self):
        return str(f"{self.name}")


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    status = models.CharField(
        max_length=2, choices=(("1", "Active"), ("2", "Inactive")), default=1
    )
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_created = models.DateTimeField(auto_now=True)

    class Meta: 
        verbose_name_plural = "List of Categories"

    def __str__(self):
        return str(f"{self.category} - {self.name}")

class Books(models.Model):
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    author = models.TextField(blank=True, null=True)
    publisher = models.TextField(blank=True, null=True)
    price = models.CharField(max_length=50, blank=True, null=True)
    berow = models.CharField(max_length=50, blank=True, null=True)
    rack = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=2, choices=(("1", "Active"), ("2", "Inactive")), default="1"
    )
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "List of Books"

    def __str__(self):
        return f"{self.isbn} - {self.title}"





class Students(models.Model):
    code = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    gender = models.CharField(
        max_length=20, choices=(("Male", "Male"), ("Female", "Female")), default="Male"
    )
    contact = models.CharField(max_length=250)
    department = models.CharField(max_length=250, blank=True, null=True)
    course = models.CharField(max_length=250, blank=True, null=True)
    education_level = models.CharField(
        max_length=3,
        choices=(("UG", "Undergraduate"), ("PG", "Postgraduate"),("PhD","Doctor of Philosophy")),
        default="UG",
    )
    email =models.EmailField(blank=True,null=True)
    address=models.CharField(max_length=500,blank=True, null=True)
    status = models.CharField(
        max_length=2, choices=(("1", "Active"), ("2", "Inactiv  e")), default=1
    )
    delete_flag = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "List of Students"

    def __str__(self):
        return str(f"{self.code} - {self.first_name}")

    def name(self):
        return str(f"{self.first_name}")

class Staff(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('Professor', 'Professor'),
        ('Assistant Professor', 'Assistant Professor'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES)
    contact = models.CharField(max_length=20, blank=True, null=True)
    delete_flag = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Borrow(models.Model):
    student = models.ForeignKey(
        Students, on_delete=models.CASCADE, related_name="student_id_fk", null=True, blank=True
    )
    staffs = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="staff_id_fk", null=True, blank=True
    )

    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="book_id_fk")
    borrowing_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(
        max_length=2, choices=(("1", "Pending"), ("2", "Returned")), default=1
    )
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Borrowing Transactions"

    def __str__(self):
        return f"{self.student.code if self.student else self.staffs.first_name}"





