from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

from cookbooks.models import Recipe

from .serializers import ReadonlyCookbookSerializer, ReadonlyRecipeSerializer, RecipeSerializer


class RecipeListAPIView(generics.ListCreateAPIView):
    @swagger_auto_schema(
        operation_description="Returns the list of all available recipes.",
        manual_parameters=[
            openapi.Parameter(
                "order", openapi.IN_QUERY, type=openapi.TYPE_STRING, enum=["rating", "created_at"]
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Creates a recipe object (SU only).",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                default="Bearer <access>",
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.method == "POST":
            return Recipe.objects.all()
        order = self.request.GET.get("order")
        return Recipe.objects.all().order_by(f"-{order}") if order else Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecipeSerializer
        return ReadonlyRecipeSerializer

    def get_authenticators(self):
        if self.request.method == "POST":
            return [auth() for auth in [JWTAuthentication]]
        return []

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                permission()
                for permission in [permissions.IsAuthenticated, permissions.IsAdminUser]
            ]
        return []


class RecipeRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ReadonlyRecipeSerializer
    queryset = Recipe.objects.all()

    @swagger_auto_schema(
        operation_description="Returns a recipe object with the specified id.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MyCookbookAPIView(generics.RetrieveAPIView):
    serializer_class = ReadonlyCookbookSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user.cookbook

    @swagger_auto_schema(
        operation_description="Returns an authorized user's cookbook data with recipes.",
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                default="Bearer <access>",
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
