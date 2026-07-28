from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Crop, Order, UserProfile
import boto3
from django.conf import settings
from .models import ChatMessage
from django.contrib.auth.decorators import login_required



# ---------------------------
# Home Page
# ---------------------------
def home(request):
    return render(request, "home.html")


# ---------------------------
# User Signup
# ---------------------------
def user_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '').strip()

        if not name or not email or not password or not role:
            messages.error(request, "All fields are required.")
            return render(request, "user_signup.html")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered! Please log in.")
            return render(request, "user_signup.html")

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            UserProfile.objects.create(user=user, role=role)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('user_login')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, "user_signup.html")

    return render(request, "user_signup.html")


# ---------------------------
# User Login
# ---------------------------
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('user_login')
    return render(request, "user_login.html")


# ---------------------------
# Dashboard (Buyer/Seller split)
# ---------------------------
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'buyer'
    search_query = request.GET.get('q', '')
    saved_count = profile.saved_crops.count() if profile and hasattr(profile, 'saved_crops') else 0

    unread_count = ChatMessage.objects.filter(receiver=request.user).count()

    if role == 'seller':
        crops = Crop.objects.filter(owner=request.user)
        orders = Order.objects.filter(crop__owner=request.user)
        template_name = "dashboard_seller.html"
    else:  # buyer
        crops = Crop.objects.filter(sold=False).annotate(total_orders=Count('order'))
        orders = Order.objects.filter(buyer=request.user)

        if search_query:
            crops = crops.filter(
                Q(crop_name__icontains=search_query) |
                Q(crop_type__icontains=search_query) |
                Q(owner__first_name__icontains=search_query)
            )

        template_name = "dashboard_buyer.html"

    return render(request, template_name, {
        "role": role,
        "crops": crops,
        "orders": orders,
        "search_query": search_query,
        "saved_count": saved_count,
        "unread_count": unread_count   # ✅ THIS LINE ENABLES NOTIFICATIONS
    })



# ---------------------------
# Saved/Favorite Crops (Buyer)
# ---------------------------
def saved_crops(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    profile = getattr(request.user, 'profile', None)
    saved_crops_list = profile.saved_crops.all() if profile and hasattr(profile, 'saved_crops') else []

    return render(request, 'saved_crops.html', {
        "saved_crops": saved_crops_list
    })


# ---------------------------
# Crop CRUD (Seller)
# ---------------------------
def add_crop(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    if request.method == "POST":
        crop_name = request.POST.get("crop_name")
        crop_type = request.POST.get("crop_type")
        quantity = request.POST.get("quantity")
        price_per_unit = request.POST.get("price_per_unit")
        description = request.POST.get("description")

        Crop.objects.create(
            owner=request.user,
            crop_name=crop_name,
            crop_type=crop_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            description=description
        )

        # ✅ SNS NOTIFICATION TRIGGER (ADDED BLOCK)
        message = f"""
        New Crop Added on Farmease!

        Crop Name: {crop_name}
        Crop Type: {crop_type}
        Quantity: {quantity}
        Price per Unit: {price_per_unit}
        Description: {description}
        """
        send_sns_notification(message)
        # ✅ END SNS BLOCK

        messages.success(request, "Crop added successfully!")
        return redirect('dashboard')

    return render(request, "add_crop.html")



def edit_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)
    
    if crop.owner != request.user:
        messages.error(request, "Not authorized")
        return redirect('dashboard')

    if request.method == "POST":
        crop.crop_name = request.POST.get("crop_name")
        crop.crop_type = request.POST.get("crop_type")
        crop.quantity = request.POST.get("quantity")
        crop.price_per_unit = request.POST.get("price_per_unit")
        crop.description = request.POST.get("description")
        crop.save()

        # ✅ Trigger SNS notification
        message = f"""
        Crop Updated on Farmease!

        Crop: {crop.crop_name}
        Type: {crop.crop_type}
        Quantity: {crop.quantity}
        Price per Unit: {crop.price_per_unit}
        Description: {crop.description}
        """
        send_sns_notification(message)

        messages.success(request, "Crop updated!")
        return redirect('dashboard')

    return render(request, "edit_crop.html", {"crop": crop})


def delete_crop(request, crop_id):
    crop = get_object_or_404(Crop, id=crop_id)
    if crop.owner != request.user:
        messages.error(request, "Not authorized")
        return redirect('dashboard')
    crop.delete()
    messages.success(request, "Crop deleted!")
    return redirect('dashboard')


# ---------------------------
# Place Order (Buyer)
# ---------------------------
def place_order(request, crop_id):
    if not request.user.is_authenticated:
        return redirect('user_login')

    crop = get_object_or_404(Crop, id=crop_id)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        if quantity > crop.quantity:
            messages.error(request, "Quantity exceeds available stock")
            return redirect('dashboard')

        total_price = quantity * crop.price_per_unit
        Order.objects.create(buyer=request.user, crop=crop, quantity=quantity, total_price=total_price)
        crop.quantity -= quantity
        if crop.quantity == 0:
            crop.sold = True
        crop.save()
        messages.success(request, "Order placed successfully!")
        return redirect('dashboard')

    return render(request, "place_order.html", {"crop": crop})


# ---------------------------
# My Orders (Separate Page)
# ---------------------------
def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'buyer'

    if role == 'seller':
        orders = Order.objects.filter(crop__owner=request.user)
    else:
        orders = Order.objects.filter(buyer=request.user)

    return render(request, 'my_orders.html', {
        "orders": orders,
        "role": role
    })


# ---------------------------
# User Profile
# ---------------------------
def profile(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name")
        request.user.email = request.POST.get("email")
        request.user.save()
        messages.success(request, "Profile updated!")
        return redirect('profile')

    orders = Order.objects.filter(buyer=request.user)
    return render(request, "profile.html", {"orders": orders})
    
    
@login_required
def chat_view(request, seller_id):
    seller = User.objects.get(id=seller_id)

    messages_list = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=seller) |
        Q(sender=seller, receiver=request.user)
    ).order_by("timestamp")


    messages_list = messages_list.order_by("timestamp")

    if request.method == "POST":
        msg = request.POST.get("message")
        ChatMessage.objects.create(
            sender=request.user,
            receiver=seller,
            message=msg
        )
        return redirect("chat", seller_id=seller.id)

    return render(request, "chat.html", {
        "seller": seller,
        "messages": messages_list
    })
    
@login_required
def seller_chat_list(request):
    buyers = (
        ChatMessage.objects
        .filter(receiver=request.user)
        .values("sender__id", "sender__first_name", "sender__username")
        .distinct()
    )

    unread_count = ChatMessage.objects.filter(receiver=request.user).count()

    return render(request, "seller_chat_list.html", {
        "buyers": buyers,
        "unread_count": unread_count
    })
    
    
@login_required
def seller_chat_view(request, buyer_id):
    buyer = get_object_or_404(User, id=buyer_id)

    messages_list = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=buyer) |
        Q(sender=buyer, receiver=request.user)
    ).order_by("timestamp")

    if request.method == "POST":
        msg = request.POST.get("message")
        if msg:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=buyer,
                message=msg
            )
            return redirect("seller_chat_view", buyer_id=buyer.id)

    return render(request, "seller_chat.html", {
        "buyer": buyer,
        "messages": messages_list
    })


def faq_page(request):
    return render(request, "faq.html")
    
def about_page(request):
    return render(request, "about.html")


def user_logout(request):
    logout(request)
    return redirect('user_login')
    
def send_sns_notification(message):
    client = boto3.client(
        "sns",
        region_name=settings.AWS_REGION
    )

    response = client.publish(
        TopicArn=settings.SNS_TOPIC_ARN,
        Message=message,
        Subject="Farmease Crop Update"
    )

    return response    
    
