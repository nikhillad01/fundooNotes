from django.views.generic import UpdateView

from .forms import UseRegistrationForm, UserUpdateForm, ProfileUpdateForm, CreateNoteForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework_jwt.settings import api_settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .models import Profile
import json
from django_ajax.decorators import ajax


def home(request):
    return render(request, 'users/aaa.html')

def home1(request):

    return render(request, 'users/crop_profile_pic.html')



def register(request):
    """
    This method is to register the new user
    :param request:take Http request
    :return:HTTP response with message
    """
    # HTTP Method POST. That means the form was submitted by a user
    if request.method == 'POST':
        # A form bound to the POST data
        form = UseRegistrationForm(request.POST)
        # IF all validation rules pass
        if form.is_valid():
            user = form.save()
            user.is_active = False
            # save user
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('users/acc_active_email.html', {
                'user': user, 'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })

            mail_subject = 'Activate your account.'
            to_email = form.cleaned_data.get('email')
            # create email instance with mail subject ,message, email id of receiver
            email = EmailMessage(mail_subject, message, to=[to_email])
            # send mail
            email.send()
            messages.success(request, f'Please confirm your email address to complete the registration.')
            # return HttpResponse('Please confirm your email address to complete the registration.')
            return redirect('register')

    else:
        # An unbound form
        form = UseRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """
     This method is to create profile for user
    :param request:take Http request
    :return: redirect to profile page

    """
    photos = Profile.objects.all()
    # If HTTP Method POST. That means the form was submitted by a user
    if request.method == 'POST':
        # A form bound to the POST data and create instance of form by user request
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES, instance=request.user.profile)
        # If all validation rules pass
        if u_form.is_valid() and p_form.is_valid():
            # save form
            u_form.save()
            p_form.save()
            messages.success(request, f'Your Account has been updated')
            return redirect('profile')
    else:
        # An unbound form
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,'photos': photos
    }
    return render(request, 'users/profile.html', context)


def get_jwt_token(user):
    """
    This method is to generate jwt token
    :param user: current logged in user
    :return: encoded jwt token
    """

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    # create payload for authorised
    payload = jwt_payload_handler(user)
    print(payload)
    print(jwt_encode_handler(payload))
    # return encoded payload
    return jwt_encode_handler(payload)


def user_login(request):
    """
    This method allow authorised user to login
    :param request: Http request
    :return: response with jwt token
    """
    # If HTTP Method POST. That means the form was submitted by a user
    if request.method == 'POST':
        # get username and password from submitted form
        username = request.POST.get('username')
        password = request.POST.get('password')
        # check for authentication
        user = authenticate(username=username, password=password)
        # user is valid
        print('usr', user,username, password)
        if user:
            if user.is_active:
                login(request,user)
                # generate token for user
                jwt_token = get_jwt_token(user)
                url = '/readallnotes/'
                response = redirect(url)
                # Add token in header of url
                response['Token'] = jwt_token
                return response
                # r = requests.post(url, data=json.dumps(payload), headers=headers)
                # response = HttpResponseRedirect(' /profile/')
                # return response
                # return HttpResponse(jwt_token)

            else:
                return HttpResponse(messages.success(request,"Your account was inactive."))
        else:
            messages.success(request, f'Invalid username or password')
            # print("Someone tried to login and failed.")
            # print("They used username: {} and password: {}".format(username,password))
            # return HttpResponse("Invalid username and password")
            return redirect('login')
    else:
        return render(request, 'users/login.html', {})


def activate(request, uidb64, token):
    """
    :param request: Http request
    :param uidb64: user's id encoded in base 64
    :param token: generated token for user
    :return: http response with text message
    """
    try:
        # takes user id and generates the base64 code
        uid = force_text(urlsafe_base64_decode(uidb64))
        # get user for given uid
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        # check user is not null and has a token
    if user is not None and account_activation_token.check_token(user, token):
        # make user active
        user.is_active = True
        # save user
        user.save()
        # make request for login
        login(request, user)
        messages.success(request, f'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
        # return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.success(request, f'Activation link is invalid!.')
        # return HttpResponse('Activation link is invalid!')
        return redirect('login')


from .serializers import NoteSerializer
from .models import Notes,Labels
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# API to create note
class addnote(APIView):
    def post(self, request, format=None):
        serializer = NoteSerializer(data=request.data)
        # check serialized data is valid or not
        if serializer.is_valid():
            # if valid then save it
            serializer.save()
            # in response return data in json format
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else return error msg in response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API to  update the note
class updatenote(APIView):
    def put(self, request, pk, format=None):
        # get all the notes of given requested id(pk)
        note = Notes.objects.get(pk=pk)
        # requested data is serialized and store it in serializer variable
        serializer = NoteSerializer(note, data=request.data)
        # check serialized data is valid or not
        if serializer.is_valid():
            # if valid then save it
            serializer.save()
            # in response return data in json format
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else return error msg in response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API to delete note
class deletenote(APIView):
    def delete(self, request, pk, format=None):
        # delete note of given id
        note = Notes.objects.get(pk=pk)
        # delete note
        note.delete()
        # return in response no content
        return Response(status=status.HTTP_204_NO_CONTENT)


# read all notes
class getnotes(APIView):
    def get(self, request, uid, format=None):
        # get note filtered by id
        note_list = Notes.objects.filter(id=uid)
        # requested notes objects are serialized and store it in serializer variable
        serializer = NoteSerializer(note_list, many=True)
        # return all data in json format
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from django.shortcuts import render
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse


def index(request):
    notes = Notes.objects.all()[:5]
    return render(request, 'notes/index.html', {'notes': notes})


def lazy_load_notes(request):
    page = request.POST.get('page')
    notes = Notes.objects.all()
    print(notes)
    # use Django's pagination
    # https://docs.djangoproject.com/en/dev/topics/pagination/
    results_per_page = 5
    paginator = Paginator(notes, results_per_page)
    try:
        notes = paginator.page(page)
    except PageNotAnInteger:
        notes = paginator.page(2)
    except EmptyPage:
        notes = paginator.page(paginator.num_pages)

    # build a html posts list with the paginated posts
    notes_html = loader.render_to_string('notes/notes_list.html', {'notes': notes})

    # package output data and return it as a JSON object
    output_data = {'notes_html': notes_html, 'has_next': notes.has_next()}
    return JsonResponse(output_data)
    # return render(request, 'notes/notes_list.html', {{'notes': notes}})

from rest_framework.filters import OrderingFilter
# this method is to create new note
def createnote(request):
    if request.method == 'POST':
        # get username and password from submitted form

        title = request.POST.get('title')
        description = request.POST.get('description')
        color= request.POST.get('color')
        notes=Notes(title=title,description=description,color=color)
        # title and description should not be null
        if title !="" and description!="":
            # save it to database
            notes.save()
            return redirect('readallnotes')
        # order notes according to it's creation time
        allnotes=Notes.objects.all().order_by('-created_time')
        print(allnotes)
        context={#'title':title,
                 #'description':description
                 'allnotes':allnotes}
    return render(request, 'notes/create-note.html',context)

# this method is to delete the note
def deleteenote(request, pk):
    if request.method == 'GET':
        # get the note with requested id
        note = Notes.objects.get(pk=pk)
        if note.trash == False:
           note.trash = True
           note.save()

        else:
            note.is_deleted=True
            # delete note
            note.delete()

        return redirect('readallnotes')
    allnotes = Notes.objects.all().order_by('-created_time')
    context = {  # 'title':title,# 'description':description
    'allnotes': allnotes}

    return render(request, 'notes/create-note.html', context)

# this method is to update note with given id
def updatenotes(request, pk):
    if request.method == 'POST':
        # get note with requested id
        note = Notes.objects.get(pk=pk)
        print(note)
        # set new tile to requested id
        note.title = request.POST.get('modal-text')
        print(note.title)
        # set new description to requested id
        note.description = request.POST.get('modal-textarea')
        if note.title !="" or note.description!="":
            # save note
            note.save()
            return redirect('readallnotes')
        allnotes = Notes.objects.all().order_by('-created_time')
        context = {  # 'title':title,
        # 'description':description
        'allnotes': allnotes}
    return render(request, 'notes/create-note.html', context)

# this method is to make copy of note
def copynote(request, pk):
    if request.method == 'GET':
        # get note with given id
        note = Notes.objects.get(pk=pk)
        # set title of requested id to new note
        title = note.title
        # set description of requested id to new note
        description = note.description
        # create ojbect of new copy
        newcopy = Notes(title=title, description=description)
        # save newcopy to database
        newcopy.save()
        allnotes = Notes.objects.all().order_by('-created_time')
        print(allnotes)
        context = {  # 'title':title,
            # 'description':description
            'allnotes': allnotes}
    return render(request, 'notes/create-note.html', context)

# method to set color
@ajax
def setcolor(request):
    if request.method == 'POST':

        color = request.POST.get('color')
        id = request.POST.get('id')
        note = Notes.objects.get(id=id)
        note.color= request.POST.get('color')
        print(color)
        print(id)
        note.save()
        return redirect('readallnotes')

    allnotes = Notes.objects.all().order_by('-created_time')
    print(allnotes)
    context = {  # 'title':title,
        # 'description':description
        'allnotes': allnotes}
    return render(request, 'notes/readallnotes.html', context)

@ajax
def isarchive(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        note = Notes.objects.get(id=id)

        if note.is_archived == False:
           note.is_archived = True
           note.save()
        else:
            note.is_archived = False
            note.save()

        allnotes = Notes.objects.all().order_by('-created_time')
        print(allnotes)
        context = {  # 'title':title,
            # 'description':description
            'allnotes': allnotes}
    return render(request, 'notes/create-note.html', context)


def showarchive(request):
        allnotes = Notes.objects.all().order_by('-created_time')
        print(allnotes)
        context = {  # 'title':title,
            # 'description':description
            'allnotes': allnotes}
        return render(request, 'notes/archived.html', context)


def readallnotes(request):
    allnotes = Notes.objects.all().order_by('-created_time')
    all_labels = Labels.objects.all().order_by('-created_time')
    print(allnotes)
    context = {  # 'title':title,
        # 'description':description
        'allnotes': allnotes,'all_labels':all_labels}
    return render(request, 'notes/create-note.html', context)

def showtrash(request):
    allnotes = Notes.objects.all().order_by('-created_time')
    print(allnotes)
    context = {  # 'title':title,
        # 'description':description
        'allnotes': allnotes}
    return render(request, 'notes/istrash.html', context)

def restore(request,pk):
    if request.method == 'GET':
        # get the note with requested id
        note = Notes.objects.get(pk=pk)
        if note.trash == True:
            note.trash = False
            note.save()

        return redirect('readallnotes')

    allnotes = Notes.objects.all().order_by('-created_time')
    print(allnotes)
    context = {  # 'title':title,
        # 'description':description
        'allnotes': allnotes}
    return render(request, 'notes/create-note.html', context)
@ajax
def ispinned(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        note = Notes.objects.get(id=id)
        if note.is_pinned  == False:
            note.is_pinned = True
            note.save()
        else:
            note.is_pinned = False
            note.save()
        return redirect('readallnotes')
    allnotes = Notes.objects.all().order_by('-created_time')
    print(allnotes)
    context = {  # 'title':title,
        # 'description':description
        'allnotes': allnotes}
    return render(request, 'notes/create-note.html', context)


def create_label(request):
    if request.method == 'POST':
        # label = Labels.objects.get(pk=pk)
        # get note id and label name from submitted form
        label_name = request.POST.get('label')
        print(label_name)
        label = Labels(label_name=label_name)
        # title and description should not be null
        if label_name!= "":
            # save it to database
            label.save()
            return redirect('readallnotes')
        # order notes according to it's creation time
        all_labels = Labels.objects.all().order_by('-created_time')

        context = {  # 'title':title,
            # 'description':description
            'all_labels': all_labels}
    return render(request, 'notes/base.html', context)


# method to delete label
def delete_label(request,pk):
    if request.method == 'GET':
        # get label id
        label = Labels.objects.get(pk=pk)
        # delete label
        label.delete()
        return redirect('readallnotes')
        # order notes according to it's creation time
        allnotes = Notes.objects.all().order_by('-created_time')
        print(allnotes)
        context = {  # 'title':title,
            # 'description':description
            'allnotes': allnotes}
    return render(request, 'notes/create-note.html', context)

# method to update label
def update_label(request, pk):
    if request.method == 'POST':
        # get note with requested id
        label = Labels.objects.get(pk=pk)
        # set new tile to requested id
        label.label_name = request.POST.get('label_name')
        print(label.label_name)
        # set new description to requested id

        if label.label_name !="":
            # save note
            label.save()
            return redirect('readallnotes')
        allnotes = Notes.objects.all().order_by('-created_time')
        context = {  # 'title':title,
        # 'description':description
        'allnotes': allnotes}
    return render(request, 'notes/create-note.html', context)


def addLabelOnNote(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        label = Labels.objects.get(id=id)
        label.note_id = request.POST.get('note_id')
        print(label.note_id)
        label.save()

        return redirect('readallnotes')
    return render(request, 'notes/create-note.html')