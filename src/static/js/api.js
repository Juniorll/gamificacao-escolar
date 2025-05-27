/**
 * Módulo de API para comunicação com o backend
 * Este arquivo contém funções para realizar requisições HTTP para o backend
 */

// Configuração base para requisições
const API = {
    // Função para realizar requisições HTTP
    request: async function(endpoint, method = 'GET', data = null, token = null) {
        const headers = {
            'Content-Type': 'application/json'
        };

        // Adiciona token de autenticação se disponível
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers,
            credentials: 'include' // Inclui cookies nas requisições
        };

        // Adiciona corpo da requisição para métodos POST, PUT, etc.
        if (data && (method === 'POST' || method === 'PUT')) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(`/api/${endpoint}`, config);
            
            // Verifica se a resposta é JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const responseData = await response.json();
                
                // Retorna objeto com dados e status
                return {
                    ok: response.ok,
                    status: response.status,
                    data: responseData
                };
            } else {
                // Retorna resposta não-JSON
                return {
                    ok: response.ok,
                    status: response.status,
                    data: await response.text()
                };
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            return {
                ok: false,
                status: 0,
                data: { mensagem: 'Erro de conexão com o servidor' }
            };
        }
    },

    // Funções específicas para autenticação
    auth: {
        login: async function(email, senha) {
            return await API.request('auth/login', 'POST', { email, senha });
        },
        
        cadastro: async function(nome, email, senha) {
            return await API.request('auth/cadastro', 'POST', { nome, email, senha });
        },
        
        logout: async function() {
            return await API.request('auth/logout', 'POST');
        },
        
        perfil: async function() {
            return await API.request('auth/perfil');
        },
        
        atualizarPerfil: async function(dados) {
            return await API.request('auth/perfil', 'PUT', dados);
        }
    },

    // Funções para gerenciamento de colégios
    colegios: {
        listar: async function() {
            return await API.request('professor/colegios');
        },
        
        criar: async function(dados) {
            return await API.request('professor/colegios', 'POST', dados);
        }
    },

    // Funções para gerenciamento de turmas
    turmas: {
        listar: async function() {
            return await API.request('professor/turmas');
        },
        
        criar: async function(dados) {
            return await API.request('professor/turmas', 'POST', dados);
        },
        
        listarAlunos: async function(turmaId) {
            return await API.request(`professor/turmas/${turmaId}/alunos`);
        }
    },

    // Funções para gerenciamento de disciplinas
    disciplinas: {
        listar: async function() {
            return await API.request('professor/disciplinas');
        },
        
        criar: async function(dados) {
            return await API.request('professor/disciplinas', 'POST', dados);
        }
    },

    // Funções para gerenciamento de períodos
    periodos: {
        listar: async function() {
            return await API.request('professor/periodos');
        },
        
        criar: async function(dados) {
            return await API.request('professor/periodos', 'POST', dados);
        }
    },

    // Funções para gerenciamento de alunos
    alunos: {
        criar: async function(formData) {
            // Usa FormData para permitir upload de arquivos
            const headers = {};
            const response = await fetch('/api/professor/alunos', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            return {
                ok: response.ok,
                status: response.status,
                data: await response.json()
            };
        },
        
        importar: async function(formData) {
            const response = await fetch('/api/admin/importar/alunos', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            return {
                ok: response.ok,
                status: response.status,
                data: await response.json()
            };
        }
    },

    // Funções para gerenciamento de atividades
    atividades: {
        listar: async function() {
            return await API.request('professor/atividades');
        },
        
        criar: async function(dados) {
            return await API.request('professor/atividades', 'POST', dados);
        }
    },

    // Funções para gerenciamento de notas
    notas: {
        lancar: async function(dados) {
            return await API.request('professor/notas', 'POST', dados);
        }
    },

    // Funções para gerenciamento de trabalhos exemplares
    trabalhosExemplares: {
        listar: async function() {
            return await API.request('aluno/trabalhos_exemplares');
        },
        
        marcar: async function(dados) {
            return await API.request('professor/trabalhos_exemplares', 'POST', dados);
        }
    },

    // Funções para visualização de alunos (sem autenticação)
    aluno: {
        rankingGeral: async function() {
            return await API.request('aluno/ranking/geral');
        },
        
        rankingPorColegio: async function(colegioId) {
            return await API.request(`aluno/ranking/colegio/${colegioId}`);
        },
        
        rankingPorTurma: async function(turmaId) {
            return await API.request(`aluno/ranking/turma/${turmaId}`);
        },
        
        rankingPorDisciplina: async function(disciplinaId) {
            return await API.request(`aluno/ranking/disciplina/${disciplinaId}`);
        },
        
        rankingPorPeriodo: async function(periodoId) {
            return await API.request(`aluno/ranking/periodo/${periodoId}`);
        },
        
        linhaTempo: async function(alunoId) {
            return await API.request(`aluno/aluno/${alunoId}/linha_tempo`);
        },
        
        chanceAprovacao: async function(alunoId) {
            return await API.request(`aluno/aluno/${alunoId}/chance_aprovacao`);
        },
        
        filtros: async function() {
            return await API.request('aluno/filtros');
        }
    },

    // Funções para configurações e personalização
    admin: {
        listarConfiguracoes: async function() {
            return await API.request('admin/configuracoes');
        },
        
        obterConfiguracao: async function(chave) {
            return await API.request(`admin/configuracoes/${chave}`);
        },
        
        salvarConfiguracao: async function(dados) {
            return await API.request('admin/configuracoes', 'POST', dados);
        },
        
        uploadImagem: async function(formData) {
            const response = await fetch('/api/admin/upload/imagem', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });
            
            return {
                ok: response.ok,
                status: response.status,
                data: await response.json()
            };
        },
        
        listarImagens: async function(tipo) {
            return await API.request(`admin/imagens/${tipo}`);
        }
    }
};
