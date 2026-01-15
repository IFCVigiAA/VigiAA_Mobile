from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- MODELO DE FOCO DE DENGUE ---
class DengueFocus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=50, blank=True, null=True)
    cep = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Foco em {self.street}, {self.city}"

def focus_image_path(instance, filename):
    return f'focus_photos/{instance.focus.id}/{filename}'

class FocusImage(models.Model):
    focus = models.ForeignKey(DengueFocus, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=focus_image_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

# --- MODELO DE PERFIL (FOTO DO USUÁRIO) ---
# Você provavelmente esqueceu de copiar esta parte aqui em baixo! 👇

def profile_image_path(instance, filename):
    return f'profile_photos/{instance.user.username}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to=profile_image_path, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

# Sinais para criar o perfil automaticamente
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)