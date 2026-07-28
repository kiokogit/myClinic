from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()

class UserListSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'


    def validate_username(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
        help_text="Username or email"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password"
    )

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class SignUpSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField()
    username = serializers.EmailField()
    other_names = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gender = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    residence = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user_type = serializers.CharField()
    date_of_birth = serializers.DateField(required=False, allow_null=True)


