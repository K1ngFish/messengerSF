from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse

from .models import Message, ChatGroup
from users.models import CustomUser
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    data = json.loads(request.body)
    author_id = data.get('author_id')
    content = data.get('content')
    receiver_id = data.get('receiver_id')

    author = get_object_or_404(CustomUser, id=author_id)
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    chat_group = ChatGroup.objects.filter(members=author).filter(members=receiver).first()
    if chat_group is None:
        chat_group = ChatGroup.objects.create()
        chat_group.members.add(author, receiver)

    is_group_chat = True if chat_group.name else False

    message = Message.objects.create(author=author, receiver=receiver, content=content)

    if is_group_chat:
        chat_group.messages.add(message)

    return JsonResponse({'status': 'Message sent successfully'})


@csrf_exempt
@require_http_methods(["POST"])
def create_chat_group(request):
    name = request.POST.get('name')
    member_ids = request.POST.getlist('members')

    if not name or not member_ids:
        return JsonResponse({'error': 'Name and members are required'}, status=400)

    try:
        member_ids = [int(id) for id in member_ids]
    except ValueError:
        return JsonResponse({'error': 'Invalid member IDs'}, status=400)

    members = CustomUser.objects.filter(id__in=member_ids)
    chat_group = ChatGroup.objects.create(name=name, creator=request.user)
    chat_group.members.set(members)
    chat_group.save()

    return redirect('messages_page')


def index(request):
    return render(request, 'index.html')


from django.db.models import Q

def chat_with_user(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    messages = Message.objects.filter(
        Q(author=request.user, receiver=other_user) | Q(author=other_user, receiver=request.user),
        chat_group=None
    ).distinct()

    return render(request, 'chat_with_user.html', {
        'other_user': other_user,
        'messages': messages
    })


@csrf_exempt
@require_http_methods(["POST"])
def edit_chat_group(request, group_id):
    chat_group = get_object_or_404(ChatGroup, id=group_id)

    if request.user != chat_group.creator:
        return HttpResponseForbidden("Только создатель группы может изменить название.")

    data = json.loads(request.body)
    new_name = data.get('name')
    chat_group.change_name(new_name)
    return JsonResponse({'status': 'Групповой чат успешно обновлён'})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_chat_group(request, group_id):
    chat_group = get_object_or_404(ChatGroup, id=group_id)
    if request.user not in chat_group.members.all():
        raise PermissionDenied

    chat_group.delete_group()
    return JsonResponse({'status': 'Групповой чат успешно удалён'})


@csrf_exempt
@require_http_methods(["POST"])
def add_member_to_chat_group(request, group_id):
    chat_group = get_object_or_404(ChatGroup, id=group_id)
    if request.user not in chat_group.members.all():
        raise PermissionDenied

    data = json.loads(request.body)
    new_member_id = data.get('new_member_id')
    new_member = get_object_or_404(CustomUser, id=new_member_id)

    chat_group.members.add(new_member)
    return JsonResponse({'status': 'Пользователь успешно добавлен в групповой чат'})

@csrf_exempt
@require_http_methods(["POST"])
def remove_member_from_chat_group(request, group_id):
    chat_group = get_object_or_404(ChatGroup, id=group_id)
    if request.user not in chat_group.members.all():
        raise PermissionDenied

    data = json.loads(request.body)
    member_id = data.get('member_id')
    member = get_object_or_404(CustomUser, id=member_id)

    chat_group.members.remove(member)
    return JsonResponse({'status': 'Пользователь успешно удалён из группового чата'})

@login_required
def get_user_chats(request):
    chat_groups = ChatGroup.objects.filter(members=request.user)
    chats_data = [{'name': chat.name, 'id': chat.id} for chat in chat_groups]
    return JsonResponse({'chats': chats_data})

@csrf_exempt
@require_http_methods(["POST"])
def send_message_to_group(request, group_id):
    content = request.POST.get('content')

    chat_group = get_object_or_404(ChatGroup, id=group_id)

    if request.user not in chat_group.members.all():
        raise PermissionDenied

    message = Message.objects.create(author=request.user, content=content, chat_group=chat_group)

    return redirect(reverse('chat_with_group', args=[group_id]))

@login_required
def messages_page(request):
    chat_groups = ChatGroup.objects.filter(members=request.user)
    return render(request, 'messages_page.html', {'chats': chat_groups})

@login_required
def create_chat_group_form(request):
    users = CustomUser.objects.all()
    return render(request, 'create_chat_group_form.html', {'users': users})

@login_required
def chat_with_group(request, group_id):
    chat_group = get_object_or_404(ChatGroup, id=group_id)

    if request.user not in chat_group.members.all():
        return HttpResponseForbidden("Вы не являетесь участником этой группы чата.")

    messages = Message.objects.filter(chat_group=chat_group).order_by('timestamp')

    return render(request, 'chat_with_group.html', {
        'chat_group': chat_group,
        'messages': messages
    })

