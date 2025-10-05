from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework import status

# Убедитесь, что ваш путь импорта моделей правильный (например, 'dogs.models')
from dogs.models import Breed, Dog, Owner, Hobby, Country
# Убедитесь, что ваш путь импорта сериализаторов правильный (например, 'dogs.serializers')
from dogs.serializers import (
    BreedSerializer, BreedCreateSerializer, OwnerSerializer, 
    HobbySerializer, CountrySerializer, DogListSerializer, 
    DogCreateSerializer, DogUpdateSerializer, LoginSerializer
)

User = get_user_model()

class ModelTests(TestCase):
    """
    Создание общих объектов (включая пользователя) для всех тестов
    """
    def setUp(self):
        super().setUp()
        
        # Создание тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.another_user = User.objects.create_user(username='otheruser', password='otherpassword')
        
        # Создание связанных объектов
        self.breed = Breed.objects.create(name='Лабрадор')
        self.country = Country.objects.create(country='Россия')
        self.hobby = Hobby.objects.create(name_hobby='Аджилити')
        self.owner = Owner.objects.create(
            first_name='Иван', 
            last_name='Петров', 
            phone_number='88005553535', 
            user=self.user
        )
        
        # Создание объекта Dog
        self.dog = Dog.objects.create(
            name='Рекс',
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
        
        # Передаем self.context для установки request.user
        serializer = DogCreateSerializer(data=self.valid_dog_data, context=self.context)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        
        dog_instance = serializer.save()

        # Проверка, что объект был создан и user установлен корректно
        self.assertEqual(Dog.objects.count(), initial_count + 1)
        self.assertEqual(dog_instance.name, self.valid_dog_data['name'])
        self.assertEqual(dog_instance.user, self.user)
        
    def test_dog_creation_with_invalid_foreign_key(self):
        """Проверка, что невалидный внешний ключ вызывает ошибку."""
        serializer = DogCreateSerializer(data=self.invalid_dog_data, context=self.context)
        self.assertFalse(serializer.is_valid())
        
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