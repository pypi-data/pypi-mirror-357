"""
Serviço do Chatbot IA - Design System ENAP
"""

import google.generativeai as genai
import json
import re
from django.conf import settings
from django.urls import reverse
from wagtail.models import Page
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..models import ChatbotConfig, ChatbotWidget, PaginaIndexada, ConversaChatbot


class ChatbotService:
    def __init__(self):
        self.config = ChatbotConfig.objects.first()
        if self.config and self.config.api_key_google:
            genai.configure(api_key=self.config.api_key_google)
            self.model = genai.GenerativeModel(self.config.modelo_ia)

    def indexar_todas_paginas(self):
        """Indexa todas as páginas públicas do site"""
        print("🚀 Iniciando indexação das páginas...")
        
        paginas = Page.objects.live().public()
        total_paginas = paginas.count()
        processadas = 0
        
        for pagina in paginas:
            try:
                # Extrai conteúdo da página
                conteudo = self._extrair_conteudo_pagina(pagina)
                
                if not conteudo.strip():
                    print(f"⚠️  Pulando (sem conteúdo): {pagina.title}")
                    continue
                
                # Atualiza ou cria registro
                pagina_indexada, created = PaginaIndexada.objects.update_or_create(
                    pagina=pagina,
                    defaults={
                        'titulo': pagina.title,
                        'conteudo_texto': conteudo,
                        'url': pagina.full_url or pagina.url,
                        'tags': json.dumps(self._extrair_tags(pagina)),
                        'ativa': True
                    }
                )
                
                processadas += 1
                status = "✅ Criada" if created else "🔄 Atualizada"
                print(f"{status}: {pagina.title} ({processadas}/{total_paginas})")
                
            except Exception as e:
                print(f"❌ Erro ao indexar {pagina.title}: {e}")
        
        print(f"🎉 Indexação concluída! {processadas} páginas processadas.")

    def _extrair_conteudo_pagina(self, pagina):
        """Extrai texto da página"""
        conteudo = []
        
        # Título
        conteudo.append(pagina.title)
        
        # SEO Title e Description
        if hasattr(pagina, 'seo_title') and pagina.seo_title:
            conteudo.append(pagina.seo_title)
        if hasattr(pagina, 'search_description') and pagina.search_description:
            conteudo.append(pagina.search_description)
        
        # StreamField content (body)
        if hasattr(pagina, 'body'):
            for block in pagina.body:
                texto_block = self._extrair_texto_block(block)
                if texto_block:
                    conteudo.append(texto_block)
        
        # Outros campos de texto comuns
        campos_texto = [
            'intro', 'description', 'content', 'resumo', 'objetivo',
            'metodologia', 'publico_alvo', 'pre_requisitos', 'observacoes'
        ]
        
        for campo in campos_texto:
            if hasattr(pagina, campo):
                try:
                    valor = getattr(pagina, campo)
                    if isinstance(valor, str) and valor.strip():
                        # Remove HTML se houver
                        texto_limpo = BeautifulSoup(valor, 'html.parser').get_text()
                        if texto_limpo.strip():
                            conteudo.append(texto_limpo.strip())
                except:
                    continue
        
        return ' '.join(conteudo)

    def _extrair_texto_block(self, block):
        """Extrai texto de um StreamField block"""
        texto_extraido = []
        
        if hasattr(block, 'value'):
            if isinstance(block.value, str):
                # Remove HTML
                texto_limpo = BeautifulSoup(block.value, 'html.parser').get_text()
                texto_extraido.append(texto_limpo.strip())
            
            elif isinstance(block.value, dict):
                # Navega pelo dicionário procurando texto
                for key, value in block.value.items():
                    if isinstance(value, str) and value.strip():
                        texto_limpo = BeautifulSoup(value, 'html.parser').get_text()
                        if texto_limpo.strip():
                            texto_extraido.append(texto_limpo.strip())
        
        return ' '.join(texto_extraido)

    def _extrair_tags(self, pagina):
        """Extrai tags/palavras-chave da página"""
        tags = []
        
        # Tags do Wagtail se existirem
        if hasattr(pagina, 'tags') and hasattr(pagina.tags, 'all') and pagina.tags.exists():
            tags.extend([str(tag.name) for tag in pagina.tags.all()])
        
        # Categoria se existir
        if hasattr(pagina, 'categoria') and pagina.categoria:
            tags.append(str(pagina.categoria))
        
        # Tipo da página (convertido para string)
        if hasattr(pagina._meta, 'verbose_name'):
            tags.append(str(pagina._meta.verbose_name))
        
        tags.append(str(pagina.__class__.__name__))
        
        # Garante que todas as tags são strings
        tags = [str(tag) for tag in tags if tag]
        
        return tags

    def buscar_paginas_relevantes(self, pergunta, limite=5):
        """Busca páginas mais relevantes para a pergunta"""
        paginas = PaginaIndexada.objects.filter(ativa=True)
        
        if not paginas.exists():
            return []
        
        # Prepara textos para análise
        documentos = []
        paginas_list = list(paginas)
        
        for pagina in paginas_list:
            texto_completo = f"{pagina.titulo} {pagina.conteudo_texto}"
            documentos.append(texto_completo)
        
        # Adiciona a pergunta
        documentos.append(pergunta)
        
        # Calcula similaridade usando TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                stop_words=None,  # Você pode adicionar stop words em português
                max_features=5000,
                ngram_range=(1, 2),
                lowercase=True
            )
            
            tfidf_matrix = vectorizer.fit_transform(documentos)
            
            # Calcula similaridade da pergunta com cada página
            pergunta_vector = tfidf_matrix[-1]  # Último é a pergunta
            paginas_vectors = tfidf_matrix[:-1]  # Todos menos o último
            
            similarities = cosine_similarity(pergunta_vector, paginas_vectors).flatten()
            
            # Ordena por similaridade
            indices_ordenados = similarities.argsort()[::-1][:limite]
            
            # Filtra apenas páginas com similaridade > 0.1
            paginas_relevantes = []
            for idx in indices_ordenados:
                if similarities[idx] > 0.1:
                    paginas_relevantes.append({
                        'pagina': paginas_list[idx],
                        'score': float(similarities[idx])
                    })
            
            return paginas_relevantes
            
        except Exception as e:
            print(f"Erro na busca semântica: {e}")
            # Fallback: busca simples por palavras-chave
            return self._busca_simples(pergunta, paginas_list, limite)

    def _busca_simples(self, pergunta, paginas_list, limite):
        """Busca simples por palavras-chave como fallback"""
        palavras = pergunta.lower().split()
        resultados = []
        
        for pagina in paginas_list:
            texto_busca = f"{pagina.titulo} {pagina.conteudo_texto}".lower()
            score = sum(1 for palavra in palavras if palavra in texto_busca)
            
            if score > 0:
                resultados.append({
                    'pagina': pagina,
                    'score': score / len(palavras)
                })
        
        # Ordena por score e retorna os melhores
        resultados.sort(key=lambda x: x['score'], reverse=True)
        return resultados[:limite]

    def gerar_resposta(self, pergunta, sessao_id=None, user_ip=None):
        """Gera resposta usando Google AI"""
        if not self.config or not self.config.api_key_google:
            return {
                'resposta': 'Chatbot não configurado. Configure a API key do Google AI Studio no admin.',
                'paginas': []
            }
        
        # Busca páginas relevantes
        paginas_relevantes = self.buscar_paginas_relevantes(pergunta)
        
        # Monta contexto
        contexto = self._montar_contexto(paginas_relevantes)
        
        # Monta prompt
        prompt = f"""
{self.config.prompt_sistema}

CONTEXTO DAS PÁGINAS DO SITE ENAP:
{contexto}

PERGUNTA DO USUÁRIO: {pergunta}

INSTRUÇÕES:
1. Responda de forma clara e objetiva em português
2. Use apenas informações do contexto fornecido
3. Se mencionar uma página, indique que há links relacionados disponíveis
4. Se não souber a resposta com base no contexto, seja honesto
5. Mantenha um tom profissional e amigável da ENAP
6. Limite a resposta a 200 palavras

RESPOSTA:
"""
        
        try:
            # Gera resposta com Gemini
            response = self.model.generate_content(prompt)
            resposta_texto = response.text
            
            # Salva conversa
            if sessao_id:
                ConversaChatbot.objects.create(
                    sessao_id=sessao_id,
                    usuario_ip=user_ip,
                    mensagem_usuario=pergunta,
                    resposta_bot=resposta_texto,
                    paginas_referenciadas=json.dumps([
                        {'titulo': p['pagina'].titulo, 'url': p['pagina'].url} 
                        for p in paginas_relevantes
                    ])
                )
            
            return {
                'resposta': resposta_texto,
                'paginas': [
                    {
                        'titulo': p['pagina'].titulo,
                        'url': p['pagina'].url,
                        'score': p['score']
                    }
                    for p in paginas_relevantes
                ]
            }
            
        except Exception as e:
            return {
                'resposta': f'Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente em alguns instantes.',
                'paginas': []
            }

    def _montar_contexto(self, paginas_relevantes):
        """Monta contexto das páginas para o prompt"""
        if not paginas_relevantes:
            return "Nenhuma página relevante encontrada no site da ENAP."
        
        contexto_parts = []
        for item in paginas_relevantes[:3]:  # Limita a 3 páginas para não estourar o contexto
            pagina = item['pagina']
            # Limita o texto para não estourar o limite do modelo
            conteudo_resumido = pagina.conteudo_texto[:800] + "..." if len(pagina.conteudo_texto) > 800 else pagina.conteudo_texto
            
            contexto_parts.append(f"""
PÁGINA: {pagina.titulo}
URL: {pagina.url}
CONTEÚDO: {conteudo_resumido}
---
""")
        
        return '\n'.join(contexto_parts)