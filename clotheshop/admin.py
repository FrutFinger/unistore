from django.contrib import admin
from .models import Product, Message, Order, Favorite, ProductSize, OrderItem

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'product_type', 'get_stock_status')
    list_filter = ('product_type',)
    search_fields = ('name',)
    inlines = [ProductSizeInline]
    
    def get_stock_status(self, obj):
        """Show stock status in admin list"""
        total_stock = sum(size.quantity for size in obj.sizes.all())
        return f"В наличии: {total_stock}" if total_stock > 0 else "Нет в наличии"
    
    get_stock_status.short_description = 'Наличие'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',),
        }

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('product', 'session_id')
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',),
        }

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'time_slot', 'get_messenger', 'created_at')
    list_filter = ('preferred_messenger', 'created_at')
    inlines = [OrderItemInline]
    
    def get_messenger(self, obj):
        messengers = {
            'telegram': 'Telegram',
            'whatsapp': 'WhatsApp',
            'neutral': 'Не указан'
        }
        return messengers.get(obj.preferred_messenger, obj.preferred_messenger)
    get_messenger.short_description = 'Мессенджер'
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',),
        }

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'phone')
    search_fields = ('name', 'surname', 'email')
    readonly_fields = ('name', 'surname', 'phone', 'email', 'text')

    fieldsets = (
        (None, {'fields': ('name', 'surname', 'email', 'phone')}),
        ('Сообщение', {'fields': ('text',)}),
    )

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',),
        } 