

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, message
from .forms import RoomForm, UserForm

# rooms = [
#     {'id':'1', 'name':'lets code'},
#     {'id':'2', 'name':'developer main'},
#     {'id':'3', 'name':'lets code'},
# ]
# Create your views here.
def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
     
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # Logic moved INSIDE the POST block
        user = authenticate(request, username=username, password=password)
        try:
            user = User.objects.get(username=username)
        except: messages.error(request, 'User does not exist')
   

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
    context = {'page':page}
    return render(request, 'base/login_register.html', context)



def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    # page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registeration')

    return render(request, 'base/login_register.html', {'form':form})

@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains = q) |
            Q(descrription__icontains = q)
            )

    topics =Topic.objects.all()
    # When rooms starts growing , learn how to filter topics by different things
    room_count = rooms.count()
    room_messages = message.objects.filter(Q(room__name__icontains = q))

    context = {'rooms':rooms, 'topics':topics,'room_count':room_count,'room_messages':room_messages }
    
    return render(request, 'base/home.html', context)

def room(request,pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == pk:
    #         room = i
    room = Room.objects.get(id=pk)

    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        new_message = message.objects.create(
            user = request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('roomUrl', pk=room.id)

    context = {'room':room, 'room_messages': room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)

def profile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user,'rooms':rooms, 'topics':topics, 'room_messages':room_messages}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # print(request.POST)
        # form=RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            descrription = request.POST.get('descrription')
        )
        return redirect('home')

    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def UpdateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.descrription = request.POST.get('descrription')
        room.save()

        
        # print(request.POST)
        # form=RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')

    context = {'form':form, 'topics':topics, 'room':room }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def DeleteRoom(request,pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def DeleteMessage(request,pk):
    delMessage = message.objects.get(id=pk)
    if request.user != delMessage.user:
        return HttpResponse('You are not allowed here')
    
    if request.method == 'POST':
        delMessage.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':delMessage})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form':form})