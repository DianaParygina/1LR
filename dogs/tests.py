from django.test import TestCase
from django.contrib.auth import get_user_model
from dogs.models import Breed, Dog, Owner, Country, Hobby

# Получаем модель пользователя Django для создания владельцев
User = get_user_model()

class ModelTests(TestCase):
    """
    Создание общих объектов, которые будут использоваться во всех тестах
    """
    def setUp(self):
        # 1. Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )
        
        # 2. Создаем базовые связанные объекты
        self.breed = Breed.objects.create(name="Лабрадор")
        self.country = Country.objects.create(country="Россия")
        self.hobby = Hobby.objects.create(name_hobby="Аджилити")
        
        # 3. Создаем владельца, привязанного к пользователю
        self.owner = Owner.objects.create(
            first_name="Иван", 
            last_name="Петров", 
            phone_number="89001234567",
            user=self.user
        )
        
        # 4. Создаем собаку, привязанную ко всем объектам
        self.dog = Dog.objects.create(
            name="Шарик",
            breed=self.breed,
            owner=self.owner,
            country=self.country,
            hobby=self.hobby,
            user=self.user
        )

# ----------------------------------------------------------------------

class BreedModelTest(ModelTests):
    """
    Тесты для модели Breed (Порода).
    """

    def test_breed_creation_and_fields(self):
        """1. Проверяет, что порода создана и поле 'name' корректно."""
        self.assertEqual(self.breed.name, "Лабрадор")

    def test_breed_str_representation(self):
        """2. Проверяет строковое представление (str) породы."""
        self.assertEqual(str(self.breed), "Лабрадор")
        
# ----------------------------------------------------------------------

class CountryModelTest(ModelTests):
    """
    Тесты для модели Country (Страна проживания).
    """
    
    def test_country_creation_and_fields(self):
        """3. Проверяет, что страна создана и поле 'country' корректно."""
        self.assertEqual(self.country.country, "Россия")

    def test_country_str_representation(self):
        """4. Проверяет строковое представление (str) страны."""
        self.assertEqual(str(self.country), "Россия")
        
# ----------------------------------------------------------------------

class HobbyModelTest(ModelTests):
    """
    Тесты для модели Hobby (Хобби).
    """
    
    def test_hobby_creation_and_fields(self):
        """5. Проверяет, что хобби создано и поле 'name_hobby' корректно."""
        self.assertEqual(self.hobby.name_hobby, "Аджилити")

    def test_hobby_str_representation(self):
        """6. Проверяет строковое представление (str) хобби."""
        self.assertEqual(str(self.hobby), "Аджилити")

# ----------------------------------------------------------------------

class OwnerModelTest(ModelTests):
    """
    Тесты для модели Owner (Владелец).
    """

    def test_owner_creation_and_fields(self):
        """7. Проверяет создание владельца и основные поля."""
        self.assertEqual(self.owner.first_name, "Иван")
        self.assertEqual(self.owner.last_name, "Петров")
        self.assertEqual(self.owner.phone_number, "89001234567")

    def test_owner_str_representation(self):
        """8. Проверяет строковое представление (str) владельца."""
        self.assertEqual(str(self.owner), "Иван Петров")

    def test_owner_user_name_property(self):
        """9. Проверяет корректность @property user_name."""
        self.assertEqual(self.owner.user_name, "testuser")
        
# ----------------------------------------------------------------------

class DogModelTest(ModelTests):
    """
    Тесты для модели Dog (Собака).
    """

    def test_dog_creation_and_fields(self):
        """10. Проверяет создание собаки и поле 'name'."""
        self.assertEqual(self.dog.name, "Шарик")
        self.assertEqual(self.dog.user, self.user)

    def test_dog_relationships(self):
        """11. Проверяет корректность внешних ключей (связей)."""
        self.assertEqual(self.dog.breed.name, "Лабрадор")
        self.assertEqual(self.dog.owner.first_name, "Иван")
        self.assertEqual(self.dog.country.country, "Россия")
        self.assertEqual(self.dog.hobby.name_hobby, "Аджилити")
        
    def test_dog_str_representation(self):
        """12. Проверяет строковое представление (str) собаки."""
        self.assertEqual(str(self.dog), "Шарик")
        
    def test_related_name_access(self):
        """13. Проверяет обратный доступ через related_name."""
        # Проверка, что через владельца можно получить список его собак
        self.assertIn(self.dog, self.owner.dogs.all())
        # Проверка, что через страну можно получить список собак
        self.assertIn(self.dog, self.country.dog_country.all())
        # Проверка, что через хобби можно получить список собак
        self.assertIn(self.dog, self.hobby.dog_hobby.all())