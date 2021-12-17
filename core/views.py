from django.shortcuts import render, redirect
from core.forms import JoinForm, LoginForm, CreateGroupForm, JoinGroup, EditSettings, TaskEntryForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from core.models import UserProfile, Group, Task
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from feed.models import FeedItem
import requests
import json
from django.contrib import messages
from datetime import datetime, timedelta
from pytz import timezone
import requests
import json
import pytz


@login_required(login_url='/login/')
def home(request):
    context = {'groups': []}
    groups = Group.objects.all()
    for group in groups:
        if request.user in group.group_members.all():
            context['groups'].append(group)
            print("True")
    return render(request, "core/home.html",context)


def about(request):
    context = {"groups": []}
    groups = Group.objects.all()
    for group in groups:
        if request.user in group.group_members.all():
            context['groups'].append(group)
            print("True")
    return render(request, "core/about.html", context)


def join(request):
    if (request.method == "POST"):
        join_form = JoinForm(request.POST)
        if (join_form.is_valid()):
            user = join_form.save()
            UserProfile.objects.create(
                user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)
            user.set_password(user.password)
            user.save()
            return redirect("/")
        else:
            page_data = {"join_form": join_form}
            return render(request, 'core/join.html', page_data)
    else:
        join_form = JoinForm()
        page_data = {"join_form": join_form}
        return render(request, 'core/join.html', page_data)


def user_login(request):
    context = {"messages": "", "login_form": LoginForm}
    if (request.method == 'POST'):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    try:
                        UserProfile.objects.get(user=user)
                    except:
                        UserProfile.objects.create(
                            user=user, first_name=user.first_name, last_name=user.last_name, email=user.email)

                    login(request, user)
                    return redirect("/")
                else:
                    return HttpResponse("Your account is not active.")
            else:
                context["messages"] = "Invalid username or password"
                return render(request, 'core/login.html', context)
    else:
        return render(request, 'core/login.html', context)


@login_required(login_url='/login/')
def user_logout(request):
    logout(request)
    return redirect("/")


def creategroup(request):
    context = {"form": CreateGroupForm,
               "group_name": str, "group_id": str, "groups": []}
    if request.method == 'POST' and 'creategroup' in request.POST:
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            context["group_name"] = form.cleaned_data["group_name"]
            context["group_id"] = get_random_string(10)
            new_group = Group(
                group_name=context["group_name"], group_creator=request.user, group_id=context["group_id"])
            new_group.save()
            users = UserProfile.objects.filter(user=request.user).all()
            for user in users:
                new_group.group_members.add(user.user)
            new_group.save()
            new_group.save
            path = '/group/' + str(new_group.id)
            groups = Group.objects.all()
            for group in groups:
                if request.user in group.group_members.all():
                    context['groups'].append(group)
            return redirect(path)
        else:
            context["form"] = form
    elif request.method == 'GET' and 'cancel' in request.GET:
        groups = Group.objects.all()
        for group in groups:
            if request.user in group.group_members.all():
                context['groups'].append(group)
        return redirect('/')
    groups = Group.objects.all()
    for group in groups:
        if request.user in group.group_members.all():
            context['groups'].append(groups)
    return render(request, "core/creategroup.html", context)


def joingroup(request):
    context = {"form": JoinGroup, "groups": []}
    if request.method == 'POST' and 'joingroup' in request.POST:
        form = JoinGroup(request.POST)
        if form.is_valid():
            group_id = form.cleaned_data["group_id"]
            try:
                group_join = Group.objects.get(group_id=group_id)
                print(group_join)
            except:
                print("Group Doesnt Exist")
            group_join.save()
            if request.user in group_join.group_members.all():
                return render(request, "core/joingroup.html", context)
            else:
                group_join.group_members.add(request.user)
                groups = Group.objects.all()
                for group in groups:
                    if request.user in group.group_members.all():
                        context['groups'].append(group)
                        print("True")
                print("Member added to Group")
            group_join.save()
            path = '/group/' + str(group_join.id)
            groups = Group.objects.all()
            for group in groups:
                if request.user in group.group_members.all():
                    context['groups'].append(group)
            return redirect(path)
        else:
            context["form"] = form
    elif request.method == 'GET' and 'cancel' in request.GET:
        return redirect('/')
    groups = Group.objects.all()
    for group in groups:
        if request.user in group.group_members.all():
            context['groups'].append(group)
    return render(request, "core/joingroup.html", context)


def leavegroup(request, id):
    group = Group.objects.get(id=id)
    group.group_members.remove(request.user)
    return redirect('/')


def settings(request):
    try:
        user = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user = UserProfile.objects.create(
            user=request.user, first_name=request.user.first_name, last_name=request.user.last_name, email=request.user.email)

    form = EditSettings(instance=user)
    if request.method == 'POST' and 'update' in request.POST:
        form = EditSettings(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            comments = FeedItem.objects.filter(user=request.user)
            for comment in comments:
                comment.profile_picture = user.profile_picture
                comment.save()
    context = {'form': form, "groups": []}
    groups = Group.objects.all()
    for group in groups:
        if request.user in group.group_members.all():
            context['groups'].append(group)
            print("True")
    return render(request, 'core/settings.html', context)


def group(request, id):
    context = {"group_details": [], "groups": []}
    group1 = Group.objects.get(id=id)
    table_data = Task.objects.filter(group=group1)
    context["group_details"] = group1
    context["table_data"] = table_data
    groups = Group.objects.all()
    for group in groups:
        if request.user in group.group_members.all():
            context['groups'].append(group)
            print("True")
    return render(request, "core/group.html", context)

def add(request, id):
    if (request.method=="POST"):
        if ("add" in request.POST):
            add_form = TaskEntryForm(request.POST)
            group = Group.objects.get(id=id)
            if (add_form.is_valid()):
                task_name = add_form.cleaned_data["task_name"]
                date = add_form.cleaned_data["date"]
                group1 = group
                user = User.objects.get(id=request.user.id)
                Task(task_name=task_name, group=group1, user=user, date=date).save()
                return redirect("/group/"+str(id))
            else:
                context = {"form_data": add_form}
                return render(request, 'core/add_task.html', context)
        else:
            return redirect("/core/")
    else:
        context = {"form_data": TaskEntryForm()}
        return render(request, 'core/add_task.html', context)

def edit(request, id, id1, id2):
    user_id = id
    task_id = id1
    group_id = id2
    group = Group.objects.get(id=group_id)
    table_data = Task.objects.get(group=group, id=task_id)
    if(request.method == "GET"):
        form = TaskEntryForm(instance=table_data)
        context = { "form_data" : form , "table_data":table_data, "group":group}
        return render(request, 'core/edit_task.html', context)
    elif (request.method == "POST"):
        if ("edit" in request.POST):
            form = TaskEntryForm(request.POST)
            if (form.is_valid()):
                taskEntry = form.save(commit=False)
                taskEntry.group=group
                taskEntry.id = task_id
                taskEntry.owner=table_data.owner
                taskEntry.user=table_data.user
                taskEntry.status=table_data.status
                taskEntry.save()
                return redirect("/group/"+str(group_id))
            else:
                context = {"form_data": form, "table_data":table_data}
                return render(request, 'core/add_tasks.html', context)
        else:
            return redirect("/group/"+str(group_id))

def assign(request, id, id1, id2):
    user_id = id
    task_id = id1
    group_id = id2
    group = Group.objects.get(id=group_id)
    task = Task.objects.get(group=group, id=task_id)
    task.owner = User.objects.get(id=id)
    task.save() 
    return redirect("/group/"+str(group_id))

def toggle(request, id, id1, id2):
    user_id = id
    task_id = id1
    group_id = id2
    group = Group.objects.get(id=group_id)
    task = Task.objects.get(group=group, id=task_id)
    task.status = not task.status 
    task.save() 
    return redirect("/group/"+str(group_id))