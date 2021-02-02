from rest_framework import serializers

from core.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for an ingredient object"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)

class RecipeSerializer(serializers.ModelSerializer):
    """ Serialize a recipe"""

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset = Ingredient.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'ingredients',)
        read_only_fields = ('id', )

class RecipeDetailSerializer(RecipeSerializer):
    """ Serialize a recipe detail """
    ingredients = IngredientSerializer(many=True, read_only=True)
    
