from datetime import datetime
import datetime
from random import random
from secrets import choice
from sys import prefix
from unicodedata import category

from django import forms

from django.contrib.auth.forms import (
    PasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from lmsApp import models
from numpy import require
from .models import Staff,StaffBorrow,Books


class UploadFileForm(forms.Form):
    file = forms.FileField(label="Upload CSV or Excel File")


class SaveUser(UserCreationForm):
    username = forms.CharField(
        max_length=250, help_text="The Username field is required."
    )
    email = forms.EmailField(max_length=250, help_text="The Email field is required.")
    first_name = forms.CharField(
        max_length=250, help_text="The First Name field is required."
    )
    last_name = forms.CharField(
        max_length=250, help_text="The Last Name field is required."
    )
    password1 = forms.CharField(max_length=250)
    password2 = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )


class UpdateProfile(UserChangeForm):
    username = forms.CharField(
        max_length=250, help_text="The Username field is required."
    )
    email = forms.EmailField(max_length=250, help_text="The Email field is required.")
    first_name = forms.CharField(
        max_length=250, help_text="The First Name field is required."
    )
    last_name = forms.CharField(
        max_length=250, help_text="The Last Name field is required."
    )
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name")

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data["current_password"]):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.exclude(id=self.cleaned_data["id"]).get(email=email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.exclude(id=self.cleaned_data["id"]).get(
                username=username
            )
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")


class UpdateUser(UserChangeForm):
    username = forms.CharField(
        max_length=250, help_text="The Username field is required."
    )
    email = forms.EmailField(max_length=250, help_text="The Email field is required.")
    first_name = forms.CharField(
        max_length=250, help_text="The First Name field is required."
    )
    last_name = forms.CharField(
        max_length=250, help_text="The Last Name field is required."
    )

    class Meta:
        model = User
        fields = ("email", "username", "first_name", "last_name")

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            user = User.objects.exclude(id=self.cleaned_data["id"]).get(email=email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            user = User.objects.exclude(id=self.cleaned_data["id"]).get(
                username=username
            )
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")


class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-sm rounded-0"}
        ),
        label="Old Password",
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-sm rounded-0"}
        ),
        label="New Password",
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control form-control-sm rounded-0"}
        ),
        label="Confirm New Password",
    )

    class Meta:
        model = User
        fields = ("old_password", "new_password1", "new_password2")


class SaveCategory(forms.ModelForm):
    name = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Category
        fields = (
            "name",
            "status",
        )

    def clean_name(self):
        id = self.data["id"] if (self.data["id"]).isnumeric() else 0
        name = self.cleaned_data["name"]
        try:
            if id > 0:
                category = models.Category.objects.exclude(id=id).get(
                    name=name, delete_flag=0
                )
            else:
                category = models.Category.objects.get(name=name, delete_flag=0)
        except:
            return name
        raise forms.ValidationError("Category Name already exists.")


class SaveSubCategory(forms.ModelForm):
    category = forms.CharField(max_length=250)
    name = forms.CharField(max_length=250)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.SubCategory
        fields = (
            "category",
            "name",
            "status",
        )

    def clean_category(self):
        cid = int(self.data["category"]) if (self.data["category"]).isnumeric() else 0
        try:
            category = models.Category.objects.get(id=cid)
            return category
        except:
            raise forms.ValidationError("Invalid Category.")

    def clean_name(self):
        id = int(self.data["id"]) if (self.data["id"]).isnumeric() else 0
        cid = int(self.data["category"]) if (self.data["category"]).isnumeric() else 0
        name = self.cleaned_data["name"]
        try:
            category = models.Category.objects.get(id=cid)
            if id > 0:
                sub_category = models.SubCategory.objects.exclude(id=id).get(
                    name=name, delete_flag=0, category=category
                )
            else:
                sub_category = models.SubCategory.objects.get(
                    name=name, delete_flag=0, category=category
                )
        except:
            return name
        raise forms.ValidationError(
            "Sub-Category Name already exists on the selected Category."
        )

class SaveBook(forms.ModelForm):
    sub_category = forms.CharField(max_length=250)
    isbn = forms.CharField(max_length=250)
    title = forms.CharField(max_length=250)
    author = forms.Textarea()
    publisher = forms.CharField(widget=forms.Textarea(), required=False)
    price = forms.CharField(max_length=50, required=False)
    berow = forms.CharField(max_length=50, required=False)
    rack = forms.CharField(max_length=50, required=False)
    date_published = forms.DateField(required=False)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Books
        fields = (
            "isbn",
            "sub_category",
            "title",
            "author",
            "publisher",
            "price",
            "berow",
            "rack",
            "date_published",
            "status",
        )

    def clean_sub_category(self):
        scid = (
            int(self.data["sub_category"])
            if (self.data["sub_category"]).isnumeric()
            else 0
        )
        try:
            sub_category = models.SubCategory.objects.get(id=scid)
            return sub_category
        except:
            raise forms.ValidationError("Invalid Sub Category.")

    def clean_isbn(self):
        id = int(self.data["id"]) if (self.data["id"]).isnumeric() else 0
        isbn = self.cleaned_data["isbn"]
        try:
            if id > 0:
                book = models.Books.objects.exclude(id=id).get(isbn=isbn, delete_flag=0)
            else:
                book = models.Books.objects.get(isbn=isbn, delete_flag=0)
        except:
            return isbn
        raise forms.ValidationError("ISBN already exists on the Database.")


class SaveStudent(forms.ModelForm):
    code = forms.CharField(max_length=250)
    first_name = forms.CharField(max_length=250)
    gender = forms.CharField(max_length=250)
    contact = forms.CharField(max_length=250)
    department = forms.CharField(max_length=250)
    course = forms.CharField(max_length=250,required=False)
    education_level = forms.CharField(max_length=5)
    year = forms.CharField(max_length=250,required=False)
    email = forms.EmailField(required=False)
    address = forms.CharField(max_length=500, required=False)
    status = forms.CharField(max_length=2)

    class Meta:
        model = models.Students
        fields = (
            "code",
            "first_name",
            "gender",
            "contact",
            "department",
            "course",
            "education_level",
            "year",
            "email",
            "address",
            "status",
        )

    def clean_code(self):
        id = int(self.data.get("id", 0)) if self.data.get("id", "0").isnumeric() else 0
        code = self.cleaned_data["code"]
        try:
            if id > 0:
                student = models.Students.objects.exclude(id=id).get(code=code, delete_flag=0)
            else:
                student = models.Students.objects.get(code=code, delete_flag=0)
        except:
            return code
        raise forms.ValidationError(
            "Student Student Id already exists on the Database."
        )


class SaveBorrow(forms.ModelForm):
    student = forms.CharField(max_length=250,required=False)
    book = forms.CharField(max_length=250)
    borrowing_date = forms.DateField()
    return_date = forms.DateField()
    status = forms.CharField(max_length=2)
    # staff = forms.CharField(max_length=250,required=False)

    class Meta:
        model = models.Borrow
        fields = (
            "student",
            "book",
            "borrowing_date",
            "return_date",
            "status",
            # "staff",
        )

    def clean_student(self):
        student = int(self.data["student"]) if (self.data["student"]).isnumeric() else 0
        try:
            student = models.Students.objects.get(id=student)
            return student
        except:
            raise forms.ValidationError("Invalid student.")
    
    def clean_staff(self):
        staff = int(self.data["staff"]) if (self.data["staff"]).isnumeric() else 0
        try:
            staff = models.Staff.objects.get(id=staff)
            return staff
        except:
            raise forms.ValidationError("Invalid student.")

    def clean_book(self):
        book = int(self.data["book"]) if (self.data["book"]).isnumeric() else 0
        try:
            book = models.Books.objects.get(id=book)
            return book
        except:
            raise forms.ValidationError("Invalid Book.")



class SaveStaff(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'education_level', 'contact']


class SaveStaffBorrow(forms.ModelForm):
    staff = forms.CharField(max_length=250, required=True)  # Accept staff ID or name
    book = forms.CharField(max_length=250, required=True)   # Accept book ID or title

    class Meta:
        model = StaffBorrow
        fields = ("staffs", "book", "borrowing_date", "return_date", "status")

    def clean_staff(self):
        staff = self.cleaned_data.get("staff")
        if staff:
            try:
                if staff.isnumeric():
                    return Staff.objects.get(id=int(staff))
                else:
                    return Staff.objects.get(name__iexact=staff)
            except Staff.DoesNotExist:
                raise forms.ValidationError("Staff not found.")
        raise forms.ValidationError("Staff is required.")

    def clean_book(self):
        book = self.cleaned_data.get("book")
        if book:
            try:
                if book.isnumeric():
                    return Books.objects.get(id=int(book))
                else:
                    return Books.objects.get(title__iexact=book)
            except Books.DoesNotExist:
                raise forms.ValidationError("Book not found.")
        raise forms.ValidationError("Book is required.")

    def clean(self):
        cleaned_data = super().clean()
        borrowing_date = cleaned_data.get("borrowing_date")
        return_date = cleaned_data.get("return_date")

        if borrowing_date and return_date and return_date < borrowing_date:
            raise forms.ValidationError(
                "The return date cannot be earlier than the borrowing date."
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.staffs = self.cleaned_data.get("staff")
        instance.book = self.cleaned_data.get("book")
        instance.borrowing_date = self.cleaned_data.get("borrowing_date")
        instance.return_date = self.cleaned_data.get("return_date")
        if commit:
            instance.save()
        return instance
