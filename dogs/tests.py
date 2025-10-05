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

# 1. БАЗОВАЯ НАСТРОЙКА ТЕСТОВЫХ ДАННЫХ

class SerializerTestSetup(APITestCase):
    """Базовый класс для создания тестовых данных, наследуется от APITestCase."""
    
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

        # Фабрика для создания фейковых запросов (нужна для контекста)
        self.factory = APIRequestFactory()
        
        # Контекст для сериализаторов, использующих request.user (DogCreateSerializer, OwnerSerializer)
        self.request = self.factory.get('/')
        self.request.user = self.user 
        self.context = {'request': self.request}
        
        # --- Данные для тестов ---
        self.valid_breed_data = {'name': 'Пудель'}
        
        self.valid_owner_data = {
            'first_name': 'Анна',
            'last_name': 'Сидорова',
            'phone_number': '89991112233',
        }
        
        self.valid_dog_data = {
            'name': 'Шарик',
            'breed': self.breed.id,
            'owner': self.owner.id,
            'country': self.country.id,
            'hobby': self.hobby.id,
        }
        
        self.invalid_dog_data = {
            'name': '', # Невалидное пустое поле (TextField в модели позволяет, но оставим для примера валидации)
            'breed': 9999, # Несуществующий PK
            'owner': self.owner.id,
            'country': self.country.id,
            'hobby': self.hobby.id,
        }

# 2. ТЕСТЫ СЕРИАЛИЗАТОРОВ ДЛЯ МОДЕЛИ DOG

class DogSerializersTest(SerializerTestSetup):
    
    # ------------------ DogListSerializer (Чтение с вложенными полями) ------------------
    def test_dog_list_serialization(self):
        """Проверка, что DogListSerializer правильно сериализует данные с вложенными объектами."""
        serializer = DogListSerializer(instance=self.dog)
        data = serializer.data
        # Проверка ожидаемых полей
        self.assertEqual(data['name'], self.dog.name)
        self.assertEqual(data['user'], self.user.id) 
        
        # Проверка вложенной сериализации (должен быть словарь, а не ID)
        self.assertIsInstance(data['breed'], dict)
        self.assertEqual(data['breed']['name'], self.breed.name)
        self.assertEqual(data['owner']['first_name'], self.owner.first_name)
        self.assertEqual(data['country']['country'], self.country.country)
        self.assertEqual(data['hobby']['name_hobby'], self.hobby.name_hobby)

    # ------------------ DogCreateSerializer (Создание) ------------------
    def test_dog_creation_with_valid_data(self):
        """Проверка создания Dog с валидными данными и установкой user из контекста."""
        initial_count = Dog.objects.count()
        
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
        
        # Проверка наличия ошибки для несуществующего PK
        self.assertIn('breed', serializer.errors)
        self.assertEqual(Dog.objects.count(), 1)

    # ------------------ DogUpdateSerializer (Обновление) ------------------
    def test_dog_update_with_valid_data(self):
        """Проверка обновления Dog с валидными данными."""
        update_data = self.valid_dog_data.copy()
        update_data['name'] = 'Новое Имя'
        
        serializer = DogUpdateSerializer(instance=self.dog, data=update_data, context=self.context)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        
        dog_instance = serializer.save()

        # Проверка, что имя обновилось, а user остался прежним (read_only)
        self.dog.refresh_from_db() # Обновляем объект из базы для проверки
        self.assertEqual(self.dog.name, 'Новое Имя')
        self.assertEqual(self.dog.user, self.user)
        
    def test_dog_update_user_is_read_only(self):
        """Проверка, что поле 'user' игнорируется при попытке обновления."""
        initial_user_id = self.dog.user.id
        update_data = self.valid_dog_data.copy()
        update_data['user'] = self.another_user.id # Попытка сменить пользователя
        update_data['name'] = 'Test'
        
        serializer = DogUpdateSerializer(instance=self.dog, data=update_data, context=self.context)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()

        # Пользователь не должен был измениться
        self.dog.refresh_from_db()
        self.assertEqual(self.dog.user.id, initial_user_id)

# 3. ТЕСТЫ СЕРИАЛИЗАТОРОВ ДЛЯ МОДЕЛИ OWNER

class OwnerSerializerTest(SerializerTestSetup):
    
    def test_owner_creation_sets_user_from_context(self):
        """Проверка, что поле 'user' устанавливается из self.context['request'].user при создании."""
        initial_count = Owner.objects.count()
        
        # Передаем self.context для установки request.user
        serializer = OwnerSerializer(data=self.valid_owner_data, context=self.context)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        
        owner_instance = serializer.save()
        # Проверка, что user установлен из контекста
        self.assertEqual(Owner.objects.count(), initial_count + 1)
        self.assertEqual(owner_instance.user, self.user)
        
    def test_owner_creation_user_is_read_only(self):
        """Проверка, что переданный 'user' игнорируется, а берется из контекста."""
        data_with_wrong_user = self.valid_owner_data.copy()
        data_with_wrong_user['user'] = self.another_user.id # Попытка передать неверный ID
        
        serializer = OwnerSerializer(data=data_with_wrong_user, context=self.context)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        owner_instance = serializer.save()

        # User должен быть self.user (из контекста), а не self.another_user
        self.assertEqual(owner_instance.user, self.user)

# 4. ТЕСТЫ ПРОСТЫХ СЕРИАЛИЗАТОРОВ (Breed, Hobby, Country)

class SimpleSerializersTest(SerializerTestSetup):
    
    # ------------------ BreedSerializer (Полный) ------------------
    def test_breed_serialization(self):
        """Проверка сериализации объекта Breed."""
        serializer = BreedSerializer(instance=self.breed)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name']))
        self.assertEqual(data['name'], self.breed.name)

    def test_breed_deserialization(self):
        """Проверка десериализации (создания) объекта Breed."""
        initial_count = Breed.objects.count()
        serializer = BreedSerializer(data=self.valid_breed_data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        serializer.save()
        self.assertEqual(Breed.objects.count(), initial_count + 1)
        
    # ------------------ HobbySerializer ------------------
    def test_hobby_serialization(self):
        """Проверка сериализации объекта Hobby."""
        serializer = HobbySerializer(instance=self.hobby)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name_hobby']))
        self.assertEqual(data['name_hobby'], self.hobby.name_hobby)

    # ------------------ CountrySerializer ------------------
    def test_country_serialization(self):
        """Проверка сериализации объекта Country."""
        serializer = CountrySerializer(instance=self.country)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'country']))
        self.assertEqual(data['country'], self.country.country)

# 5. ТЕСТЫ СЕРИАЛИЗАТОРА АУТЕНТИФИКАЦИИ

class LoginSerializerTest(SerializerTestSetup):
    
    def test_login_serializer_valid_data(self):
        """Проверка валидации данных с правильными полями."""
        data = {'username': 'testuser', 'password': 'testpassword'}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_login_serializer_missing_fields(self):
        """Проверка валидации с отсутствующими обязательными полями."""
        # Отсутствует 'password'
        data = {'username': 'testuser'}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        
        # Отсутствует 'username'
        data = {'password': 'testpassword'}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

