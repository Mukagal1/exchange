from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Item, ExchangeRequest, Notification, Category, UserProfile
from .forms import ItemForm, ExchangeRequestForm
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import GroupChat, GroupMessage, Chat, Message


from .models import UserProfile
from .utils import get_client_ip_address, get_location_by_ip

def index(request):
    return render(request, "index.html")

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, "login.html", {"error": "Введите имя пользователя и пароль"})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"redirect_url": "/main/"})
        else:
            return render(request, "login.html", {"error": "Неверные учетные данные"})

    return render(request, "login.html")

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            if not username:
                return JsonResponse({"error": "Введите имя пользователя"}, status=400)
            if not email:
                return JsonResponse({"error": "Введите email"}, status=400)
            if not password or not confirm_password:
                return JsonResponse({"error": "Введите пароль и его подтверждение"}, status=400)
            if password != confirm_password:
                return JsonResponse({"error": "Пароли не совпадают"}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Имя пользователя уже занято"}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)

            ip = get_client_ip_address(request)
            location = get_location_by_ip(ip)

            print(f"User IP: {ip}")
            print(f"User Location: {location}")

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "city": location.get('city') or "Unknown",
                    "country": location.get('country') or "Unknown",
                    "region": location.get('region') or "Unknown",
                    "latitude": location.get('lat') or 0.0,
                    "longitude": location.get('lon') or 0.0,
                }
            )

            return JsonResponse({"message": "Регистрация успешна"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Ошибка обработки JSON"}, status=400)

    return render(request, "signup.html")


def signout(request):
    logout(request)
    return redirect('login')  # После выхода перекидывает на логин

@login_required
def main_page(request):
    if not request.user.is_authenticated:
        print('not authenticated')
        return redirect('login')  # Если не залогинен — отправляем на логин
    return render(request, "main.html", {"user": request.user})

@login_required
def place(request):
    items = Item.objects.all()
    print(items)
    return render(request, "place.html", {"items": items})

@login_required
def item_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    return render(request, "item_detail.html", {"item": item})

@login_required
def my_items(request):
    items = Item.objects.filter(user=request.user)
    return render(request, "my_items.html", {"items": items})

from django.contrib import messages

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Вещь успешно удалена.")
    return redirect("myitems")

@login_required
def add_item(request):
    """ Добавление новой вещи """
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user  # Привязываем вещь к пользователю

            user_profile = request.user.profile
            item.city = user_profile.city
            item.country = user_profile.country
            item.save()
            return redirect("myitems")
    else:
        form = ItemForm()
    
    return render(request, "add_item.html", {"form": form})

@login_required
def offer_exchange(request, item_id):
    to_item = get_object_or_404(Item, id=item_id)
    from_items = Item.objects.filter(user=request.user)  # Все вещи пользователя

    if request.method == 'POST':
        form = ExchangeRequestForm(request.POST, user=request.user)
        if form.is_valid():
            from_item = form.cleaned_data['from_item']
            exchange_request = ExchangeRequest(
                from_user=request.user,
                to_user=to_item.user,
                from_item=from_item,
                to_item=to_item
            )
            exchange_request.save()

            return redirect('item_detail', item_id=item_id)  # Вернуться на страницу вещи

    else:
        form = ExchangeRequestForm(user=request.user)

    return render(request, 'offer_trade.html', {'to_item': to_item, 'from_items': from_items, 'form': form})

@login_required
def notifications(request):
    exchange_requests = ExchangeRequest.objects.filter(to_user=request.user, status="pending").order_by('-created_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-id')
    return render(
        request,
        "notifications.html",
        {
            "exchange_requests": exchange_requests,
            "notifications": notifications,
        }
    )

@login_required
def mark_notifications_as_read(request):
    ExchangeRequest.objects.filter(to_user=request.user, status="pending").update(status="viewed")
    Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)
    return JsonResponse({"success": True})

@login_required
def unread_notifications_count(request):
    exchange_count = ExchangeRequest.objects.filter(to_user=request.user, status="pending").count()
    notification_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    total_count = exchange_count + notification_count
    return JsonResponse({"count": total_count})

from django.urls import reverse

@login_required
@csrf_exempt
def accept_exchange(request, request_id):
    if request.method == "POST":
        exchange_request = get_object_or_404(ExchangeRequest, id=request_id, to_user=request.user)
        exchange_request.status = "accepted"
        exchange_request.save()

        # Найти или создать чат между пользователями
        chat = Chat.objects.filter(members=exchange_request.from_user).filter(members=exchange_request.to_user).first()
        if not chat:
            chat = Chat.objects.create(name=f"Чат {exchange_request.from_user.username} и {exchange_request.to_user.username}")
            chat.members.add(exchange_request.from_user, exchange_request.to_user)

        # Отправить уведомление отправителю
        Notification.objects.create(
            user=exchange_request.from_user,
            sender=request.user,
            from_item=exchange_request.from_item.name,
            to_item=exchange_request.to_item.name,
            is_read=True,
        )

        # Вернуть URL для перехода в чат
        chat_url = reverse('chat_detail', args=[chat.id])
        return JsonResponse({"success": True, "redirect_url": chat_url})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.members.all():
        return redirect('main_page')
    messages = chat.messages.all().order_by("created_at")
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)
            return redirect("chat_detail", chat_id=chat.id)
    return render(request, "chat_detail.html", {"chat": chat, "messages": messages})

@login_required
@csrf_exempt
def decline_exchange(request, request_id):
    if request.method == "POST":
        exchange_request = get_object_or_404(ExchangeRequest, id=request_id, to_user=request.user)
        exchange_request.status = "declined"
        exchange_request.save()

        # Отправить уведомление отправителю
        Notification.objects.create(
            user=exchange_request.from_user,
            sender=request.user,
            from_item=exchange_request.from_item.name,
            to_item=exchange_request.to_item.name,
            is_read=False,
        )

        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
@csrf_exempt
def profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {'form': form})

@login_required
def update_avatar(request):
    if request.method == 'POST':
        profile = request.user.profile
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
            profile.save()
    return redirect('profile')


@login_required
def place(request):
    items = Item.objects.all()
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    city = request.GET.get('city', '')
    country = request.GET.get('country', '')

    # Фильтрация
    if query:
        items = items.filter(name__icontains=query)
    if category:
        items = items.filter(category__id=category)
    if city:
        items = items.filter(city__icontains=city)
    if country:
        items = items.filter(country__icontains=country)

    categories = Category.objects.all()  # Для отображения категорий в фильтре
    return render(request, "place.html", {"items": items, "categories": categories})

@login_required
def group_chats(request):
    """Список чатов: ваши групповые и приватные чаты"""
    user_chats = GroupChat.objects.filter(members=request.user)  # Групповые чаты
    available_chats = GroupChat.objects.exclude(members=request.user)  # Доступные групповые чаты
    private_chats = Chat.objects.filter(members=request.user)  # Приватные чаты (один на один)
    return render(
        request,
        "group_chats.html",
        {
            "user_chats": user_chats,
            "available_chats": available_chats,
            "private_chats": private_chats,
        }
    )

@login_required
def group_chat_detail(request, chat_id):
    """Детали конкретного чата"""
    chat = get_object_or_404(GroupChat, id=chat_id)
    
    # Если пользователь не участник, добавляем его в чат
    if request.user not in chat.members.all():
        chat.members.add(request.user)

    # Получаем сообщения чата
    messages = chat.messages.all().order_by("created_at")

    # Обрабатываем отправку сообщения
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            GroupMessage.objects.create(chat=chat, sender=request.user, content=content)
            return redirect("group_chat_detail", chat_id=chat.id)

    return render(request, "group_chat_detail.html", {"chat": chat, "messages": messages})


@login_required
def join_group_chat(request, chat_id):
    """Присоединение к чату"""
    chat = get_object_or_404(GroupChat, id=chat_id)
    chat.members.add(request.user)
    return redirect("group_chat_detail", chat_id=chat.id)


@login_required
def create_group_chat(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')  # Получаем описание
        chat = GroupChat.objects.create(name=name, description=description)
        chat.members.add(request.user)  # Добавляем создателя в участники
        return redirect('group_chats')  # Перенаправление на список чатов
    return render(request, 'create_group_chat.html')
