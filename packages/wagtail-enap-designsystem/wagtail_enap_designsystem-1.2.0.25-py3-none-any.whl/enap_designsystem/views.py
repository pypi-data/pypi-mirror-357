import uuid
import requests
import time
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseBadRequest
from .utils.decorators import aluno_login_required
from .utils.sso import get_valid_access_token
from wagtail.models import Page
from django.shortcuts import redirect
from django.contrib import messages
from .models import Contato
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse 
from django.core.mail import send_mail
from .models import Contato, FormularioSnippet, RespostaFormulario
from django.shortcuts import redirect, get_object_or_404, render
import csv
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone





def teste_login_sso(request):
	return render(request, "teste_login_sso.html")

def login_sso(request):
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	# Gera state único para segurança (proteção CSRF)
	state = str(uuid.uuid4())

	# print("Redirect URI gerado:", redirect_uri)
	# Monta query com todos os parâmetros
	query = {
		"client_id": settings.SSO_CLIENT_ID,
		"redirect_uri": redirect_uri,
		"response_type": "code",
		"scope": "openid",
		"state": state,
	}

	# Monta URL final do SSO
	sso_login_url = f"{settings.SSO_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in query.items())}"
	return redirect(sso_login_url)

def callback_sso(request):
	code = request.GET.get("code")
	if not code:
		return HttpResponseBadRequest("Código de autorização ausente.")

	# 🛑 IMPORTANTE: esta URL precisa ser exatamente igual à registrada no Keycloak
	redirect_uri = request.build_absolute_uri(settings.SSO_REDIRECT_PATH)

	data = {
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": redirect_uri,
		"client_id": settings.SSO_CLIENT_ID,
		"client_secret": settings.SSO_CLIENT_SECRET,
	}
	headers = {
		"Content-Type": "application/x-www-form-urlencoded"
	}

	# ⚠️ Desativa verificação SSL apenas em DEV
	verify_ssl = not settings.DEBUG

	# 🔐 Solicita o token
	print("📥 Enviando para /token:", data)
	token_response = requests.post(
		settings.SSO_TOKEN_URL,
		data=data,
		headers=headers,
		verify=verify_ssl
	)
	print("🧾 TOKEN RESPONSE:", token_response.status_code, token_response.text)

	if token_response.status_code != 200:
		return HttpResponse("Erro ao obter token", status=token_response.status_code)

	access_token = token_response.json().get("access_token")
	if not access_token:
		return HttpResponse("Token de acesso não recebido.", status=400)

	# 🔍 Pega dados do usuário
	userinfo_headers = {
		"Authorization": f"Bearer {access_token}"
	}
	user_info_response = requests.get(
		settings.SSO_USERINFO_URL,
		headers=userinfo_headers,
		verify=verify_ssl
	)

	if user_info_response.status_code != 200:
		return HttpResponse("Erro ao obter informações do usuário.", status=400)

	user_info = user_info_response.json()
	email = user_info.get("email")
	nome = user_info.get("name")
	cpf = user_info.get("cpf")
	print("user_info", user_info)
	if not email or not nome:
		return HttpResponse("Informações essenciais ausentes no SSO.", status=400)

	# 🧠 Armazena na sessão para uso em /area-do-aluno
	request.session["aluno_sso"] = {
		"email": email,
		"nome": nome,
		"cpf": cpf,
		"access_token": access_token,
		"refresh_token": token_response.json().get("refresh_token"),
		"access_token_expires_at": int(time.time()) + token_response.json().get("expires_in", 300),
	}

	return redirect(get_area_do_aluno_url())

def logout_view(request):
	request.session.flush()
	return render(request, "logout_intermediario.html")

def get_area_do_aluno_url():
	try:
		page = Page.objects.get(slug="area-do-aluno").specific
		return page.url
	except Page.DoesNotExist:
		return "/"
	
@aluno_login_required
def area_do_aluno(request):
	token = get_valid_access_token(request.session)
	if not token:
		return redirect("/")

	# Exemplo: usar o token para chamar API externa
	response = requests.get("https://api.enap.gov.br/aluno", headers={
		"Authorization": f"Bearer {token}"
	})
	aluno_dados = response.json()

	return render(request, "area_do_aluno.html", {
		"aluno": request.session["aluno_sso"],
		"dados": aluno_dados,
	})






def salvar_contato(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        mensagem = request.POST.get('mensagem')
        
        # Salva no banco
        Contato.objects.create(
            nome=nome,
            email=email,
            mensagem=mensagem
        )
        
        messages.success(request, 'Mensagem enviada com sucesso!')
        return redirect(request.META.get('HTTP_REFERER', '/'))
	



def salvar_resposta_formulario(request):
    """Salva resposta do formulário snippet"""
    if request.method == 'POST':
        try:
            formulario_id = request.POST.get('formulario_id')
            nome = request.POST.get('nome', '').strip()
            email = request.POST.get('email', '').strip()
            telefone = request.POST.get('telefone', '').strip()
            assunto = request.POST.get('assunto', '').strip()
            mensagem = request.POST.get('mensagem', '').strip()
            
            # Validação básica
            if not formulario_id or not nome or not email or not assunto or not mensagem:
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor, preencha todos os campos obrigatórios.'
                })
            
            # Busca o formulário
            formulario = get_object_or_404(FormularioSnippet, id=formulario_id, ativo=True)
            
            # Função para pegar IP
            def get_client_ip(request):
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                return ip
            
            # Salva no banco
            resposta = RespostaFormulario.objects.create(
                formulario=formulario,
                nome=nome,
                email=email,
                telefone=telefone,
                assunto=assunto,
                mensagem=mensagem,
                ip_address=get_client_ip(request)
            )
            
            # Envia email (opcional - pode comentar se não quiser)
            try:
                send_mail(
                    subject=f"[{formulario.nome}] {assunto}",
                    message=f"""
Nova mensagem recebida através do formulário "{formulario.nome}":

Nome: {nome}
Email: {email}
Telefone: {telefone}
Assunto: {assunto}

Mensagem:
{mensagem}

---
Enviado em: {resposta.data.strftime('%d/%m/%Y às %H:%M')}
IP: {resposta.ip_address}
                    """,
                    from_email='noreply@enap.gov.br',  # Ajuste conforme necessário
                    recipient_list=[formulario.email_destino],
                    fail_silently=True,
                )
            except Exception as email_error:
                print(f"Erro ao enviar email: {email_error}")
                # Não quebra o formulário se der erro no email
                pass
            
            return JsonResponse({
                'success': True,
                'message': 'Mensagem enviada com sucesso! Entraremos em contato em breve.'
            })
            
        except FormularioSnippet.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Formulário não encontrado ou inativo.'
            })
        except Exception as e:
            print(f"Erro ao salvar formulário: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Erro interno. Tente novamente.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido.'
    })







@staff_member_required
def exportar_respostas_csv(request):
    """View para exportar respostas em CSV"""
    
    # Pega filtro de formulário se houver
    formulario_id = request.GET.get('formulario')
    
    if formulario_id:
        respostas = RespostaFormulario.objects.filter(formulario_id=formulario_id)
        filename = f"respostas_formulario_{formulario_id}_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    else:
        respostas = RespostaFormulario.objects.all()
        filename = f"todas_respostas_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # Cria resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # BOM para UTF-8
    response.write('\ufeff')
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'Formulário',
        'Nome', 
        'Email',
        'Telefone',
        'Assunto',
        'Mensagem',
        'Data/Hora',
        'IP'
    ])
    
    # Dados
    for resposta in respostas:
        writer.writerow([
            resposta.formulario.nome,
            resposta.nome,
            resposta.email,
            resposta.telefone,
            resposta.assunto,
            resposta.mensagem,
            resposta.data.strftime('%d/%m/%Y %H:%M'),
            resposta.ip_address or ''
        ])
    
    return response





@staff_member_required
def exportar_respostas_csv(request):
    """View para exportar respostas em CSV com filtro de formulário"""
    
    # Se é GET, mostra página de escolha
    if request.method == 'GET' and not request.GET.get('formulario'):
        formularios = FormularioSnippet.objects.filter(ativo=True)
        context = {
            'formularios': formularios,
            'total_respostas': RespostaFormulario.objects.count()
        }
        return render(request, 'admin/exportar_respostas.html', context)
    
    # Se tem filtro ou é POST, exporta
    formulario_id = request.GET.get('formulario') or request.POST.get('formulario')
    
    if formulario_id:
        formulario = FormularioSnippet.objects.get(id=formulario_id)
        respostas = RespostaFormulario.objects.filter(formulario_id=formulario_id)
        filename = f"respostas_{formulario.nome.replace(' ', '_')}_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    else:
        respostas = RespostaFormulario.objects.all()
        filename = f"todas_respostas_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
    
    # Cria resposta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # BOM para UTF-8
    response.write('\ufeff')
    writer = csv.writer(response)
    
    # Cabeçalho
    writer.writerow([
        'Formulário',
        'Nome', 
        'Email',
        'Telefone',
        'Assunto',
        'Mensagem',
        'Data/Hora',
        'IP'
    ])
    
    # Dados
    for resposta in respostas.order_by('-data'):
        writer.writerow([
            resposta.formulario.nome,
            resposta.nome,
            resposta.email,
            resposta.telefone,
            resposta.assunto,
            resposta.mensagem,
            resposta.data.strftime('%d/%m/%Y %H:%M'),
            resposta.ip_address or ''
        ])
    
    return response