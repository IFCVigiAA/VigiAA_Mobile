from rest_framework import serializers
from django.contrib.auth.models import User, update_last_login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            # Decodifica o ID
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            # Verifica o Token
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Token inválido ou expirado', 401)

            # Truque: Guardamos o usuário no "self" para usar na hora de salvar
            self.user = user
            
            # CORREÇÃO: Retornamos os dados (attrs), e não o usuário!
            return attrs 

        except Exception as e:
            raise AuthenticationFailed('Token inválido ou usuário não encontrado', 401)

    def save(self, **kwargs):
        # Aqui sim a gente salva a senha
        password = self.validated_data['password']
        
        self.user.set_password(password)
        self.user.save()
        
        return self.user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        update_last_login(None, self.user)
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("A senha atual está incorreta.")
        return value

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "A nova senha deve ser diferente da atual."})
        return attrs