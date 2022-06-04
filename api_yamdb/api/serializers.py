from django.conf import settings
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from reviews.models import (Categories, Comments, Genres, Ratings, Reviews,
                            Titles, User)


class FullUserSerializer(serializers.ModelSerializer):
    """Serializer for user model with all fields"""
    class Meta:
        fields = ('first_name', 'last_name', 'username',
                  'bio', 'role', 'email')
        model = User


class UserEmailCodeSerializer(serializers.Serializer):
    """Serializer for checking code from user."""
    username = serializers.CharField(required=True, max_length=128)
    confirmation_code = serializers.IntegerField(required=True)

    def validate(self, data):
        confirmation_code = data['confirmation_code']
        user = get_object_or_404(User, username=data['username'])
        if confirmation_code == settings.RESET_CONFIRMATION_CODE:
            raise serializers.ValidationError(
                (f'Данный код подтверждения уже использовался.'
                 f'Получите новый через регистрацию'))
        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError('Неверный код подтверждения')
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registrations with email and username."""

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Username "me" уже занято.')
        return data


class TitleSerialiser(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genres.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Categories.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Titles


class GenreSerialiser(serializers.ModelSerializer):

    class Meta:
        model = Genres
        exclude = ('id',)
        lookup_fields = 'slug'
        extra_kwargs = {
            'url': {'lookup_fields': 'slug'}
        }


class CategorySerialiser(serializers.ModelSerializer):

    class Meta:
        model = Categories
        exclude = ('id',)
        lookup_fields = 'slug'
        extra_kwargs = {
            'url': {'lookup_fields': 'slug'}
        }


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerialiser(many=True)
    category = CategorySerialiser()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'category', 'genre', 'rating')
        model = Titles


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Titles.objects.all(),
        read_only=False,
        required=False
    )

    class Meta:
        fields = '__all__'
        model = Reviews

    def create(self, validated_data):
        if self.is_valid:
            title = validated_data.get('title')
            score = validated_data.get('score')
            rating_obj, created = Ratings.objects.get_or_create(title=title)
            rating_obj.count_score = rating_obj.count_score + 1
            rating_obj.summ_score = rating_obj.summ_score + score
            if rating_obj.count_score == 0:
                rating_obj.rating = 0
            else:
                rating_obj.rating = (rating_obj.summ_score
                                     / rating_obj.count_score)
            rating_obj.save()
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Titles.objects.all(),
        read_only=False,
        required=False
    )
    review = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Reviews.objects.all(),
        read_only=False,
        required=False
    )

    class Meta:
        fields = '__all__'
        model = Comments
        read_only_fields = ('author',)
