from .forms import UseRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework_jwt.settings import api_settings
from django.http import HttpResponse
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


def home(request):
    return render(request, 'users/home.html')

def home1(request):
    # profile=Profile.objects.all()
    # if request.method == 'POST':
    #     if request.is_ajax():
    #         image = request.FILES.get('Upload Image')
    #
    #         new_profile=Profile(image=image)
    #         new_profile.save()
    #
    # # return render_to_response('home.html', {'profile':profile}, )


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
                url = '/profile/'
                response = redirect(url)
                # Add token in header of url
                response['Token'] = jwt_token
                return response
                # r = requests.post(url, data=json.dumps(payload), headers=headers)
                # response = HttpResponseRedirect('/profile/')
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





