from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import update_last_login

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user) #gera o token
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        update_last_login(None, self.user)
        
        return data