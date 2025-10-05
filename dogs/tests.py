from django.test import TestCase
from dogs.models import Breed, Dog, Hobby, Owner, Country
from model_bakery import baker
from rest_framework.test import APIClient


# Create your tests here.
class DogsViewsetTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list(self):
        self.assertEqual(1,1)

    def test_get_list(self):
        brd = baker.make("dogs.Breed")
        dog = baker.make("Dog", breed=brd)

        r = self.client.get('/api/dogs/')
        data = r.json()
        print(data)

        assert dog.name == data[0]['name']
        assert dog.id == data[0]['id']
        assert dog.breed.id == data[0]['breed']['id']
        assert len(data) == 1


    def test_create_dog(self):
        brd = baker.make("dogs.Breed")
        hb = baker.make("dogs.Hobby")
        cnt = baker.make("dogs.Country")
        own = baker.make("dogs.Owner")

        r = self.client.post("/api/dogs/", {
            "name": "Собака",
            "breed": brd.id,
            "hobby": hb.id,
            "country": cnt.id,
            "owner": own.id
        })

        new_dog_id = r.json()['id']

        dogs = Dog.objects.all()
        assert len(dogs) == 1

        new_dog = Dog.objects.filter(id=new_dog_id).first()
        assert new_dog.name == "Собака"
        assert new_dog.breed == brd
        assert new_dog.hobby == hb
        assert new_dog.country == cnt
        assert new_dog.owner == own

    def test_delete_dog(self):
        dogs = baker.make("Dog", 10)
        r = self.client.get("/api/dogs/")
        data = r.json()
        assert len(data) == 10

        dog_id_to_delete = dogs[3].id
        self.client.delete(f'/api/dogs/{dog_id_to_delete}/')

        r = self.client.get("/api/dogs/")
        data = r.json()
        assert len(data) == 9

        assert dog_id_to_delete not in [i['id'] for i in data] 


    def test_update_dog(self):
        brd = baker.make("dogs.Breed")
        hb = baker.make("dogs.Hobby")
        cnt = baker.make("dogs.Country")
        own = baker.make("dogs.Owner")

        dogs = baker.make("Dog", 10, breed = brd, hobby = hb, country = cnt, owner = own)
        dog: Dog = dogs[2]

        r = self.client.get(f'/api/dogs/{dog.id}/')
        data = r.json()
        assert data['name'] == dog.name
        assert data['breed']['id'] == dog.breed.id 
        assert data['hobby']['id'] == dog.hobby.id 
        assert data['country']['id'] == dog.country.id 
        assert data['owner']['id'] == dog.owner.id 

        r = self.client.patch(
            f'/api/dogs/{dog.id}/',
            {
                "name": "Коржик",
                "breed": brd.id,
                "hobby": hb.id,
                "country": cnt.id,
                "owner": own.id
            }
        )
        assert r.status_code == 200

        r = self.client.get(f'/api/dogs/{dog.id}/')
        data = r.json()
        assert data['name'] == "Коржик"
        assert data['breed']['id'] == brd.id 
        assert data['hobby']['id'] == hb.id 
        assert data['country']['id'] == cnt.id 
        assert data['owner']['id'] == own.id 

        dog.refresh_from_db()
        assert data['name'] == dog.name
        assert data['breed']['id'] == brd.id 
        assert data['hobby']['id'] == hb.id 
        assert data['country']['id'] == cnt.id 
        assert data['owner']['id'] == own.id



class BreedViewsetTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list(self):
        self.assertEqual(1,1)

    def test_get_list2(self):
        brd = baker.make("dogs.Breed")

        r = self.client.get('/api/breed/')
        data = r.json()
        print(data)

        assert brd.name == data[0]['name']
        assert len(data) == 1


    def test_create_breed(self):
        r = self.client.post("/api/breed/", {
            "name": "Собака2",
        })

        new_breed_id = r.json()['id']

        breeds = Breed.objects.all()
        assert len(breeds) == 1

        new_breed = Breed.objects.filter(id=new_breed_id).first()
        assert new_breed.name == "Собака2"


    def test_delete_breed(self):
        breeds = baker.make("Breed", 10)
        r = self.client.get("/api/breed/")
        data = r.json()
        assert len(data) == 10

        breed_id_to_delete = breeds[3].id
        self.client.delete(f'/api/breed/{breed_id_to_delete}/')

        r = self.client.get("/api/breed/")
        data = r.json()
        assert len(data) == 9

        assert breed_id_to_delete not in [i['id'] for i in data] 


    def test_update_breed(self):
        breeds = baker.make("Breed", 10)
        breed: Breed = breeds[2]

        r = self.client.get(f'/api/breed/{breed.id}/')
        data = r.json()
        assert data['name'] == breed.name 

        r = self.client.patch(
            f'/api/breed/{breed.id}/',
            {
                "name": "Собака2",
            }
        )
        assert r.status_code == 200

        r = self.client.get(f'/api/breed/{breed.id}/')
        data = r.json()
        assert data['name'] == "Собака2"

        breed.refresh_from_db()
        assert data['name'] == breed.name


class OwnerViewsetTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list(self):
        self.assertEqual(1,1)

    def test_get_list3(self):
        own = baker.make("dogs.Owner")

        r = self.client.get('/api/owner/')
        data = r.json()
        print(data)

        assert own.first_name == data[0]['first_name']
        assert own.last_name == data[0]['last_name']
        assert own.phone_number == data[0]['phone_number']
        assert len(data) == 1


    def test_create_owner(self):
        r = self.client.post("/api/owner/", {
            "first_name": "Петя",
            "last_name": "Иванов",
            "phone_number": "34545656787"
        })

        new_owner_id = r.json()['id']

        owners = Owner.objects.all()
        assert len(owners) == 1

        new_owner = Owner.objects.filter(id=new_owner_id).first()
        assert new_owner.first_name == "Петя"
        assert new_owner.last_name == "Иванов"
        assert new_owner.phone_number == "34545656787"


    def test_delete_owner(self):
        owners = baker.make("Owner", 10)
        r = self.client.get("/api/owner/")
        data = r.json()
        assert len(data) == 10

        owner_id_to_delete = owners[3].id
        self.client.delete(f'/api/owner/{owner_id_to_delete}/')

        r = self.client.get("/api/owner/")
        data = r.json()
        assert len(data) == 9

        assert owner_id_to_delete not in [i['id'] for i in data] 


    def test_update_owner(self):
        owners = baker.make("Owner", 10)
        owner: Owner = owners[2]

        r = self.client.get(f'/api/owner/{owner.id}/')
        data = r.json()
        assert data['first_name'] == owner.first_name 
        assert data['last_name'] == owner.last_name 
        assert data['phone_number'] == owner.phone_number 

        r = self.client.patch(
            f'/api/owner/{owner.id}/',
            {
                "first_name": "Петя",
                "last_name": "Иванов",
                "phone_number": "34545656787",
            }
        )
        assert r.status_code == 200

        r = self.client.get(f'/api/owner/{owner.id}/')
        data = r.json()
        assert data['first_name'] == "Петя"
        assert data['last_name'] == "Иванов"
        assert data['phone_number'] == "34545656787"

        owner.refresh_from_db()
        assert data['first_name'] == owner.first_name
        assert data['last_name'] == owner.last_name
        assert data['phone_number'] == owner.phone_number

class CountryViewsetTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list(self):
        self.assertEqual(1,1)

    def test_get_list2(self):
        cnt = baker.make("dogs.Country")

        r = self.client.get('/api/country/')
        data = r.json()
        print(data)

        assert cnt.country == data[0]['country']
        assert len(data) == 1


    def test_create_country(self):
        r = self.client.post("/api/country/", {
            "country": "СССССР",
        })

        new_country_id = r.json()['id']

        countries = Country.objects.all()
        assert len(countries) == 1

        new_country = Country.objects.filter(id=new_country_id).first()
        assert new_country.country == "СССССР"


    def test_delete_country(self):
        countries = baker.make("Country", 10)
        r = self.client.get("/api/country/")
        data = r.json()
        assert len(data) == 10

        country_id_to_delete = countries[3].id
        self.client.delete(f'/api/country/{country_id_to_delete}/')

        r = self.client.get("/api/country/")
        data = r.json()
        assert len(data) == 9

        assert country_id_to_delete not in [i['id'] for i in data] 


    def test_update_country(self):
        countries = baker.make("Country", 10)
        country: Country = countries[2]

        r = self.client.get(f'/api/country/{country.id}/')
        data = r.json()
        assert data['country'] == country.country 

        r = self.client.patch(
            f'/api/country/{country.id}/',
            {
                "country": "СССССР",
            }
        )
        assert r.status_code == 200

        r = self.client.get(f'/api/country/{country.id}/')
        data = r.json()
        assert data['country'] == "СССССР"

        country.refresh_from_db()
        assert data['country'] == country.country


class HobbyViewsetTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_list(self):
        self.assertEqual(1,1)

    def test_get_list3(self):
        hb = baker.make("dogs.Hobby")

        r = self.client.get('/api/hobby/')
        data = r.json()
        print(data)

        assert hb.name_hobby == data[0]['name_hobby']
        assert len(data) == 1


    def test_create_hobby(self):
        r = self.client.post("/api/hobby/", {
            "name_hobby": "Сон",
        })

        new_hobby_id = r.json()['id']

        hobbies = Hobby.objects.all()
        assert len(hobbies) == 1

        new_hobby = Hobby.objects.filter(id=new_hobby_id).first()
        assert new_hobby.name_hobby == "Сон"


    def test_delete_hobby(self):
        hobbies = baker.make("Hobby", 10)
        r = self.client.get("/api/hobby/")
        data = r.json()
        assert len(data) == 10

        hobby_id_to_delete = hobbies[3].id
        self.client.delete(f'/api/hobby/{hobby_id_to_delete}/')

        r = self.client.get("/api/hobby/")
        data = r.json()
        assert len(data) == 9

        assert hobby_id_to_delete not in [i['id'] for i in data] 


    def test_update_hobby(self):
        hobbies = baker.make("Hobby", 10)
        hobby: Hobby = hobbies[2]

        r = self.client.get(f'/api/hobby/{hobby.id}/')
        data = r.json()
        assert data['name_hobby'] == hobby.name_hobby

        r = self.client.patch(
            f'/api/hobby/{hobby.id}/',
            {
                "name_hobby": "Сон",
            }
        )
        assert r.status_code == 200

        r = self.client.get(f'/api/hobby/{hobby.id}/')
        data = r.json()
        assert data['name_hobby'] == "Сон"

        hobby.refresh_from_db()
        assert data['name_hobby'] == hobby.name_hobby