from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

# /api/recipe/recipes
#/api/recipe/recipes/1
#we are going to pass in this argument (id)
def detail_url(recipe_id):
    """ Return recipe detail URL """
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_ingredient(user, name="Cinnamon"):
    """ Create and return sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
    """ Create and return sample recipe"""
    defaults={
        'name':'Sample Recipe',
        'text': 'Some text about Recipe'
    }
    defaults.update(params)


    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """ Test unauthenticated recipe API access """

    def setUp(self):
        self.client=APIClient()

    def test_required_auth(self):
        """ Test that auth authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """ Test unauthenticated recipe API access """

    def setUp(self):
        self.client=APIClient()
        self.user = get_user_model().objects.create_user(
            'test@kosta.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retreive_recepies(self):
        """Test retreiving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ Test retrieving recepes for user"""
        user2 = get_user_model().objects.create_user(
            'other@kosta.com',
            'test1234'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer=RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """ Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.ingredients.add(sample_ingredient(user=self.user))

        #generate urls
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """ Test creating recipe """
        payload = {
            'name': 'Chocolate cheesecake',
            'text': 'Preparation takes 1h and 20 minutes and it is great'
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_ingredients(self):
        """ Test creating a recipe with ingredients """
        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'name' : 'THAI prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'text': 'some text about this recipe'
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """ Test updating a recipe with patch """
        recipe = sample_recipe(user=self.user)
        recipe.ingredients.add(sample_ingredient(user=self.user))
        new_ingredient = sample_ingredient(user=self.user, name='Something')
        payload = {
                'name':'Chicken tikka',
                'ingredients':[new_ingredient.id]
                }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.name, payload['name'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 1)
        self.assertIn(new_ingredient, ingredients)

    def test_full_update_recipe(self):
        """ Test updating a recipe with put """
        recipe = sample_recipe(user=self.user)
        recipe.ingredients.add(sample_ingredient(user=self.user))
        payload = {
            'name': 'Spaghetti',
            'text':'some other text about the recipe'
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.text, payload['text'])

        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 0)

    def test_filter_recipes_by_ingredients(self):
        """Test returning recipes with specific ingredients """
        recipe1 = sample_recipe(user=self.user, name="Thai vegetable curry")
        recipe2 = sample_recipe(user=self.user, name="Aubergine with tahini")
        ingredient1 = sample_ingredient(user=self.user, name='Something 1')
        ingredient2 = sample_ingredient(user=self.user, name='Something 2')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, name="Some fish")

        res = self.client.get(
                RECIPES_URL,
                {'ingredients': '{},{}'.format(ingredient1.id, ingredient2.id)}
                )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
