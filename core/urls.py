from django.urls import path
from . import views
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views
from .views import aluno_detail, perfil_aluno, turma_detail, turma_detail_prof, adicionar_recado, visualizar_recados, professor_view, pagina_inicial_prof

urlpatterns = [
    path('', views.login_view, name='home'),  
    path('login/', views.login_view, name='login'),  
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 

    path('aluno/', views.pagina_inicial_aluno, name='pagina_inicial_aluno'),  
    path('turma/<int:turma_id>/detail/', views.turma_detail, name='turma_detail'),  
    path('aluno/<int:aluno_id>/', views.aluno_detail, name='aluno_detail'),  

    path('aluno/<int:turma_id>/visualizar-recados/', views.visualizar_recados, name='visualizar_recados'),

    path('professor/', views.pagina_inicial_prof, name='pagina_inicial_prof'),  
    path('turma/<int:turma_id>/', views.turma_detail_prof, name='turma_detail_prof'),  
    path('turma/<int:turma_id>/adicionar-recado/', views.adicionar_recado, name='adicionar_recado'),
    path('turma/<int:turma_id>/visualizar-recados/', views.visualizar_recados, name='visualizar_recados'), 

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
