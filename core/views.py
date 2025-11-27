from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from .models import StudyMaterial, StudyGroup, GroupJoinRequest, UserProfile
from .forms import StudyMaterialForm, StudyGroupForm
from django.contrib.auth.models import User

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    total_materials = StudyMaterial.objects.count()
    total_groups = StudyGroup.objects.count()
    user_materials = StudyMaterial.objects.filter(uploader=request.user).count()
    top_users = User.objects.annotate(
        material_count=Count('uploaded_materials')
    ).order_by('-material_count')[:5]

    context = {
        'total_materials': total_materials,
        'total_groups': total_groups,
        'user_materials': user_materials,
        'top_users': top_users,
    }
    return render(request, 'core/home.html', context)

@login_required
def study_materials_view(request):
    materials = StudyMaterial.objects.all()
    return render(request, 'core/study_materials.html', {'materials': materials})

@login_required
def upload_material_view(request):
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploader = request.user
            material.save()

            # Increase uploader score
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.score += 10
            profile.save()

            messages.success(request, 'Material uploaded successfully!')
            return redirect('study_materials')
    else:
        form = StudyMaterialForm()
    return render(request, 'core/upload_material.html', {'form': form})

@login_required
def study_groups_view(request):
    groups = StudyGroup.objects.all()
    user_groups = request.user.study_groups.all()
    return render(request, 'core/study_groups.html', {'groups': groups, 'user_groups': user_groups})

@login_required
def create_group_view(request):
    if request.method == 'POST':
        form = StudyGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            group.members.add(request.user)
            messages.success(request, 'Study group created successfully!')
            return redirect('study_groups')
    else:
        form = StudyGroupForm()
    return render(request, 'core/create_group.html', {'form': form})

@login_required
def group_detail_view(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    is_member = request.user in group.members.all()
    is_creator = request.user == group.creator

    # Check if user has pending request
    has_pending_request = GroupJoinRequest.objects.filter(
        group=group, user=request.user, status='pending'
    ).exists()

    # Get pending requests if user is creator
    pending_requests = []
    if is_creator:
        pending_requests = GroupJoinRequest.objects.filter(group=group, status='pending')

    context = {
        'group': group,
        'is_member': is_member,
        'is_creator': is_creator,
        'has_pending_request': has_pending_request,
        'pending_requests': pending_requests,
    }
    return render(request, 'core/group_detail.html', context)

@login_required
def join_group_view(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)

    # Create join request
    request_obj, created = GroupJoinRequest.objects.get_or_create(
        group=group, user=request.user, defaults={'status': 'pending'}
    )

    if created:
        messages.success(request, 'Join request sent!')
    else:
        messages.info(request, 'You already have a pending request.')

    return redirect('group_detail', pk=pk)

@login_required
def approve_request_view(request, pk):
    join_request = get_object_or_404(GroupJoinRequest, pk=pk)

    if request.user == join_request.group.creator:
        join_request.status = 'approved'
        join_request.save()
        join_request.group.members.add(join_request.user)
        messages.success(request, f'{join_request.user.username} has been added to the group!')

    return redirect('group_detail', pk=join_request.group.pk)

@login_required
def reject_request_view(request, pk):
    join_request = get_object_or_404(GroupJoinRequest, pk=pk)

    if request.user == join_request.group.creator:
        join_request.status = 'rejected'
        join_request.save()
        messages.info(request, 'Request rejected.')

    return redirect('group_detail', pk=join_request.group.pk)

@login_required
def leaderboard_view(request):
    users = User.objects.annotate(
        material_count=Count('uploaded_materials')
    ).order_by('-material_count')

    # Also consider profile scores
    profiles = UserProfile.objects.select_related('user').order_by('-score')

    context = {
        'users': users,
        'profiles': profiles,
    }
    return render(request, 'core/leaderboard.html', context)

@login_required
def profile_view(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile, created = UserProfile.objects.get_or_create(user=user)
    materials = StudyMaterial.objects.filter(uploader=user)

    context = {
        'profile_user': user,
        'profile': profile,
        'materials': materials,
    }
    return render(request, 'core/profile.html', context)

@login_required
def who_uploaded_view(request):
    materials = StudyMaterial.objects.select_related('uploader').all()
    return render(request, 'core/who_uploaded.html', {'materials': materials})
