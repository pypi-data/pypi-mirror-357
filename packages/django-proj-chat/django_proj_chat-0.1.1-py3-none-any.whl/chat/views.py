from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message

@login_required
def chat_view(request):
    users = User.objects.exclude(id=request.user.id)
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        content = request.POST.get('content')
        if recipient_id and content:
            try:
                recipient = User.objects.get(id=recipient_id)
                Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    content=content
                )
                return redirect('chat')
            except User.DoesNotExist:
                return redirect('chat')
        else:
            return redirect('chat')
    return render(request, 'chat/chat.html', {'users': users})

@login_required
def messages_view(request, recipient_id):
    try:
        recipient = User.objects.get(id=recipient_id)
        messages = Message.objects.filter(
            sender__in=[request.user, recipient],
            recipient__in=[request.user, recipient]
        ).order_by('timestamp')
        return render(request, 'chat/messages.html', {
            'recipient': recipient,
            'messages': messages
        })
    except User.DoesNotExist:
        return redirect('chat')