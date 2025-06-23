from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Favorite, ProductSize, OrderItem, Order
from .forms import MessageForm, OrderForm
from django.http import HttpResponse
from django.contrib import admin
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
import random
import json
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


def home(request):
    # Получаем 6 случайных товаров, которые есть в наличии
    available_products = []
    
    # Получаем все товары
    all_products = Product.objects.all()
    
    # Фильтруем только те, которые есть в наличии
    for product in all_products:
        if not product.is_fully_out_of_stock():
            available_products.append(product)
    
    # Преобразуем в список и перемешиваем
    random.shuffle(available_products)
    
    # Берем первые 6 (или меньше, если товаров мало)
    featured_products = available_products[:6]
    
    return render(request, 'main.html', {
        'featured_products': featured_products
    })

# Главная страница с каталогом товаров
def catalog(request):
    products = Product.objects.all()
    product_type = request.GET.get('type')
    price_from = request.GET.get('price_from')
    price_to = request.GET.get('price_to')
    size_filter = request.GET.get('size')
    sort_by = request.GET.get('sort', 'name')  # По умолчанию сортируем по имени

    if product_type:
        products = products.filter(product_type=product_type)
    if price_from:
        products = products.filter(price__gte=price_from)
    if price_to:
        products = products.filter(price__lte=price_to)
    
    # Фильтрация по размеру
    if size_filter:
        products = products.filter(sizes__size=size_filter, sizes__quantity__gt=0)
    
    # Сортировка
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-id')
    
    # Фильтруем товары, которые есть в наличии
    available_products = []
    for product in products:
        if not product.is_fully_out_of_stock():
            available_products.append(product)

    # Получаем все доступные размеры для фильтра
    available_sizes = ProductSize.objects.filter(quantity__gt=0).values_list('size', flat=True).distinct()

    return render(request, 'catalog.html', {
        'products': available_products,
        'available_sizes': available_sizes,
        'current_filters': {
            'type': product_type,
            'price_from': price_from,
            'price_to': price_to,
            'size': size_filter,
            'sort': sort_by
        }
    })

# Страница контактов и обратной связи
def contact(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            # Проверяем, был ли это AJAX-запрос
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'message': 'Сообщение успешно отправлено!'}, status=200)
            # Если это обычный POST-запрос, перенаправляем на страницу успеха
            return redirect('contact_success')
        else:
            # Если форма невалидна, возвращаем ошибки
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({'errors': errors}, status=400)
            # Для обычного запроса, снова рендерим страницу с формой и ошибками
            return render(request, 'contact.html', {'form': form})
    else:
        # Для GET-запроса просто показываем пустую форму
        form = MessageForm()
    
    return render(request, 'contact.html', {'form': form})


# Страница с информацией об оплате и получении заказа
def payment(request):
    return render(request, 'payment.html')

def cart(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    cart_data = request.session.get('cart', {})
    detailed_cart = []
    total_price = 0

    # Если вдруг cart_data — список, то приводим к пустому словарю
    if isinstance(cart_data, list):
        cart_data = {}

    for key, item in cart_data.items():
        try:
            product = Product.objects.get(id=item['product_id'])
            size = item['size']
            quantity = item['quantity']
            
            if product.has_sizes():
                # Для товаров с размерами
                size_obj = ProductSize.objects.get(product=product, size=size)

                max_quantity = size_obj.quantity
                if quantity > max_quantity:
                    quantity = max_quantity
                    item['quantity'] = quantity

                detailed_cart.append({
                    'product': product,
                    'size': size,
                    'quantity': quantity,
                    'subtotal': quantity * float(product.price)
                })
                total_price += quantity * float(product.price)
            else:
                # Для товаров без размеров
                if hasattr(product, 'no_size_info'):
                    max_quantity = product.no_size_info.quantity
                    if quantity > max_quantity:
                        quantity = max_quantity
                        item['quantity'] = quantity

                    detailed_cart.append({
                        'product': product,
                        'size': 'Без размера',
                        'quantity': quantity,
                        'subtotal': quantity * float(product.price)
                    })
                    total_price += quantity * float(product.price)
                    
        except Product.DoesNotExist:
            continue
        except ProductSize.DoesNotExist:
            continue

    request.session['cart'] = cart_data  # обновляем, если изменили

    # Создаем форму для заказа
    form = OrderForm()

    hours = range(9, 20)  # Пример для выбора времени

    total_quantity = sum(item['quantity'] for item in detailed_cart)

    return render(request, 'cart.html', {
        'cart_items': detailed_cart,
        'form': form,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'hours': hours,
    })


# Страница избранного товара
def favorites(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    fav_items = Favorite.objects.filter(session_id=session_id)
    return render(request, 'favorites.html', {'favorites': fav_items})

def add_to_cart_detail(request, product_id):
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Not a POST request'}, status=400)

    size = request.POST.get('size')
    action = request.POST.get('action', 'add')

    try:
        product = Product.objects.get(id=product_id)
        
        # Проверяем, есть ли у товара размеры
        if product.has_sizes():
            if not size:
                return JsonResponse({'success': False, 'error': 'Size not specified'}, status=400)
            
            try:
                size_obj = ProductSize.objects.get(product=product, size=size)
                
                # Проверяем, есть ли товар в наличии
                if size_obj.quantity <= 0:
                    return JsonResponse({'success': False, 'error': 'Товар закончился'}, status=400)
                    
            except ProductSize.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Size not available'}, status=404)
        else:
            # Для товаров без размеров (шапки, кепки)
            if not hasattr(product, 'no_size_info') or product.no_size_info.quantity <= 0:
                return JsonResponse({'success': False, 'error': 'Товар закончился'}, status=400)
            size = 'ONE_SIZE'  # Используем ONE_SIZE для товаров без размеров
            
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

    cart = request.session.get('cart')
    if not isinstance(cart, dict):
        cart = {}
    key = f"{product.id}_{size}"

    if action == 'add':
         if key not in cart:
            cart[key] = {'product_id': product.id, 'size': size, 'quantity': 1}
    elif action == 'increase':
        if product.has_sizes():
            size_obj = ProductSize.objects.get(product=product, size=size)
            if key in cart and cart[key]['quantity'] < size_obj.quantity:
                cart[key]['quantity'] += 1
            else:
                return JsonResponse({'success': False, 'error': 'Недостаточно товара на складе'}, status=400)
        else:
            # Для товаров без размеров
            if key in cart and cart[key]['quantity'] < product.no_size_info.quantity:
                cart[key]['quantity'] += 1
            else:
                return JsonResponse({'success': False, 'error': 'Недостаточно товара на складе'}, status=400)
    elif action == 'decrease':
        if key in cart and cart[key]['quantity'] > 1:
            cart[key]['quantity'] -= 1
        elif key in cart:
            del cart[key]
    elif action == 'remove':
        if key in cart:
            del cart[key]

    request.session['cart'] = cart
    return JsonResponse({'success': True})

def add_to_cart(request, product_id):
    if request.method == 'POST':
        size = request.POST.get('size')
        cart = request.session.get('cart', {})
        
        # Проверяем доступность товара
        try:
            product = Product.objects.get(id=product_id)
            
            if product.has_sizes():
                # Для товаров с размерами
                if not size:
                    return redirect('catalog')
                    
                try:
                    size_obj = ProductSize.objects.get(product=product, size=size)
                    
                    if size_obj.quantity <= 0:
                        # Товар закончился
                        return redirect('catalog')
                        
                except ProductSize.DoesNotExist:
                    return redirect('catalog')
            else:
                # Для товаров без размеров (шапки, кепки)
                if not hasattr(product, 'no_size_info') or product.no_size_info.quantity <= 0:
                    return redirect('catalog')
                size = 'ONE_SIZE'  # Используем ONE_SIZE для товаров без размеров
                
        except Product.DoesNotExist:
            return redirect('catalog')

        key = f"{product_id}_{size}"

        if key in cart:
            # Проверяем, не превышаем ли доступное количество
            if product.has_sizes():
                size_obj = ProductSize.objects.get(product=product, size=size)
                if cart[key]['quantity'] < size_obj.quantity:
                    cart[key]['quantity'] += 1
            else:
                if cart[key]['quantity'] < product.no_size_info.quantity:
                    cart[key]['quantity'] += 1
        else:
            cart[key] = {'product_id': product_id, 'size': size, 'quantity': 1}

        request.session['cart'] = cart
    return redirect('catalog')

# Добавление товара в избранное
def add_to_favorites(request, product_id):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    product = get_object_or_404(Product, id=product_id)
    Favorite.objects.get_or_create(product=product, session_id=session_id)
    return redirect('catalog')

def contact_success(request):
    """
    Страница, которая отображается после успешной отправки формы.
    """
    return render(request, 'contact_success.html')

# Обработка отправки заказа
def submit_order(request):
    if request.method == 'POST':
        # Проверяем, что корзина не пуста
        cart = request.session.get('cart', {})
        if not cart:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'errors': {'__all__': ['Ваша корзина пуста. Пожалуйста, добавьте товары перед оформлением заказа.']}}, status=400)
            return redirect('cart')
        
        form = OrderForm(request.POST)
        if form.is_valid():
            print("Received data:", request.POST)  # Для отладки
            print("Form is valid. Messenger:", form.cleaned_data['preferred_messenger'])
            
            # Проверяем наличие товаров перед созданием заказа
            insufficient_stock = []
            
            for item in cart.values():
                try:
                    product = Product.objects.get(id=item['product_id'])
                    
                    if product.has_sizes():
                        # Для товаров с размерами
                        size_obj = ProductSize.objects.get(product=product, size=item['size'])
                        
                        if size_obj.quantity < item['quantity']:
                            insufficient_stock.append(f"{product.name} (размер {item['size']}) - доступно {size_obj.quantity}, заказано {item['quantity']}")
                    else:
                        # Для товаров без размеров
                        if not hasattr(product, 'no_size_info') or product.no_size_info.quantity < item['quantity']:
                            available = product.no_size_info.quantity if hasattr(product, 'no_size_info') else 0
                            insufficient_stock.append(f"{product.name} - доступно {available}, заказано {item['quantity']}")
                            
                except (Product.DoesNotExist, ProductSize.DoesNotExist):
                    insufficient_stock.append(f"Товар с ID {item['product_id']} не найден")
            
            if insufficient_stock:
                error_message = "Недостаточно товаров на складе: " + "; ".join(insufficient_stock)
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'errors': {'__all__': [error_message]}}, status=400)
                # Для обычного запроса, можно добавить сообщение в сессию
                return redirect('cart')
            
            # Создаем заказ
            order = form.save()
            
            # Создаем элементы заказа и обновляем остатки
            for item in cart.values():
                product = Product.objects.get(id=item['product_id'])
                
                if product.has_sizes():
                    # Для товаров с размерами
                    size_obj = ProductSize.objects.get(product=product, size=item['size'])
                    
                    # Создаем элемент заказа
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        size=item['size'],
                        quantity=item['quantity']
                    )
                    
                    # Уменьшаем остаток на складе
                    size_obj.quantity -= item['quantity']
                    size_obj.save()
                    
                    print(f"Updated stock for {product.name} size {item['size']}: {size_obj.quantity + item['quantity']} -> {size_obj.quantity}")
                else:
                    # Для товаров без размеров
                    no_size_obj = product.no_size_info
                    
                    # Создаем элемент заказа
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        size=None,  # Нет размера для шапок/кепок
                        quantity=item['quantity']
                    )
                    
                    # Уменьшаем остаток на складе
                    no_size_obj.quantity -= item['quantity']
                    no_size_obj.save()
                    
                    print(f"Updated stock for {product.name}: {no_size_obj.quantity + item['quantity']} -> {no_size_obj.quantity}")
            
            # Очищаем корзину
            request.session['cart'] = {}
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('order_success', args=[order.id])
                })
            return redirect('order_success', order_id=order.id)
        
        # Если форма невалидна
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [str(error) for error in field_errors]
            return JsonResponse({'errors': errors}, status=400)
    
    return redirect('cart')

# Страница товара
import json

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Для товаров с размерами
    if product.has_sizes():
        sizes = product.sizes.filter(quantity__gt=0)
    else:
        # Для товаров без размеров (шапки, кепки)
        sizes = []
        if hasattr(product, 'no_size_info') and product.no_size_info.quantity > 0:
            sizes = [{'size': 'ONE_SIZE', 'quantity': product.no_size_info.quantity}]

    # Логика корзины
    cart = request.session.get('cart', {})
    cart_for_product = {
        item['size']: item['quantity']
        for key, item in cart.items()
        if str(item['product_id']) == str(product_id)
    }

    # Логика для блока «Вам может понравиться»
    if product.has_sizes():
        related_products = list(
            Product.objects.exclude(id=product_id)
            .filter(product_type=product.product_type)
            .filter(sizes__quantity__gt=0)  # Только товары в наличии
            .distinct()
        )
    else:
        # Для товаров без размеров
        related_products = list(
            Product.objects.exclude(id=product_id)
            .filter(product_type=product.product_type)
            .filter(no_size_info__quantity__gt=0)  # Только товары в наличии
            .distinct()
        )
    
    # Перемешиваем и берем первые 4
    random.shuffle(related_products)
    related_products = related_products[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'sizes': sizes,
        'cart_json': json.dumps(cart_for_product),
        'related_products': related_products,
    })



# Удаление из избранного

@require_POST
def remove_favorite(request, favorite_id):
    session_id = request.session.session_key
    if not session_id:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=400)

    try:
        fav_item = Favorite.objects.get(id=favorite_id, session_id=session_id)
        fav_item.delete()
        return JsonResponse({'status': 'success'})
    except Favorite.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Favorite item not found'}, status=404)
    
@require_POST
def update_cart_quantity(request):
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    action = request.POST.get('action')

    cart = request.session.get('cart', {})
    key = f"{product_id}_{size}"

    if key in cart:
        if action == 'increase':
            # Проверяем доступность товара перед увеличением
            try:
                product = Product.objects.get(id=product_id)
                
                if product.has_sizes():
                    # Для товаров с размерами
                    size_obj = ProductSize.objects.get(product=product, size=size)
                    
                    if cart[key]['quantity'] < size_obj.quantity:
                        cart[key]['quantity'] += 1
                    else:
                        # Недостаточно товара
                        return JsonResponse({'success': False, 'error': 'Недостаточно товара на складе'}, status=400)
                else:
                    # Для товаров без размеров
                    if hasattr(product, 'no_size_info') and cart[key]['quantity'] < product.no_size_info.quantity:
                        cart[key]['quantity'] += 1
                    else:
                        # Недостаточно товара
                        return JsonResponse({'success': False, 'error': 'Недостаточно товара на складе'}, status=400)
                        
            except (Product.DoesNotExist, ProductSize.DoesNotExist):
                return JsonResponse({'success': False, 'error': 'Товар не найден'}, status=404)
        elif action == 'decrease':
            cart[key]['quantity'] = max(1, cart[key]['quantity'] - 1)
        elif action == 'remove':
            del cart[key]

    request.session['cart'] = cart
    return redirect('cart')

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    total = sum(item.product.price * item.quantity for item in order_items)
    
    return render(request, 'order_success.html', {
        'order': order,
        'order_items': order_items,
        'total': total
    })