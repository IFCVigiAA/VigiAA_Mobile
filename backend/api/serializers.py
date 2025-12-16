from rest_framework import serializers
from django.contrib.auth.models import User, update_last_login  
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

# ESTA ERA A LINHA QUE FALTAVA (para o Login funcionar):
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token inválido ou expirado", 401)

            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError("Token inválido ou usuário não encontrado", 401)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user) #gera o token
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        update_last_login(None, self.user)
        
        return data