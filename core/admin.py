from django.contrib import admin
from django.utils.html import mark_safe
from .models import Aluno, Conta, Professor, Sala, ContaSalaLivre, HorarioLivre, Turma, Recado, Anuncio,Manuais_Profs, Eventos

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_aluno', 'user', 'get_turmas')
    search_fields = ('nome_aluno', 'user__username')
    ordering = ('nome_aluno',)

    def get_turmas(self, obj):
        return ", ".join([turma.nome_turma for turma in obj.turmas_rel.all()])
    get_turmas.short_description = 'Turmas'

@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome','link')
    search_fields = ('nome',)

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome_professor', 'get_turmas')
    search_fields = ('nome_professor',)

    def get_turmas(self, obj):
        return ", ".join([turma.nome_turma for turma in obj.turmas_ministradas.all()])
    get_turmas.short_description = 'Turmas Ministradas'

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'capacidade')
    search_fields = ('nome',)
    ordering = ('nome',)

@admin.register(ContaSalaLivre)
class ContaSalaLivreAdmin(admin.ModelAdmin):
    list_display = ('id', 'dia_semana', 'horario_inicio', 'horario_fim', 'status_ocupacao', 'descricao', 'conta', 'sala')
    search_fields = ('descricao', 'conta__nome', 'sala__nome')
    list_filter = ('dia_semana', 'ocupado', 'conta', 'sala')

    def status_ocupacao(self, obj):
        if obj.ocupado:
            return mark_safe('<span style="color: red;">❌ Ocupado</span>')
        return mark_safe('<span style="color: green;">✔️ Livre</span>')
    status_ocupacao.short_description = 'Status'

@admin.register(HorarioLivre)
class HorarioLivreAdmin(admin.ModelAdmin):
    list_display = ('id', 'dia_semana', 'horario_inicio', 'horario_fim', 'status_ocupacao', 'ocupacao_tipo', 'ocupacao_nome', 'professor')
    search_fields = ('ocupacao_tipo', 'ocupacao_nome', 'professor__nome_professor')
    list_filter = ('dia_semana', 'ocupado', 'professor')

    def status_ocupacao(self, obj):
        if obj.ocupado:
            return mark_safe('<span>❌ Ocupado</span>')
        return mark_safe('<span>✔️ Livre</span>')
    status_ocupacao.short_description = 'Status'

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_turma', 'professor_responsavel', 'horario_livre', 'conta_sala_livre', 'card_link')
    search_fields = ('nome_turma', 'professor_responsavel__nome_professor')
    list_filter = ('professor_responsavel', 'conta_sala_livre', 'card_link', 'horario_livre')

    fieldsets = (
        (None, {
            'fields': ('nome_turma', 'professor_responsavel', 'conta_sala_livre', 'horario_livre', 'card_link')
        }),
        ('Alunos', {
            'fields': ('alunos',),
            'description': 'Selecione os Alunos que estão nesta Turma'
        }),
    )
    
    filter_horizontal = ('alunos',)

@admin.register(Recado)
class RecadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'conteudo', 'data', 'turma')
    search_fields = ('conteudo',)  # Transformado em uma tupla com vírgula no final
    list_filter = ('turma', 'data')  # Filtros para facilitar a busca

class AnuncioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'imagem_preview')  # Adiciona a pré-visualização da imagem
    search_fields = ('titulo',)

    def imagem_preview(self, obj):
        if obj.imagem:
            return mark_safe('<img src="{}" width="150" height="auto" />'.format(obj.imagem.url))
        return "(Nenhuma imagem disponível)"
    
    imagem_preview.short_description = 'Pré-visualização'  # Define um título para a coluna

admin.site.register(Anuncio, AnuncioAdmin)

@admin.register(Manuais_Profs)
class PdfAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_upload')

@admin.register(Eventos)
class EventosAdmin(admin.ModelAdmin):

    list_display = ('titulo', 'local', 'data', 'conta_sala_livre')  
    ordering = ('-data',)
    search_fields = ('titulo', 'local')  
    list_filter = ('data', 'conta_sala_livre') 


    fields = ('titulo', 'local', 'data', 'conta_sala_livre')

