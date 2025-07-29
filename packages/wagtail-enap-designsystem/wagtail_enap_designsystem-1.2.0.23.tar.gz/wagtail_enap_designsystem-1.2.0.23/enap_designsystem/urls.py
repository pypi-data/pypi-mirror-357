from django.urls import path
from . import views

urlpatterns = [
	# ...
	path("teste-login-sso/", views.teste_login_sso, name="teste_login_sso"),
	path("login-sso/", views.login_sso, name="login_sso"),
	path("pt/elasticsearch/callback/", views.callback_sso, name="callback_sso"),
	path("logout/", views.logout_view, name="logout"),
    path('salvar-contato/', views.salvar_contato, name='salvar_contato'),
    path('salvar-resposta-formulario/', views.salvar_resposta_formulario, name='salvar_resposta_formulario'),
    path('exportar-respostas/', views.exportar_respostas_csv, name='exportar_respostas_csv'),
]
