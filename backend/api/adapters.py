from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # Roda a lógica padrão primeiro
        user = super().populate_user(request, sociallogin, data)
        
        # Se não tiver username, pega a primeira parte do email (ex: joao do joao@gmail.com)
        if not user.username:
            user.username = user.email.split('@')[0]
        
        return user

    def is_open_for_signup(self, request, sociallogin):
        return True