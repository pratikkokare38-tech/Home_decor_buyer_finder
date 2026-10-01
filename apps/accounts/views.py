from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .forms import SellerRegistrationForm, SellerProfileForm
from .models import SellerProfile
from .serializers import UserSerializer, RegisterSerializer


# ------------------------------------------------------------------
# Page Views (Django HTML Templates)
# ------------------------------------------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('search_page')

    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            profile, _ = SellerProfile.objects.get_or_create(user=user)
            profile.company_name = form.cleaned_data['company_name']
            profile.from_name = form.cleaned_data['from_name']
            profile.from_email = form.cleaned_data['email']
            profile.postal_address = form.cleaned_data['postal_address']
            profile.save()

            auth_login(request, user)
            messages.success(request, f"Welcome to DecorFinder USA, {user.username}!")
            return redirect('search_page')
    else:
        form = SellerRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('search_page')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next') or 'search_page'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def profile_view(request):
    profile, _ = SellerProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Seller profile updated successfully.")
            return redirect('profile_page')
    else:
        form = SellerProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


# ------------------------------------------------------------------
# DRF REST API Views
# ------------------------------------------------------------------

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            auth_login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response({'error': {'code': 'VALIDATION_ERROR', 'message': serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            return Response(UserSerializer(user).data)
        return Response({'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Invalid username or password'}}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        auth_logout(request)
        return Response({'message': 'Logged out successfully'})


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
