import datetime
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from lmsApp import forms, models
from .models import Students,SubCategory,Category,Books,Staff
import pandas as pd
from django.utils import timezone
from .forms import UploadFileForm




def context_data(request):
    fullpath = request.get_full_path()
    abs_uri = request.build_absolute_uri()
    abs_uri = abs_uri.split(fullpath)[0]
    context = {
        "system_host": abs_uri,
        "page_name": "",
        "page_title": "",
        "system_name": "பாவாணர் பைந்தமிழ் நூலகம் தமிழ்த்துறை பெரியார் கலைக்கல்லூரி,கடலூர்",
        "topbar": True,
        "footer": True,
    }

    return context


def userregister(request):
    context = context_data(request)
    context["topbar"] = False
    context["footer"] = False
    context["page_title"] = "User Registration"
    if request.user.is_authenticated:
        return redirect("home-page")
    return render(request, "register.html", context)


def save_register(request):
    resp = {"status": "failed", "msg": ""}
    if not request.method == "POST":
        resp["msg"] = "No data has been sent on this request"
    else:
        form = forms.SaveUser(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Account has been created succesfully")
            resp["status"] = "success"
        else:
            for field in form:
                for error in field.errors:
                    if resp["msg"] != "":
                        resp["msg"] += str("<br />")
                    resp["msg"] += str(f"[{field.name}] {error}.")

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def update_profile(request):
    context = context_data(request)
    context["page_title"] = "Update Profile"
    user = User.objects.get(id=request.user.id)
    if not request.method == "POST":
        form = forms.UpdateProfile(instance=user)
        context["form"] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile-page")
        else:
            context["form"] = form

    return render(request, "manage_profile.html", context)


@login_required
def update_password(request):
    context = context_data(request)
    context["page_title"] = "Update Password"
    if request.method == "POST":
        form = forms.UpdatePasswords(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your Account Password has been updated successfully"
            )
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context["form"] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context["form"] = form
    return render(request, "update_password.html", context)


# Create your views here.
def login_page(request):
    context = context_data(request)
    context["topbar"] = False
    context["footer"] = False
    context["page_name"] = "login"
    context["page_title"] = "Login"
    return render(request, "login.html", context)


def login_user(request):
    logout(request)
    resp = {"status": "failed", "msg": ""}
    username = ""
    password = ""
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp["status"] = "success"
            else:
                resp["msg"] = "Incorrect username or password"
        else:
            resp["msg"] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def home(request):
    context = context_data(request)
    context["page"] = "home"
    context["page_title"] = "Home"
    context["categories"] = (
        models.Category.objects.filter(delete_flag=0, status=1).all().count()
    )
    context["sub_categories"] = (
        models.SubCategory.objects.filter(delete_flag=0, status=1).all().count()
    )
    context["students"] = (
        models.Students.objects.filter(delete_flag=0, status=1).all().count()
    )
    context["books"] = (
        models.Books.objects.filter(delete_flag=0, status=1).all().count()
    )
    context["staffs"]= models.Staff.objects.all().count()
    context["pending"] = models.Borrow.objects.filter(status=1).all().count()
    context["pending"] = models.Borrow.objects.filter(status=1).all().count()
    context["transactions"] = models.Borrow.objects.all().count()

    return render(request, "home.html", context)


def logout_user(request):
    logout(request)
    return redirect("login-page")


@login_required
def profile(request):
    context = context_data(request)
    context["page"] = "profile"
    context["page_title"] = "Profile"
    return render(request, "profile.html", context)


@login_required
def users(request):
    context = context_data(request)
    context["page"] = "users"
    context["page_title"] = "User List"
    context["users"] = (
        User.objects.exclude(pk=request.user.pk).filter(is_superuser=False).all()
    )
    return render(request, "users.html", context)


@login_required
def save_user(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        if not post["id"] == "":
            user = User.objects.get(id=post["id"])
            form = forms.UpdateUser(request.POST, instance=user)
        else:
            form = forms.SaveUser(request.POST)

        if form.is_valid():
            form.save()
            if post["id"] == "":
                messages.success(request, "User has been saved successfully.")
            else:
                messages.success(request, "User has been updated successfully.")
            resp["status"] = "success"
        else:
            for field in form:
                for error in field.errors:
                    if not resp["msg"] == "":
                        resp["msg"] += str("<br/>")
                    resp["msg"] += str(f"[{field.name}] {error}")
    else:
        resp["msg"] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def manage_user(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_user"
    context["page_title"] = "Manage User"
    if pk is None:
        context["user"] = {}
    else:
        context["user"] = User.objects.get(id=pk)

    return render(request, "manage_user.html", context)


@login_required
def delete_user(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "User ID is invalid"
    else:
        try:
            User.objects.filter(pk=pk).delete()
            messages.success(request, "User has been deleted successfully.")
            resp["status"] = "success"
        except:
            resp["msg"] = "Deleting User Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def category(request):
    context = context_data(request)
    context["page"] = "category"
    context["page_title"] = "Category List"
    context["category"] = models.Category.objects.filter(delete_flag=0).all()
    return render(request, "category.html", context)


@login_required
def save_category(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        if not post["id"] == "":
            category = models.Category.objects.get(id=post["id"])
            form = forms.SaveCategory(request.POST, instance=category)
        else:
            form = forms.SaveCategory(request.POST)

        if form.is_valid():
            form.save()
            if post["id"] == "":
                messages.success(request, "Category has been saved successfully.")
            else:
                messages.success(request, "Category has been updated successfully.")
            resp["status"] = "success"
        else:
            for field in form:
                for error in field.errors:
                    if not resp["msg"] == "":
                        resp["msg"] += str("<br/>")
                    resp["msg"] += str(f"[{field.name}] {error}")
    else:
        resp["msg"] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_category(request, pk=None):
    context = context_data(request)
    context["page"] = "view_category"
    context["page_title"] = "View Category"
    if pk is None:
        context["category"] = {}
    else:
        context["category"] = models.Category.objects.get(id=pk)

    return render(request, "view_category.html", context)


@login_required
def manage_category(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_category"
    context["page_title"] = "Manage Category"
    if pk is None:
        context["category"] = {}
    else:
        context["category"] = models.Category.objects.get(id=pk)

    return render(request, "manage_category.html", context)


@login_required
def delete_category(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "Category ID is invalid"
    else:
        try:
            models.Category.objects.filter(pk=pk).delete()
            messages.success(request, "Category has been deleted successfully.")
            resp["status"] = "success"
        except:
            resp["msg"] = "Deleting Category Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def sub_category(request):
    context = context_data(request)
    context["page"] = "sub_category"
    context["page_title"] = "Sub Category List"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0).all()
    return render(request, "sub_category.html", context)


@login_required
def sub_cat_1(request):
    context = context_data(request)
    context["page"] = "sub_cat_1"
    context["page_title"] = "Sub Category List 1"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=1).all()
    return render(request, "sub_category.html", context)


@login_required
def sub_cat_2(request):
    context = context_data(request)
    context["page"] = "sub_cat_2"
    context["page_title"] = "Sub Category List 2"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=2).all()
    return render(request, "sub_category.html", context)

@login_required
def sub_cat_3(request):
    context = context_data(request)
    context["page"] = "sub_cat_3"
    context["page_title"] = "Sub Category List 3"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=3).all()
    return render(request, "sub_category.html", context)

@login_required
def sub_cat_4(request):
    context = context_data(request)
    context["page"] = "sub_cat_4"
    context["page_title"] = "Sub Category List 4"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=4).all()
    return render(request, "sub_category.html", context)

@login_required
def sub_cat_5(request):
    context = context_data(request)
    context["page"] = "sub_cat_5"
    context["page_title"] = "Sub Category List 5"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=5).all()
    return render(request, "sub_category.html", context)

@login_required
def sub_cat_6(request):
    context = context_data(request)
    context["page"] = "sub_cat_6"
    context["page_title"] = "Sub Category List 6"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=6).all()
    return render(request, "sub_category.html", context)

@login_required
def sub_cat_7(request):
    context = context_data(request)
    context["page"] = "sub_cat_7"
    context["page_title"] = "Sub Category List 7"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=7).all()
    return render(request, "sub_category.html", context)

@login_required
def sub_cat_8(request):
    context = context_data(request)
    context["page"] = "sub_cat_8"
    context["page_title"] = "Sub Category List 8"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=8).all()
    return render(request, "sub_category.html", context)

@login_required
def sub_cat_9(request):
    context = context_data(request)
    context["page"] = "sub_cat_9"
    context["page_title"] = "Sub Category List 9"
    context["sub_category"] = models.SubCategory.objects.filter(delete_flag=0, category=9).all()
    return render(request, "sub_category.html", context)



@login_required
def save_sub_category(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        if not post["id"] == "":
            sub_category = models.SubCategory.objects.get(id=post["id"])
            form = forms.SaveSubCategory(request.POST, instance=sub_category)
        else:
            form = forms.SaveSubCategory(request.POST)

        if form.is_valid():
            form.save()
            if post["id"] == "":
                messages.success(request, "Sub Category has been saved successfully.")
            else:
                messages.success(request, "Sub Category has been updated successfully.")
            resp["status"] = "success"
        else:
            for field in form:
                for error in field.errors:
                    if not resp["msg"] == "":
                        resp["msg"] += str("<br/>")
                    resp["msg"] += str(f"[{field.name}] {error}")
    else:
        resp["msg"] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_sub_category(request, pk=None):
    context = context_data(request)
    context["page"] = "view_sub_category"
    context["page_title"] = "View Sub Category"
    if pk is None:
        context["sub_category"] = {}
    else:
        context["sub_category"] = models.SubCategory.objects.get(id=pk)

    return render(request, "view_sub_category.html", context)


@login_required
def manage_sub_category(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_sub_category"
    context["page_title"] = "Manage Sub Category"
    if pk is None:
        context["sub_category"] = {}
    else:
        context["sub_category"] = models.SubCategory.objects.get(id=pk)
    context["categories"] = models.Category.objects.filter(
        delete_flag=0, status=1
    ).all()
    return render(request, "manage_sub_category.html", context)


@login_required
def delete_sub_category(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "Sub Category ID is invalid"
    else:
        try:
            models.SubCategory.objects.filter(pk=pk).delete()
            messages.success(request, "Sub Category has been deleted successfully.")
            resp["status"] = "success"
        except:
            resp["msg"] = "Deleting Sub Category Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


#@login_required
def books(request):
    context = context_data(request)
    context["page"] = "book"
    context["page_title"] = "Book List"
    context["books"] = models.Books.objects.filter(delete_flag=0)
    return render(request, "books.html", context)


@login_required
def save_book(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        book = None
        if post.get("id"):
            try:
                book = models.Books.objects.get(id=post["id"])
            except models.Books.DoesNotExist:
                resp["msg"] = "Book not found."
                return HttpResponse(json.dumps(resp), content_type="application/json")

        form = forms.SaveBook(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Book has been {} successfully.".format(
                    "updated" if post.get("id") else "saved"
                ),
            )
            resp["status"] = "success"
        else:
            resp["msg"] = "<br>".join(
                f"[{field}] {error}" for field, errors in form.errors.items() for error in errors
            )
    else:
        resp["msg"] = "No data sent in the request."

    return HttpResponse(json.dumps(resp), content_type="application/json")


#@login_required
def view_book(request, pk=None):
    context = context_data(request)
    context["page"] = "view_book"
    context["page_title"] = "View Book"
    try:
        context["book"] = models.Books.objects.get(id=pk, delete_flag=0)
    except models.Books.DoesNotExist:
        context["book"] = None
        messages.error(request, "Book not found.")
    return render(request, "view_book.html", context)


@login_required
def manage_book(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_book"
    context["page_title"] = "Manage Book"
    try:
        context["book"] = models.Books.objects.get(id=pk, delete_flag=0) if pk else None
    except models.Books.DoesNotExist:
        context["book"] = None
        messages.error(request, "Book not found.")

    context["sub_categories"] = models.SubCategory.objects.filter(
        delete_flag=0, status="1"
    )
    return render(request, "manage_book.html", context)


@login_required
def delete_book(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "Book ID is invalid."
    else:
        try:
            book = models.Books.objects.filter(pk=pk).first()
            if book:
                book.delete()
                # book.save()
                messages.success(request, "Book has been deleted successfully.")
                resp["status"] = "success"
            else:
                resp["msg"] = "Book not found."
        except Exception as e:
            resp["msg"] = f"Deleting Book Failed: {str(e)}"

    return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required
def students(request):
    context = context_data(request)
    context["page"] = "student"
    context["page_title"] = "Student List"
    context["students"] = models.Students.objects.filter(delete_flag=0).all()
    return render(request, "students.html", context)


@login_required
def save_student(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        if not post["id"] == "":
            student = models.Students.objects.get(id=post["id"])
            form = forms.SaveStudent(request.POST, instance=student)
        else:
            form = forms.SaveStudent(request.POST)

        if form.is_valid():
            form.save()
            if post["id"] == "":
                messages.success(request, "Student has been saved successfully.")
            else:
                messages.success(request, "Student has been updated successfully.")
            resp["status"] = "success"
        else:
            for field in form:
                for error in field.errors:
                    if not resp["msg"] == "":
                        resp["msg"] += str("<br/>")
                    resp["msg"] += str(f"[{field.name}] {error}")
    else:
        resp["msg"] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_student(request, pk=None):
    context = context_data(request)
    context["page"] = "view_student"
    context["page_title"] = "View Student"
    if pk is None:
        context["student"] = {}
    else:
        context["student"] = models.Students.objects.get(id=pk)

    return render(request, "view_student.html", context)


@login_required
def manage_student(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_student"
    context["page_title"] = "Manage Student"
    if pk is None:
        context["student"] = {}
    else:
        context["student"] = models.Students.objects.get(id=pk)
    context["sub_categories"] = models.SubCategory.objects.filter(
        delete_flag=0, status=1
    ).all()
    return render(request, "manage_student.html", context)


@login_required
def delete_student(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "Student ID is invalid"
    else:
        try:
            models.Students.objects.filter(pk=pk).delete()
            messages.success(request, "Student has been deleted successfully.")
            resp["status"] = "success"
        except:
            resp["msg"] = "Deleting Student Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def borrows(request):
    context = context_data(request)
    context["page"] = "borrow"
    context["page_title"] = "Borrowing Transaction List"
    context["borrows"] = models.Borrow.objects.order_by("status").all()
    return render(request, "borrows.html", context)


@login_required
def save_borrow(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        if not post["id"] == "":
            borrow = models.Borrow.objects.get(id=post["id"])
            form = forms.SaveBorrow(request.POST, instance=borrow)
        else:
            form = forms.SaveBorrow(request.POST)

        if form.is_valid():
            form.save()
            if post["id"] == "":
                messages.success(
                    request, "Borrowing Transaction has been saved successfully."
                )
            else:
                messages.success(
                    request, "Borrowing Transaction has been updated successfully."
                )
            resp["status"] = "success"
        else:
            for field in form:
                for error in field.errors:
                    if not resp["msg"] == "":
                        resp["msg"] += str("<br/>")
                    resp["msg"] += str(f"[{field.name}] {error}")
    else:
        resp["msg"] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def view_borrow(request, pk=None):
    context = context_data(request)
    context["page"] = "view_borrow"
    context["page_title"] = "View Transaction Details"
    if pk is None:
        context["borrow"] = {}
    else:
        context["borrow"] = models.Borrow.objects.get(id=pk)

    return render(request, "view_borrow.html", context)


@login_required
def manage_borrow(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_borrow"
    context["page_title"] = "Manage Transaction Details"
    if pk is None:
        context["borrow"] = {}
    else:
        context["borrow"] = models.Borrow.objects.get(id=pk)
    context["students"] = models.Students.objects.filter(delete_flag=0, status=1).all()
    context["books"] = models.Books.objects.filter(delete_flag=0, status=1).all()
    return render(request, "manage_borrow.html", context)


@login_required
def delete_borrow(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "Transaction ID is invalid"
    else:
        try:
            models.Borrow.objects.filter(pk=pk).delete()
            messages.success(request, "Transaction has been deleted successfully.")
            resp["status"] = "success"
        except:
            resp["msg"] = "Deleting Transaction Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")


def handle_uploaded_file(file):
    # Handle CSV or Excel file
    try:
        # Check the file extension
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file, engine="openpyxl")
        else:
            raise ValueError("Unsupported file format")

        # Process DataFrame
        return df
    except Exception as e:
        raise ValueError(f"Error processing file: {e}")


@login_required
def upload_file_view(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            upload_type = request.POST.get('upload_type')
            try:
                df =handle_uploaded_file(file)
                # print(df.shape[0])
                # df.replace(value=None, inplace=True)
                df = df.fillna("---")
                
                # Iterate over DataFrame and create or update model instances
                if upload_type == 'students':

                    if 'email' in df.columns:
                        df['email'] = df['email'].fillna('')
                    else:
                        df['email'] = ''  # Default to empty string if the column is missing

                    for index, row in df.iterrows():
                        # Extract year and convert to string (to match choices in the model)
                        year = str(row.get('year', '1')) if row.get('year') else None

                        # Use update_or_create with proper structure
                        Students.objects.update_or_create(
                            code=row['code'],  # Lookup field to check for an existing record
                            defaults={
                                'first_name': row['first_name'],
                                'gender': row.get('gender', 'Male'),  # Default to 'Male'
                                'contact': row['contact'],
                                'department': row.get('department', None),
                                'course': row.get('course', None),
                                'education_level': row.get('education_level', 'UG'),  # Default to 'UG'
                                'year': year,
                                'email': row.get('email', None),
                                'address': row.get('address', None),
                                'status': row.get('status', '1'),  # Default to 'Active'
                                'delete_flag': row.get('delete_flag', 0),  # Default to 0
                                'date_added': row.get('date_added', timezone.now()),  # Default to current time
                                'date_created': row.get('date_created', timezone.now()),  # Default to current time
                            }
                        )

                    messages.success(request, "Student data uploaded and added to the database successfully!")
                    return redirect('/students')



                elif upload_type == 'subcategory':

                    for index, row in df.iterrows():
                        category_instance = Category.objects.get(name=row['category'])
                        SubCategory.objects.update_or_create(
                            category=category_instance,
                            name=row['name'],
                            defaults={
                                "status": row.get("status", "1"),
                                "delete_flag": row.get("delete_flag", 0),
                            }
                        )
                    messages.success(request, "Subcategory data uploaded and added to the database successfully!")
                    return redirect('/category') 

                elif upload_type == 'books':
                    for index, row in df.iterrows():
                        try:
                            # Fetch the SubCategory instance based on name or ID
                            sub_category_name = row.get('sub_category').strip() if row.get('sub_category') else None

                            if not sub_category_name:
                                messages.error(request, f"SubCategory name is missing at row {index + 1}")
                                continue

                            sub_category_instance = SubCategory.objects.filter(name=sub_category_name).first()

                            if not sub_category_instance:
                                messages.error(request, f"SubCategory '{sub_category_name}' not found for row {index + 1}")
                                continue  # Skip this row if sub_category is not found


                            # Create or update the book record
                            Books.objects.update_or_create(
                                sub_category=sub_category_instance,
                                isbn=row['isbn'],
                                defaults={
                                    'title': row['title'],
                                    'author': row.get('author', ''),  
                                    'publisher': row.get('publisher', ''),
                                    'price':row.get('price',''),
                                    'berow':row.get('berow',''),
                                    'rack':row.get('rack','')                                  
                                    }
                            )

                        except Exception as e:
                            messages.error(request, f"An error occurred at row {index + 1}: {str(e)}")
                            continue  # Skip this row if another error occurs

                    messages.success(request, "Books data uploaded and added to the database successfully.")
                    return redirect('/books')

                elif upload_type == 'staff':
                    for index, row in df.iterrows():
                        Staff.objects.update_or_create(
                            name=row['name'],
                            defaults={
                                'education_level': row.get('education_level', 'Professor'),
                                'contact': row.get('contact', None),
                            }
                        )
                    messages.success(request, "Staff data uploaded and added to the database successfully!")
                    return redirect('/staffs')


   
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = UploadFileForm()

    return render(request, "upload_file.html", {"form": form})

@login_required
def staffs(request):
    context = context_data(request)
    context["page"] = "staff"
    context["page_title"] = "Staff List"
    context["staffs"] = models.Staff.objects.filter(delete_flag=0).all()
    return render(request, "staff.html", context)

@login_required
def save_staff(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        if not post["id"] == "":
            staff = models.Staff.objects.get(id=post["id"])
            form = forms.SaveStaff(request.POST, instance=staff)
        else:
            form = forms.SaveStaff(request.POST)

        if form.is_valid():
            form.save()
            if post["id"] == "":
                messages.success(request, "Staff has been saved successfully.")
            else:
                messages.success(request, "Staff has been updated successfully.")
            resp["status"] = "success"
        else:
            for field in form:
                for error in field.errors:
                    if not resp["msg"] == "":
                        resp["msg"] += str("<br/>")
                    resp["msg"] += str(f"[{field.name}] {error}")
    else:
        resp["msg"] = "There's no data sent on the request"

    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def view_staff(request, pk=None):
    context = context_data(request)
    context["page"] = "view_staff"
    context["page_title"] = "View Staff"
    if pk is None:
        context["staff"] = {}
    else:
        context["staff"] = models.Staff.objects.get(id=pk)

    return render(request, "view_staff.html", context)

@login_required
def manage_staff(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_staff"
    context["page_title"] = "Manage Staff"
    if pk is None:
        context["staff"] = {}
    else:
        context["staff"] = models.Staff.objects.get(id=pk)
    
    return render(request, "manage_staff.html", context)

@login_required
def delete_staff(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "Staff ID is invalid"
    else:
        try:
            models.Staff.objects.filter(pk=pk).delete()
            messages.success(request, "Staff has been deleted successfully.")
            resp["status"] = "success"
        except:
            resp["msg"] = "Deleting Staff Failed"

    return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required
def staff_borrows(request):
    context = context_data(request)
    context["page"] = "staff_borrow"
    context["page_title"] = "Staff Borrowing Transaction List"
    context["staff_borrows"] = models.StaffBorrow.objects.order_by("status").all()
    return render(request, "staff_borrows.html", context)


@login_required
def save_staff_borrow(request):
    resp = {"status": "failed", "msg": ""}
    if request.method == "POST":
        post = request.POST
        print(post)  # Debugging: Print POST data to verify input
        # if post.get("id"):
        if not post["id"] == "":
            staff_borrow = models.StaffBorrow.objects.get(id=post["id"])
            form = forms.SaveStaffForm(request.POST, instance=staff_borrow)
        else:
            form = forms.SaveStaffForm(request.POST)

        if form.is_valid():
            form.save()
            #if not post.get("id"):
            if post["id"] == "":
                messages.success(
                    request, "Staff Borrowing Transaction has been saved successfully."
                )
            else:
                messages.success(
                    request, "Staff Borrowing Transaction has been updated successfully."
                )
            resp["status"] = "success"
        else:
            # Log form errors for debugging
            print(form.errors.as_json())
            for field in form:
                for error in field.errors:
                    if resp["msg"]:
                        resp["msg"] += "<br/>"
                    resp["msg"] += f"[{field}] {error}"
    else:
        resp["msg"] = "No data sent with the request."

    return HttpResponse(json.dumps(resp), content_type="application/json")



@login_required
def view_staff_borrow(request, pk=None):
    context = context_data(request)
    context["page"] = "view_staff_borrow"
    context["page_title"] = "View Staff Transaction Details"
    if pk is None:
        context["borrow"] = {}
    else:
        context["borrow"] = models.StaffBorrow.objects.get(id=pk)

    return render(request, "view_staff_borrow.html", context)


@login_required
def manage_staff_borrow(request, pk=None):
    context = context_data(request)
    context["page"] = "manage_staff_borrow"
    context["page_title"] = "Manage Staff Transaction Details"
    if pk is None:
        context["staff_borrow"] = {}
    else:
        context["staff_borrow"] = models.StaffBorrow.objects.get(id=pk)
    context["staffs"] = models.Staff.objects.all()
    context["books"] = models.Books.objects.filter(delete_flag=0, status=1).all()
    return render(request, "manage_staff_borrow.html", context)


@login_required
def delete_staff_borrow(request, pk=None):
    resp = {"status": "failed", "msg": ""}
    if pk is None:
        resp["msg"] = "Transaction ID is invalid"
    else:
        try:
            models.StaffBorrow.objects.filter(pk=pk).delete()
            messages.success(request, "Staff Transaction has been deleted successfully.")
            resp["status"] = "success"
        except Exception as e:
            resp["msg"] = f"Deleting Transaction Failed: {str(e)}"

    return HttpResponse(json.dumps(resp), content_type="application/json")




                    





