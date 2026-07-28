import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from main.models import Crop, Order # Adjust if your models are in a different file
from main.models import UserProfile



# ---------------------------
# Helper function to create a user
# ---------------------------
@pytest.fixture
def create_user(db):
    def _create_user(username="Test User", email="testuser@example.com", password="12345"):
        user = User.objects.create_user(username=email, email=email, password=password, first_name=username)
        return user
    return _create_user

@pytest.fixture
def create_crop(db, create_user):
    def _create_crop(owner=None, crop_name="Test Crop", crop_type="Vegetable", quantity=10, price_per_unit=100.0, description="Dummy crop"):
        if owner is None:
            owner = create_user(username="Seller", email="seller@example.com")
        crop = Crop.objects.create(
            owner=owner,
            crop_name=crop_name,
            crop_type=crop_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            description=description
        )
        return crop
    return _create_crop
    
@pytest.fixture
def create_order(db, create_user, create_crop):
    def _create_order(buyer=None, crop=None, quantity=1):
        if buyer is None:
            buyer = create_user(username="Buyer", email="buyer@example.com")
        if crop is None:
            crop = create_crop()
        order = Order.objects.create(
            buyer=buyer,
            crop=crop,
            quantity=quantity,
            total_price=quantity * crop.price_per_unit
        )
        return order
    return _create_order


# ---------------------------
# General Pages Tests
# ---------------------------
@pytest.mark.django_db
def test_home_page(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_signup_page(client):
    url = reverse("user_signup")
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_login_page(client):
    url = reverse("user_login")
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_logout_redirect(client):
    url = reverse("user_logout")
    response = client.get(url)
    # Logout usually redirects
    assert response.status_code in [301, 302]


# ---------------------------
# Dashboard & Profile Tests
# ---------------------------
@pytest.mark.django_db
def test_dashboard_redirect_without_login(client):
    url = reverse("dashboard")
    response = client.get(url)
    assert response.status_code in [301, 302]

@pytest.mark.django_db
def test_profile_redirect_without_login(client):
    url = reverse("profile")
    response = client.get(url)
    assert response.status_code in [301, 302]

@pytest.mark.django_db
def test_my_orders_redirect_without_login(client):
    url = reverse("my_orders")
    response = client.get(url)
    assert response.status_code in [301, 302]


# ---------------------------
# Auth Tests
# ---------------------------
@pytest.mark.django_db
def test_user_login(create_user, client):
    user = create_user()
    url = reverse("user_login")
    response = client.post(url, {"username": user.username, "password": "12345"})
    assert response.status_code in [200, 302]  # redirect after login

@pytest.mark.django_db
def test_user_signup(client):
    url = reverse("user_signup")
    response = client.post(url, {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123",
        "role": "buyer"
    })

    # Check redirect to login page
    assert response.status_code in [200, 302]

    # User and UserProfile created
    user = User.objects.filter(username="testuser@example.com").first()
    assert user is not None

    profile = UserProfile.objects.filter(user=user).first()
    assert profile is not None
    assert profile.role == "buyer"


# ---------------------------
# Crop Management Tests (Seller)
# ---------------------------
@pytest.mark.django_db
def test_add_crop_redirect_without_login(client):
    url = reverse("add_crop")
    response = client.get(url)
    assert response.status_code in [301, 302]

@pytest.mark.django_db
def test_edit_crop_redirect_without_login(client, create_crop):
    crop = create_crop()
    url = reverse("edit_crop", args=[crop.id])
    response = client.get(url)
    assert response.status_code in [301, 302]  # Redirect to login
    
@pytest.mark.django_db
def test_delete_crop_redirect_without_login(client, create_crop):
    crop = create_crop()
    url = reverse("delete_crop", args=[crop.id])
    response = client.get(url)
    assert response.status_code in [301, 302]  # Redirect to login

# ---------------------------
# Order Tests (Buyer)
# ---------------------------
@pytest.mark.django_db
def test_place_order_redirect_without_login(client):
    url = reverse("place_order", args=[1])
    response = client.get(url)
    assert response.status_code in [301, 302]


# ---------------------------
# Saved Crops Page
# ---------------------------
@pytest.mark.django_db
def test_saved_crops_redirect_without_login(client):
    url = reverse("saved_crops")
    response = client.get(url)
    assert response.status_code in [301, 302]
