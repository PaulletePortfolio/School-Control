from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

class Conta(models.Model):
    nome = models.CharField(max_length=100)
    link = models.URLField(max_length=200, default='...')

    def __str__(self):
        return self.nome

class Sala(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.PositiveIntegerField(default=10)
    
    def __str__(self):
        return self.nome

class HorarioLivre(models.Model):
    DIAS_SEMANA_CHOICES = [
        ('segunda', 'SEG'),
        ('terca', 'TER'),
        ('quarta', 'QUA'),
        ('quinta', 'QUI'),
        ('sexta', 'SEX'),
        ('sabado', 'SAB'),
        ('domingo', 'DOM'),
    ]
    
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA_CHOICES)
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE, related_name='horarios_livres')
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    ocupado = models.BooleanField(default=False)
    ocupacao_tipo = models.CharField(max_length=50, blank=True, null=True)
    ocupacao_nome = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.dia_semana} {self.horario_inicio} - {self.horario_fim} (Prof: {self.professor})"

class ContaSalaLivre(models.Model):
    conta = models.ForeignKey('Conta', null=True, blank=True, on_delete=models.CASCADE)
    sala = models.ForeignKey('Sala', null=True, blank=True, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=10)
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    ocupado = models.BooleanField(default=False)
    ocupacao_tipo = models.CharField(max_length=50, blank=True, null=True)
    ocupacao_nome = models.CharField(max_length=100, blank=True, null=True)
    descricao = models.CharField(max_length=100, default='...')

    def __str__(self):
        return f"{self.dia_semana} {self.horario_inicio} - {self.horario_fim} (Conta: {self.conta}, Sala: {self.sala})"

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=' ') 
    nome_professor = models.CharField(max_length=100, default='...')

    def __str__(self):
        return self.nome_professor

class Turma(models.Model):
    card_link = models.URLField(max_length=200)
    alunos = models.ManyToManyField('core.Aluno', related_name='turmas_rel', blank=True, verbose_name="Alunos na Turma")
    nome_turma = models.CharField(max_length=100)
    conta_sala_livre = models.ForeignKey('ContaSalaLivre', null=True, blank=True, on_delete=models.SET_NULL)
    horario_livre = models.ForeignKey('HorarioLivre', on_delete=models.CASCADE, related_name='turmas', null=True, blank=True)
    professor_responsavel = models.ForeignKey(Professor, related_name='turmas_ministradas', on_delete=models.CASCADE)

    def clean(self):
        if self.horario_livre and self.horario_livre.ocupado:
            raise ValidationError(f'O horário {self.horario_livre} já está ocupado.')
        if self.conta_sala_livre and self.conta_sala_livre.ocupado:
            raise ValidationError(f'A conta/sala {self.conta_sala_livre} já está ocupada.')
        conflitos_professor = Turma.objects.filter(
            professor_responsavel=self.professor_responsavel,
            horario_livre=self.horario_livre
        ).exclude(pk=self.pk)
        if conflitos_professor.exists():
            raise ValidationError(f'O professor {self.professor_responsavel.nome_professor} já está ocupado com outra turma nesse horário.')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._reservar_horario()

    def _reservar_horario(self):
        if self.horario_livre:
            self.horario_livre.ocupado = True
            self.horario_livre.ocupacao_tipo = 'Turma'
            self.horario_livre.ocupacao_nome = self.nome_turma
            self.horario_livre.save()
        if self.conta_sala_livre:
            self.conta_sala_livre.ocupado = True
            self.conta_sala_livre.ocupacao_tipo = 'Turma'
            self.conta_sala_livre.ocupacao_nome = self.nome_turma
            self.conta_sala_livre.save()

    def __str__(self):
        return self.nome_turma         

@receiver(m2m_changed, sender=Turma.alunos.through)
def alunos_turma_changed(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        pass
    if action in ["post_add", "post_remove"]:
        pass

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default= ' ')
    nome_aluno = models.CharField(max_length=100)
    
    def __str__(self):
        turmas_nomes = ', '.join(turma.nome_turma for turma in self.turmas_rel.all())
        username = self.user.username if self.user else "Sem usuário"
        return f"{self.nome_aluno} ({username}) - Turmas: {turmas_nomes if turmas_nomes else 'Nenhuma'}"

class Recado(models.Model):
    conteudo = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE, related_name='recados') 

    def __str__(self):
        return self.conteudo
    
class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set', 
        blank=True,
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  
        blank=True,
        help_text='Specific permissions for this user.'
    )

class Anuncio(models.Model):
    titulo = models.CharField(max_length=255)
    imagem = models.ImageField(upload_to='anuncios/', blank=True, null=True)  

    def __str__(self):
        return self.titulo
    
class Imagem(models.Model):
    imagem = models.ImageField(upload_to='anuncios/')

class Manuais_Profs(models.Model):
    titulo = models.CharField(max_length=255)  
    arquivo = models.FileField(upload_to='pdfs/') 
    data_upload = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.titulo
    
class Eventos(models.Model):
    titulo = models.CharField(max_length=255)  
    local = models.CharField(max_length=255)  
    data = models.DateTimeField(default=timezone.now)
    conta_sala_livre = models.ForeignKey('ContaSalaLivre', null=True, blank=True, on_delete=models.SET_NULL)

    def clean(self):
        if self.conta_sala_livre and self.conta_sala_livre.ocupado:
            raise ValidationError(f'A conta/sala {self.conta_sala_livre} já está ocupada.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self._reservar_horario()

    def _reservar_horario(self):
        if self.conta_sala_livre:
            self.conta_sala_livre.ocupado = True
            self.conta_sala_livre.ocupacao_tipo = 'Evento'
            self.conta_sala_livre.ocupacao_nome = self.titulo
            self.conta_sala_livre.save()

    def __str__(self):
        return self.titulo
