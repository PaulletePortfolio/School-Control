from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Turma, Aluno, Professor, HorarioLivre, Recado, Anuncio, Manuais_Profs,Eventos
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import RecadoForm

@login_required
def aluno_detail(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    turmas = Turma.objects.filter(alunos=aluno)

    return render(request, 'pagina_aluno.html', {
        'aluno': aluno,
        'turmas': turmas,
    })
    
@login_required
def perfil_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, id=aluno_id)
    turmas = Turma.objects.filter(alunos=aluno)

    return render(request, 'perfil_aluno.html', {
        'aluno': aluno,
        'turmas': turmas,
    })

@login_required
def pagina_inicial_aluno(request):
    aluno = get_object_or_404(Aluno, user=request.user)
    turmas = Turma.objects.filter(alunos=aluno)
    
    recados = []
    for turma in turmas:
        recados.extend(turma.recados.all()) 

    anuncios = Anuncio.objects.all()


    return render(request, 'pagina_inicial_aluno.html', {
        'aluno': aluno,
        'turmas': turmas,
        'recados': recados,
        'anuncios': anuncios,

    })

@login_required
def turma_detail(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    alunos = turma.alunos.all()  
    
    recados = turma.recados.all()  

    return render(request, 'turma_alunoview.html', {
        'turma': turma,
        'alunos': alunos,  
        'recados': recados,  
    })
    
@login_required
def turma_detail_prof(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    alunos = turma.alunos.all() 
    recados = turma.recados.all()  
    card_link = turma.card_link

    if request.method == 'POST':
        form = RecadoForm(request.POST)
        if form.is_valid():
            recado = form.save(commit=False)
            recado.turma = turma  
            recado.save()
            return redirect('turma_detail_prof', turma_id=turma_id) 
    else:
        form = RecadoForm()

    return render(request, 'turma_teacherview.html', {
        'turma': turma,
        'alunos': alunos,  
        'recados': recados,
        'form': form,  
        'card_link': card_link,
    })

@login_required
def listar_turmas(request):
    try:
        turmas = Turma.objects.all()
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao listar as turmas: {str(e)}')
        turmas = []

    return render(request, 'turmas.html', {'turmas': turmas})

@login_required
def detalhes_professor(request, professor_id):
    professor = get_object_or_404(Professor, pk=professor_id)
    turmas_professor = Turma.objects.filter(professor_responsavel=professor)
    manuais = Manuais_Profs.objects.all()

    return render(request, 'detalhes_professor.html', {
        'professor': professor,
        'turmas_professor': turmas_professor,
        'manuais': manuais,
    })
    
@login_required
def professor_view(request):
    professor = get_object_or_404(Professor, user=request.user)
    turmas = Turma.objects.filter(professor_responsavel=professor)
    manuais = Manuais_Profs.objects.all()

    return render(request, 'pagina_inicial_prof.html', {
        'turmas': turmas,
        'manuais': manuais,})

@login_required
def listar_horarios_livres(request):
    dia = request.GET.get('dia')
    if dia and dia in [day[0] for day in HorarioLivre.DIAS_SEMANA_CHOICES]:
        horarios_livres = HorarioLivre.objects.filter(dia_semana=dia)
    else:
        horarios_livres = HorarioLivre.objects.all()
    
    return render(request, 'listar_horarios_livres.html', {'horarios_livres': horarios_livres})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Redireciona com base no tipo de usuário
            if Aluno.objects.filter(user=user).exists():
                return redirect('pagina_inicial_aluno')
            elif Professor.objects.filter(user=user).exists():
                return redirect('pagina_inicial_prof')

            messages.error(request, "Usuário não autorizado.")
        else:
            messages.error(request, 'Login ou senha inválidos.')
    
    return render(request, 'login.html')

@login_required
def pagina_inicial_prof(request):
    professor = get_object_or_404(Professor, user=request.user)
    turmas = Turma.objects.filter(professor_responsavel=professor)
    manuais = Manuais_Profs.objects.all()
    eventos = Eventos.objects.all()

    return render(request, 'pagina_inicial_prof.html', {'turmas': turmas, 'manuais': manuais,'eventos': eventos,})

@login_required
def adicionar_recado(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    
    if request.method == 'POST':
        form = RecadoForm(request.POST)
        if form.is_valid():
            recado = form.save(commit=False)
            recado.turma = turma  # Atribui a turma ao recado
            recado.save()
            messages.success(request, 'Recado adicionado com sucesso!')
            # Renderiza novamente a página com o formulário e os recados
            return render(request, 'turma_teacherview.html', {
                'form': RecadoForm(),  # Reseta o formulário
                'turma': turma,
                'recados': turma.recado_set.all()  # Pega todos os recados da turma
            })
    else:
        form = RecadoForm()

    return render(request, 'turma_teacherview.html', {
        'form': form,
        'turma': turma,
        'recados': turma.recado_set.all()  # Pega todos os recados da turma
    })
    
def lista_anuncios(request):
    anuncios = Anuncio.objects.all()  
    return render(request, 'pagina_inicial_aluno.html', {'anuncios': anuncios})

@login_required
def visualizar_recados(request, turma_id):
    turma = get_object_or_404(Turma, id=turma_id)
    recados = turma.recado_set.all()  # Obtem todos os recados da turma

    return render(request, 'visualizar_recados.html', {
        'turma': turma,
        'recados': recados,
    })
    