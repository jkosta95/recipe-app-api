from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import Ingredient, Recipe

from recipe import serializers


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """Manage ingredients in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """ Create a new ingredinet"""
        serializer.save(user=self.request.user)

class RecipeViewSet(viewsets.ModelViewSet):
    """ Manage recipes in the database"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )

    def _params_to_ints(self, qs):
        """ Convert a list of string IDs to a list of ints"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """ Retrieve the recipes for the authenticated user """
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """ Return appropriate serializer class """
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new recipe"""
        serializer.save(user=self.request.user)
