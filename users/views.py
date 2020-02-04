from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserForm, UserRegisterForm, PatientProfileForm, DoctorProfileForm, UserTermAgree


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        term_form = UserTermAgree(request.POST)
        if form.is_valid() and term_form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
        term_form = UserTermAgree()
    context = {
        'form': form,
        'term_form': term_form,
    }
    return render(request, 'users/register.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        if request.user.is_patient:
            profile_form = PatientProfileForm(request.POST, instance=request.user.patient_profile)
        elif request.user.is_doctor:
            profile_form = DoctorProfileForm(request.POST, request.FILES, instance=request.user.doctor_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your profile has been updated')
            return redirect('profile')

    else:
        user_form = UserForm(instance=request.user)
        if request.user.is_patient:
            profile_form = PatientProfileForm(instance=request.user.patient_profile)
        elif request.user.is_doctor:
            profile_form = DoctorProfileForm(instance=request.user.doctor_profile)

    return render(request, 'users/profile.html', {
        'u_form': user_form,
        'p_form': profile_form,
    })


def home(request):
    context = {
        'title': 'Homepage',
    }
    return render(request, 'users/home.html')
