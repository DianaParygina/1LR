from django.test import TestCase
from django.contrib.auth import get_user_model
from dogs.models import Breed, Dog, Owner, Country, Hobby

# Получаем модель пользователя Django
User = get_user_model()

class ModelTests(TestCase):
    """
    Создание общих объектов (включая пользователя) для всех тестов
    """
    def setUp(self):
        # 1. Создаем тестового пользователя (обязательно для Dog и Owner)
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', # Добавил email, если он требуется
            password='testpassword',
            is_staff=True, # Опционально: можно сделать его штатным сотрудником
            is_superuser=True # Опционально: можно сделать его суперпользователем
        )
        
        # 2. Создаем базовые связанные объекты
        self.breed = Breed.objects.create(name="Пудель")
        self.country = Country.objects.create(country="Испания")
        self.hobby = Hobby.objects.create(name_hobby="Фрисби")
        
        # 3. Создаем владельца, привязанного к пользователю
        self.owner = Owner.objects.create(
            first_name="Мария", 
            last_name="Иванова", 
            phone_number="88005553535",
            user=self.user 
        )
        
        # 4. Создаем собаку, привязанную ко всем объектам
        self.dog = Dog.objects.create(
            name="Алмаз",
            breed=self.breed,
            owner=self.owner,
            country=self.country,
            hobby=self.hobby,
            user=self.user
        )

# ----------------------------------------------------------------------
# ПРОПУСКАЕМ тесты для Breed, Country, Hobby, Owner, Dog. Они используют setUp.
# ----------------------------------------------------------------------

class DogCreationTest(ModelTests):
    """
    Фокусируемся только на test_create_dog
    """
    def test_create_dog(self):
        """Проверяет, что собака создается с привязкой к пользователю и владельцу."""
        dog_count_before = Dog.objects.count()
        
        new_dog = Dog.objects.create(
            name="Рекс",
            breed=self.breed,
            owner=self.owner,
            country=self.country,
            hobby=self.hobby,
            user=self.user 
        )
        
        # 1. Проверяем, что объект создан
        self.assertEqual(Dog.objects.count(), dog_count_before + 1)
        # 2. Проверяем, что внешний ключ user установлен
        self.assertEqual(new_dog.user, self.user)
        # 3. Проверяем, что имя установлено
        self.assertEqual(new_dog.name, "Рекс")


class OwnerCreationTest(ModelTests):
    """
    Фокусируемся только на test_create_owner
    """
    def test_create_owner(self):
        """Проверяет, что владелец создается с привязкой к новому пользователю."""
        owner_count_before = Owner.objects.count()
        
        # Создаем еще одного пользователя, чтобы избежать конфликта
        new_user = User.objects.create_user(
            username='newowneruser', 
            password='newpassword'
        )
        
        new_owner = Owner.objects.create(
            first_name="Елена",
            last_name="Сергеева",
            phone_number="89991112233",
            user=new_user
        )
        
        # 1. Проверяем, что объект создан
        self.assertEqual(Owner.objects.count(), owner_count_before + 1)
        # 2. Проверяем, что внешний ключ user установлен
        self.assertEqual(new_owner.user, new_user)
        # 3. Проверяем, что строковое представление корректно
        self.assertEqual(str(new_owner), "Елена Сергеева")