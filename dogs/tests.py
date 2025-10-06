from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

# Убедитесь, что ваш путь импорта моделей правильный
from dogs.models import Breed, Dog, Owner, Hobby, Country

# Получаем модель пользователя Django
User = get_user_model()

# ==============================================================================
# 1. БАЗОВАЯ НАСТРОЙКА ТЕСТОВЫХ ДАННЫХ
# ==============================================================================

class BaseAPITestSetup(APITestCase):
    """Базовый класс для создания тестовых данных и общих URL."""
    
    def setUp(self):
        super().setUp()
        
        # Создание тестовых пользователей
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

        # --- Данные для POST/PUT запросов ---
        self.valid_dog_data = {
            'name': 'Шарик',
            'breed': self.breed.id,
            'owner': self.owner.id,
            'country': self.country.id,
            'hobby': self.hobby.id,
        }
        
        self.valid_owner_data = {
            'first_name': 'Анна',
            'last_name': 'Сидорова',
            'phone_number': '89991112233',
        }
        
        self.valid_breed_data = {'name': 'Пудель'}

        # --- URL-адреса, соответствующие DefaultRouter ---
        self.DOG_LIST_URL = '/api/dogs/'
        self.OWNER_LIST_URL = '/api/owner/'
        self.BREED_LIST_URL = '/api/breed/'
        self.COUNTRY_LIST_URL = '/api/country/'
        self.HOBBY_LIST_URL = '/api/hobby/'

# ==============================================================================
# 2. ТЕСТЫ API ДЛЯ DOG ( dogs )
# ==============================================================================

class DogViewTest(BaseAPITestSetup):
    """Тесты API для DogsViewset."""
    
    def test_list_dogs_authenticated(self):
        """Проверка получения списка собак (GET /api/dogs/)."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.DOG_LIST_URL, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_create_dog_authenticated(self):
        """Проверка создания собаки (POST /api/dogs/)."""
        self.client.force_authenticate(user=self.user)
        initial_count = Dog.objects.count()
        
        response = self.client.post(self.DOG_LIST_URL, self.valid_dog_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dog.objects.count(), initial_count + 1)
        
    def test_update_dog_authenticated(self):
        """Проверка обновления собаки (PUT /api/dogs/{id}/)."""
        self.client.force_authenticate(user=self.user)
        update_data = self.valid_dog_data.copy()
        update_data['name'] = 'Новое Имя'
        
        response = self.client.put(f'{self.DOG_LIST_URL}{self.dog.id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dog.refresh_from_db()
        self.assertEqual(self.dog.name, 'Новое Имя')

# ==============================================================================
# 3. ТЕСТЫ API ДЛЯ OWNER ( owner )
# ==============================================================================

class OwnerViewTest(BaseAPITestSetup):
    """Тесты API для OwnersViewset."""
    
    def test_create_owner_authenticated(self):
        """Проверка создания владельца (POST /api/owner/)."""
        self.client.force_authenticate(user=self.another_user) # Используем другого пользователя для чистоты
        initial_count = Owner.objects.count()
        
        response = self.client.post(self.OWNER_LIST_URL, self.valid_owner_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Owner.objects.count(), initial_count + 1)
        # Проверяем, что user установлен корректно (он должен быть self.another_user)
        self.assertEqual(Owner.objects.last().user, self.another_user)

    def test_retrieve_owner_detail(self):
        """Проверка получения детальной информации о владельце (GET /api/owner/{id}/)."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(f'{self.OWNER_LIST_URL}{self.owner.id}/', format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Иван')

# ==============================================================================
# 4. ТЕСТЫ API ДЛЯ BREED ( breed )
# ==============================================================================

class BreedViewTest(BaseAPITestSetup):
    """Тесты API для BreedsViewset."""
    
    def test_list_breeds(self):
        """Проверка получения списка всех пород (GET /api/breed/)."""
        # Обычно доступен для всех
        response = self.client.get(self.BREED_LIST_URL, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        
    def test_create_breed_authenticated(self):
        """Проверка создания породы (POST /api/breed/)."""
        self.client.force_authenticate(user=self.user)
        initial_count = Breed.objects.count()
        
        response = self.client.post(self.BREED_LIST_URL, self.valid_breed_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Breed.objects.count(), initial_count + 1)

# ==============================================================================
# 5. ТЕСТЫ API ДЛЯ COUNTRY ( country )
# ==============================================================================

class CountryViewTest(BaseAPITestSetup):
    """Тесты API для CountryViewset."""
    
    def test_list_countries(self):
        """Проверка получения списка всех стран (GET /api/country/)."""
        response = self.client.get(self.COUNTRY_LIST_URL, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

# ==============================================================================
# 6. ТЕСТЫ API ДЛЯ HOBBY ( hobby )
# ==============================================================================

class HobbyViewTest(BaseAPITestSetup):
    """Тесты API для HobbyViewset."""
    
    def test_list_hobbies(self):
        """Проверка получения списка всех хобби (GET /api/hobby/)."""
        response = self.client.get(self.HOBBY_LIST_URL, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)