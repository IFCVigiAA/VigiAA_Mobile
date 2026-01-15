from django.contrib import admin
from .models import DengueFocus, FocusImage, Profile

# Configuração para mostrar as fotos dentro do Foco no Admin
class FocusImageInline(admin.TabularInline):
    model = FocusImage
    extra = 0 # Não mostrar linhas vazias extras

class DengueFocusAdmin(admin.ModelAdmin):
    # Colunas que vão aparecer na lista
    list_display = ('id', 'street', 'city', 'user', 'created_at')
    # Filtros laterais
    list_filter = ('city', 'created_at')
    # Barra de pesquisa
    search_fields = ('street', 'description', 'user__username')
    # Mostra as fotos dentro do cadastro do foco
    inlines = [FocusImageInline]

admin.site.register(DengueFocus, DengueFocusAdmin)
admin.site.register(Profile)