from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Item, ExchangeRequest, Notification
from .forms import ItemForm, ExchangeRequestForm
from django.shortcuts import get_object_or_404

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

            User.objects.create_user(username=username, email=email, password=password)
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

@login_required
def add_item(request):
    """ Добавление новой вещи """
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user  # Привязываем вещь к пользователю
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
    print(exchange_requests)
    return render(request, "notifications.html", {"notifications": exchange_requests})

@login_required
def mark_notifications_as_read(request):
    ExchangeRequest.objects.filter(to_user=request.user, status="pending").update(status="viewed")
    return redirect("notifications")

@login_required
def unread_notifications_count(request):
    count = ExchangeRequest.objects.filter(to_user=request.user, status="pending").count()
    return JsonResponse({"count": count})

@login_required
@csrf_exempt
def accept_exchange(request, request_id):
    if request.method == "POST":
        exchange_request = get_object_or_404(ExchangeRequest, id=request_id, to_user=request.user)
        exchange_request.status = "accepted"
        exchange_request.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
@csrf_exempt
def decline_exchange(request, request_id):
    if request.method == "POST":
        exchange_request = get_object_or_404(ExchangeRequest, id=request_id, to_user=request.user)
        exchange_request.status = "declined"
        exchange_request.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
