from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Product, Message, Order, ProductSize, OrderItem

# Убираем ненужные разделы из админ-панели
admin.site.unregister(Group)

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'product_type', 'get_stock_status', 'get_image_preview')
    list_filter = ('product_type',)
    search_fields = ('name',)
    inlines = [ProductSizeInline]
    
    def get_stock_status(self, obj):
        """Show stock status in admin list"""
        total_stock = sum(size.quantity for size in obj.sizes.all())
        return f"В наличии: {total_stock}" if total_stock > 0 else "Нет в наличии"
    
    get_stock_status.short_description = 'Наличие'
    
    def get_image_preview(self, obj):
        """Show image preview in admin list"""
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
        return "Нет изображения"
    get_image_preview.short_description = 'Изображение'
    get_image_preview.allow_tags = True

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