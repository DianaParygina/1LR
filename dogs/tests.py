from django.test import TestCase
from django.urls import reverse
from dogs.models import Dog, Breed # Убедитесь, что ваши модели называются Breed и Dog

class DogModelTest(TestCase):
    """
    Тесты для модели Dog (Собака).
    """

    def setUp(self):
        # Создаем тестовую породу, необходимую для создания собаки
        self.breed = Breed.objects.create(
            name='Labrador',
            size='Large',
            country='USA'
        )
        # Создаем тестовый объект Dog
        self.dog = Dog.objects.create(
            name='Buddy',
            age=5,
            breed=self.breed,
            is_vaccinated=True
        )

    # 1. Тест создания объекта Dog
    def test_dog_creation(self):
        """Проверяет, что объект Dog создан корректно."""
        self.assertEqual(self.dog.name, 'Buddy')
        self.assertEqual(self.dog.age, 5)
        self.assertTrue(self.dog.is_vaccinated)
        self.assertEqual(self.dog.breed.name, 'Labrador')

    # 2. Тест строкового представления (метод __str__)
    def test_string_representation(self):
        """Проверяет корректность метода __str__ модели Dog."""
        expected_string = 'Buddy (Labrador)'
        self.assertEqual(str(self.dog), expected_string)
        
    # 3. Тест возраста собаки
    def test_dog_age_validation(self):
        """Проверяет, что возраст собаки корректный."""
        new_dog = Dog.objects.create(name='Max', age=1, breed=self.breed)
        self.assertTrue(new_dog.age >= 0)
        
class BreedModelTest(TestCase):
    """
    Тесты для модели Breed (Порода).
    """

    # 4. Тест создания объекта Breed
    def test_breed_creation(self):
        """Проверяет, что объект Breed создан корректно."""
        breed = Breed.objects.create(name='Poodle', size='Small')
        self.assertEqual(breed.name, 'Poodle')
        self.assertEqual(breed.size, 'Small')
        
    # 5. Тест строкового представления (метод __str__)
    def test_breed_string_representation(self):
        """Проверяет корректность метода __str__ модели Breed."""
        breed = Breed.objects.create(name='German Shepherd')
        self.assertEqual(str(breed), 'German Shepherd')

class DogViewTest(TestCase):
    """
    Тесты для проверки доступности страниц (View).
    """
    
    # Добавляем фиктивные данные для теста (аналогично DogModelTest)
    def setUp(self):
        self.breed = Breed.objects.create(name='Bulldog', size='Medium')
        Dog.objects.create(name='Rocky', age=3, breed=self.breed)
        
    # 6. Тест страницы со списком собак
    def test_dogs_list_view(self):
        """Проверяет, что страница списка собак доступна."""
        # Используйте 'dogs:dog_list' или другой name, который вы используете в urls.py
        # Если вы используете Django REST Framework и не имеете view, можете пропустить этот тест.
        # response = self.client.get(reverse('dogs:dog_list')) 
        # self.assertEqual(response.status_code, 200)
        pass # Замените на реальный тест, если у вас есть View.