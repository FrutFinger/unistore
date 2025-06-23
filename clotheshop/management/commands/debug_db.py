from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Debug database connection'

    def handle(self, *args, **options):
        self.stdout.write('=== Database Debug Info ===')
        
        # Показываем настройки базы данных
        self.stdout.write(f'DATABASE_URL from env: {settings.DATABASES["default"]}')
        
        # Пытаемся подключиться
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                self.stdout.write(f'PostgreSQL version: {version[0]}')
                
                # Проверяем существующие таблицы
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                self.stdout.write(f'Existing tables: {[table[0] for table in tables]}')
                
        except Exception as e:
            self.stdout.write(f'Database connection failed: {e}')
            self.stdout.write(f'Error type: {type(e)}') 