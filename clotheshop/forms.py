from django import forms
from .models import Message, Order
import phonenumbers
import re
from datetime import datetime, timedelta
import pytz


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['name', 'surname', 'phone', 'email', 'text']
        error_messages = {
            'name': {
                'required': "Пожалуйста, введите ваше имя",
            },
            'surname': {
                'required': "Пожалуйста, введите вашу фамилию",
            },
            'phone': {
                'required': "Пожалуйста, введите ваш телефон",
            },
            'email': {
                'required': "Пожалуйста, введите ваш email",
                'invalid': "Введите корректный email адрес",
            },
            'text': {
                'required': "Пожалуйста, введите текст сообщения",
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Имя"
        self.fields['surname'].label = "Фамилия"
        self.fields['phone'].label = "Телефон"
        self.fields['email'].label = "Электронная почта"
        self.fields['text'].label = "Текст сообщения"
        
        # Добавляем атрибуты для HTML5 валидации
        self.fields['name'].widget.attrs.update({'required': 'true'})
        self.fields['phone'].widget.attrs.update({
            'required': 'true',
            'inputmode': 'numeric',
            'maxlength': '11',
            'placeholder': '79991112233'
        })
        self.fields['text'].widget.attrs.update({'required': 'true'})

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Пожалуйста, введите ваше имя")
        if not name.isalpha() or not all('а' <= ch.lower() <= 'я' for ch in name):
            raise forms.ValidationError("Имя должно содержать только буквы русского алфавита")
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get('surname', '').strip()
        if surname:  # Фамилия не обязательна
            if not surname.isalpha() or not all('а' <= ch.lower() <= 'я' for ch in surname):
                raise forms.ValidationError("Фамилия должна содержать только буквы русского алфавита")
        return surname

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:  # Email не обязателен
            if not any(email.endswith(d) for d in ['@gmail.com', '@mail.ru', '@yandex.ru']):
                raise forms.ValidationError("Введите корректную почту (gmail.com, mail.ru или yandex.ru)")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        # Remove all non-digit characters
        phone = ''.join(ch for ch in phone if ch.isdigit())
        
        if not phone:
            raise forms.ValidationError("Пожалуйста, введите ваш телефон")
        
        if len(phone) != 11:
            raise forms.ValidationError("Номер должен содержать 11 цифр")
        
        if not phone.startswith('7'):
            raise forms.ValidationError("Номер должен начинаться с 7")
            
        try:
            # Add +7 prefix for phonenumbers library
            phone_with_prefix = '+7' + phone[1:]
            parsed_phone = phonenumbers.parse(phone_with_prefix, 'RU')
            if not phonenumbers.is_valid_number(parsed_phone):
                raise forms.ValidationError("Введите корректный номер телефона")
        except phonenumbers.NumberParseException:
            raise forms.ValidationError("Неверный формат номера")
            
        # Return the 11-digit format
        return phone

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if not text:
            raise forms.ValidationError("Пожалуйста, введите текст сообщения")
        return text


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'time_slot', 'preferred_messenger']
        error_messages = {
            'name': {
                'required': "Пожалуйста, введите ваше имя",
            },
            'phone': {
                'required': "Пожалуйста, введите ваш телефон",
            },
            'time_slot': {
                'required': "Пожалуйста, выберите время доставки",
            },
            'preferred_messenger': {
                'required': "Пожалуйста, выберите предпочитаемый мессенджер",
            }
        }
        
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': '79991112233',
                'class': 'phone-input',
                'id': 'phone-input',
                'maxlength': '11'
            }),
            'preferred_messenger': forms.HiddenInput(attrs={
                'id': 'messenger-input'  # Добавляем ID для удобства
            }),
            'time_slot': forms.Select(attrs={
                'class': 'time-slot-select'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Генерируем доступные временные слоты на основе московского времени
        available_slots = self.get_available_time_slots()
        
        if available_slots:
            self.fields['time_slot'] = forms.ChoiceField(
                choices=available_slots,
                widget=forms.Select(attrs={
                    'class': 'time-slot-select'
                }),
                error_messages={
                    'required': "Пожалуйста, выберите время доставки",
                }
            )
        else:
            # Если магазин закрыт, показываем сообщение
            self.fields['time_slot'] = forms.ChoiceField(
                choices=[('closed', 'На сегодня магазин закрыт, пожалуйста, попробуйте сделать заказ завтра с 9:00 до 19:30')],
                widget=forms.Select(attrs={
                    'class': 'time-slot-select',
                    'disabled': 'disabled'
                }),
                required=False
            )

    def get_available_time_slots(self):
        """Генерирует доступные временные слоты на основе московского времени"""
        try:
            # Получаем московское время
            moscow_tz = pytz.timezone('Europe/Moscow')
            now = datetime.now(moscow_tz)
            
            # Проверяем, не позже ли 19:30
            if now.hour >= 19 and now.minute >= 30:
                return []  # Магазин закрыт
            
            # Начало и конец рабочего дня
            start_hour = 9
            end_hour = 19
            
            # Если сейчас раньше 9:00, показываем все слоты
            if now.hour < start_hour:
                return [(f"{h}:00 - {h+1}:00", f"{h}:00 - {h+1}:00") for h in range(start_hour, end_hour)]
            
            # Если сейчас между 9:00 и 19:00, показываем только будущие слоты
            available_slots = []
            current_hour = now.hour
            current_minute = now.minute
            
            # Если сейчас 16:50, показываем слоты 17:00-18:00, 18:00-19:00
            # Если сейчас 17:30, показываем только 18:00-19:00
            for h in range(start_hour, end_hour):
                # Если это текущий час, проверяем минуты
                if h == current_hour:
                    # Если прошло больше 30 минут текущего часа, не показываем этот слот
                    if current_minute >= 30:
                        continue
                    # Если прошло меньше 30 минут, показываем текущий слот
                    available_slots.append((f"{h}:00 - {h+1}:00", f"{h}:00 - {h+1}:00"))
                elif h > current_hour:
                    # Показываем все будущие часы
                    available_slots.append((f"{h}:00 - {h+1}:00", f"{h}:00 - {h+1}:00"))
            
            return available_slots
            
        except Exception:
            # Fallback если что-то пошло не так с временными зонами
            return [(f"{h}:00 - {h+1}:00", f"{h}:00 - {h+1}:00") for h in range(9, 20)]

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Remove all non-digit characters
        phone = re.sub(r"[^\d]", "", phone)
        
        if len(phone) != 11:
            raise forms.ValidationError("Номер должен содержать 11 цифр.")
        
        if not phone.startswith('7'):
            raise forms.ValidationError("Номер должен начинаться с 7.")
        
        try:
            # Add +7 prefix for phonenumbers library
            phone_with_prefix = '+7' + phone[1:]
            parsed_phone = phonenumbers.parse(phone_with_prefix, 'RU')
            if not phonenumbers.is_valid_number(parsed_phone):
                raise forms.ValidationError("Введите корректный номер телефона.")
        except phonenumbers.NumberParseException:
            raise forms.ValidationError("Неверный формат номера.")
        
        # Return the 11-digit format
        return phone