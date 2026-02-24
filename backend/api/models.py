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

# --- ADICIONE ISTO NO FINAL DO SEU models.py ---

class DengueCase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Quem registrou
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Dados do Formulário
    notification_date = models.DateField()
    cep = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    neighborhood = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=20)
    birth_date = models.DateField()
    positive_test = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Caso em {self.city} ({self.notification_date})"
    
class PositiveDengueCase(models.Model):
    # Liga este paciente ao caso de dengue base que acabamos de criar
    dengue_case = models.OneToOneField(DengueCase, on_delete=models.CASCADE, related_name='positive_details')
    patient_name = models.CharField(max_length=150)
    cpf = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20)
    test_location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paciente Positivo: {self.patient_name}"