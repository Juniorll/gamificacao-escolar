/**
 * Módulo principal da aplicação
 * Este arquivo contém a lógica principal para inicialização e roteamento da aplicação
 */

// Inicialização da aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa a aplicação
    App.init();
});

// Objeto principal da aplicação
const App = {
    // Estado atual da aplicação
    state: {
        currentView: null,
        isAuthenticated: false,
        isLoading: true,
        userData: null,
        filtros: null
    },
    
    // Inicialização da aplicação
    init: async function() {
        console.log('Inicializando aplicação...');
        
        // Verifica se há uma sessão ativa
        if (Auth.isAuthenticated()) {
            const sessionValid = await Auth.checkSession();
            this.state.isAuthenticated = sessionValid;
            
            if (sessionValid) {
                this.state.userData = Auth.getUser();
                this.renderProfessorDashboard();
            } else {
                this.renderLoginView();
            }
        } else {
            // Verifica se há um parâmetro na URL para visualização de aluno
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('aluno')) {
                this.renderAlunoView();
            } else {
                this.renderLoginView();
            }
        }
        
        // Remove o indicador de carregamento
        this.state.isLoading = false;
        document.querySelector('.loading-container').style.display = 'none';
    },
    
    // Renderiza a tela de login
    renderLoginView: function() {
        console.log('Renderizando tela de login');
        this.state.currentView = 'login';
        
        // Obtém o template de login
        const template = document.getElementById('login-template');
        const appContainer = document.getElementById('app');
        
        // Limpa o conteúdo atual
        appContainer.innerHTML = '';
        
        // Clona o template e adiciona ao container
        const loginView = template.content.cloneNode(true);
        appContainer.appendChild(loginView);
        
        // Adiciona eventos aos botões
        document.getElementById('btn-login').addEventListener('click', this.handleLogin.bind(this));
        document.getElementById('link-cadastro').addEventListener('click', this.renderCadastroView.bind(this));
        document.getElementById('link-aluno-view').addEventListener('click', this.renderAlunoView.bind(this));
    },
    
    // Renderiza a tela de cadastro
    renderCadastroView: function(e) {
        if (e) e.preventDefault();
        
        console.log('Renderizando tela de cadastro');
        this.state.currentView = 'cadastro';
        
        // Obtém o template de cadastro
        const template = document.getElementById('cadastro-template');
        const appContainer = document.getElementById('app');
        
        // Limpa o conteúdo atual
        appContainer.innerHTML = '';
        
        // Clona o template e adiciona ao container
        const cadastroView = template.content.cloneNode(true);
        appContainer.appendChild(cadastroView);
        
        // Adiciona eventos aos botões
        document.getElementById('btn-cadastrar').addEventListener('click', this.handleCadastro.bind(this));
        document.getElementById('link-voltar-login').addEventListener('click', this.renderLoginView.bind(this));
    },
    
    // Renderiza o dashboard do professor
    renderProfessorDashboard: function() {
        console.log('Renderizando dashboard do professor');
        this.state.currentView = 'professor-dashboard';
        
        // Obtém o template do dashboard
        const template = document.getElementById('professor-dashboard-template');
        const appContainer = document.getElementById('app');
        
        // Limpa o conteúdo atual
        appContainer.innerHTML = '';
        
        // Clona o template e adiciona ao container
        const dashboardView = template.content.cloneNode(true);
        appContainer.appendChild(dashboardView);
        
        // Atualiza o nome do professor
        if (this.state.userData) {
            document.getElementById('professor-nome').textContent = this.state.userData.nome;
        }
        
        // Adiciona eventos aos links do menu
        const navLinks = document.querySelectorAll('.nav-link[data-page]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.loadProfessorPage(page);
                
                // Atualiza a classe active
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
        
        // Adiciona evento ao botão de logout
        document.getElementById('btn-logout').addEventListener('click', this.handleLogout.bind(this));
        
        // Carrega a página inicial do dashboard
        this.loadProfessorPage('dashboard');
    },
    
    // Renderiza a visualização do aluno
    renderAlunoView: async function(e) {
        if (e) e.preventDefault();
        
        console.log('Renderizando visualização do aluno');
        this.state.currentView = 'aluno-view';
        
        // Obtém o template da visualização do aluno
        const template = document.getElementById('aluno-view-template');
        const appContainer = document.getElementById('app');
        
        // Limpa o conteúdo atual
        appContainer.innerHTML = '';
        
        // Clona o template e adiciona ao container
        const alunoView = template.content.cloneNode(true);
        appContainer.appendChild(alunoView);
        
        // Adiciona eventos aos links do menu
        const navLinks = document.querySelectorAll('.nav-link[data-page]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.loadAlunoPage(page);
                
                // Atualiza a classe active
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            });
        });
        
        // Adiciona evento ao link para área do professor
        document.getElementById('link-professor-login').addEventListener('click', this.renderLoginView.bind(this));
        
        // Carrega os filtros disponíveis
        await this.loadFiltros();
        
        // Carrega a página inicial (ranking geral)
        this.loadAlunoPage('ranking-geral');
    },
    
    // Carrega os filtros disponíveis para a visualização do aluno
    loadFiltros: async function() {
        try {
            const response = await API.aluno.filtros();
            
            if (response.ok) {
                this.state.filtros = response.data;
                
                // Preenche os dropdowns de filtros
                this.populateFiltrosDropdowns();
            } else {
                console.error('Erro ao carregar filtros:', response.data);
            }
        } catch (error) {
            console.error('Erro ao carregar filtros:', error);
        }
    },
    
    // Preenche os dropdowns de filtros
    populateFiltrosDropdowns: function() {
        if (!this.state.filtros) return;
        
        // Preenche dropdown de colégios
        const colegiosDropdown = document.getElementById('colegios-dropdown');
        colegiosDropdown.innerHTML = '';
        
        this.state.filtros.colegios.forEach(colegio => {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.className = 'dropdown-item';
            link.href = '#';
            link.textContent = colegio.nome;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadAlunoPage('ranking-colegio', colegio.id);
            });
            
            item.appendChild(link);
            colegiosDropdown.appendChild(item);
        });
        
        // Preenche dropdown de turmas
        const turmasDropdown = document.getElementById('turmas-dropdown');
        turmasDropdown.innerHTML = '';
        
        this.state.filtros.turmas.forEach(turma => {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.className = 'dropdown-item';
            link.href = '#';
            link.textContent = turma.nome;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadAlunoPage('ranking-turma', turma.id);
            });
            
            item.appendChild(link);
            turmasDropdown.appendChild(item);
        });
        
        // Preenche dropdown de disciplinas
        const disciplinasDropdown = document.getElementById('disciplinas-dropdown');
        disciplinasDropdown.innerHTML = '';
        
        this.state.filtros.disciplinas.forEach(disciplina => {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.className = 'dropdown-item';
            link.href = '#';
            link.textContent = disciplina.nome;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadAlunoPage('ranking-disciplina', disciplina.id);
            });
            
            item.appendChild(link);
            disciplinasDropdown.appendChild(item);
        });
        
        // Preenche dropdown de períodos
        const periodosDropdown = document.getElementById('periodos-dropdown');
        periodosDropdown.innerHTML = '';
        
        this.state.filtros.periodos.forEach(periodo => {
            const item = document.createElement('li');
            const link = document.createElement('a');
            link.className = 'dropdown-item';
            link.href = '#';
            link.textContent = `${periodo.nome} (${periodo.tipo})`;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadAlunoPage('ranking-periodo', periodo.id);
            });
            
            item.appendChild(link);
            periodosDropdown.appendChild(item);
        });
    },
    
    // Carrega uma página específica do dashboard do professor
    loadProfessorPage: function(page) {
        console.log(`Carregando página do professor: ${page}`);
        
        const contentContainer = document.getElementById('dashboard-content');
        contentContainer.innerHTML = '<div class="loading-animation"><i class="fas fa-spinner fa-spin"></i><p>Carregando...</p></div>';
        
        // Carrega o conteúdo da página
        switch (page) {
            case 'dashboard':
                ProfessorDashboard.loadDashboard(contentContainer);
                break;
            case 'colegios':
                ProfessorDashboard.loadColegios(contentContainer);
                break;
            case 'turmas':
                ProfessorDashboard.loadTurmas(contentContainer);
                break;
            case 'disciplinas':
                ProfessorDashboard.loadDisciplinas(contentContainer);
                break;
            case 'periodos':
                ProfessorDashboard.loadPeriodos(contentContainer);
                break;
            case 'alunos':
                ProfessorDashboard.loadAlunos(contentContainer);
                break;
            case 'atividades':
                ProfessorDashboard.loadAtividades(contentContainer);
                break;
            case 'trabalhos':
                ProfessorDashboard.loadTrabalhosExemplares(contentContainer);
                break;
            case 'personalizacao':
                ProfessorDashboard.loadPersonalizacao(contentContainer);
                break;
            case 'perfil':
                ProfessorDashboard.loadPerfil(contentContainer);
                break;
            default:
                contentContainer.innerHTML = '<div class="alert alert-warning">Página não encontrada</div>';
        }
    },
    
    // Carrega uma página específica da visualização do aluno
    loadAlunoPage: function(page, id) {
        console.log(`Carregando página do aluno: ${page}${id ? ' com ID ' + id : ''}`);
        
        const contentContainer = document.getElementById('aluno-content');
        contentContainer.innerHTML = '<div class="loading-animation"><i class="fas fa-spinner fa-spin"></i><p>Carregando...</p></div>';
        
        // Carrega o conteúdo da página
        switch (page) {
            case 'ranking-geral':
                AlunoView.loadRankingGeral(contentContainer);
                break;
            case 'ranking-colegio':
                AlunoView.loadRankingPorColegio(contentContainer, id);
                break;
            case 'ranking-turma':
                AlunoView.loadRankingPorTurma(contentContainer, id);
                break;
            case 'ranking-disciplina':
                AlunoView.loadRankingPorDisciplina(contentContainer, id);
                break;
            case 'ranking-periodo':
                AlunoView.loadRankingPorPeriodo(contentContainer, id);
                break;
            case 'aluno-perfil':
                AlunoView.loadAlunoPerfil(contentContainer, id);
                break;
            case 'trabalhos-exemplares':
                AlunoView.loadTrabalhosExemplares(contentContainer);
                break;
            default:
                contentContainer.innerHTML = '<div class="alert alert-warning">Página não encontrada</div>';
        }
    },
    
    // Manipula o evento de login
    handleLogin: async function() {
        const email = document.getElementById('email').value;
        const senha = document.getElementById('senha').value;
        
        if (!email || !senha) {
            alert('Por favor, preencha todos os campos');
            return;
        }
        
        // Desabilita o botão durante o login
        const btnLogin = document.getElementById('btn-login');
        btnLogin.disabled = true;
        btnLogin.textContent = 'Entrando...';
        
        try {
            const result = await Auth.login(email, senha);
            
            if (result.success) {
                this.state.isAuthenticated = true;
                this.state.userData = Auth.getUser();
                this.renderProfessorDashboard();
            } else {
                alert(result.message);
                btnLogin.disabled = false;
                btnLogin.textContent = 'Entrar';
            }
        } catch (error) {
            console.error('Erro ao fazer login:', error);
            alert('Erro ao fazer login. Tente novamente mais tarde.');
            btnLogin.disabled = false;
            btnLogin.textContent = 'Entrar';
        }
    },
    
    // Manipula o evento de cadastro
    handleCadastro: async function() {
        const nome = document.getElementById('nome').value;
        const email = document.getElementById('email-cadastro').value;
        const senha = document.getElementById('senha-cadastro').value;
        const confirmarSenha = document.getElementById('confirmar-senha').value;
        
        if (!nome || !email || !senha || !confirmarSenha) {
            alert('Por favor, preencha todos os campos');
            return;
        }
        
        if (senha !== confirmarSenha) {
            alert('As senhas não coincidem');
            return;
        }
        
        // Desabilita o botão durante o cadastro
        const btnCadastrar = document.getElementById('btn-cadastrar');
        btnCadastrar.disabled = true;
        btnCadastrar.textContent = 'Cadastrando...';
        
        try {
            const result = await Auth.register(nome, email, senha);
            
            if (result.success) {
                alert('Cadastro realizado com sucesso! Faça login para continuar.');
                this.renderLoginView();
            } else {
                alert(result.message);
                btnCadastrar.disabled = false;
                btnCadastrar.textContent = 'Cadastrar';
            }
        } catch (error) {
            console.error('Erro ao cadastrar:', error);
            alert('Erro ao cadastrar. Tente novamente mais tarde.');
            btnCadastrar.disabled = false;
            btnCadastrar.textContent = 'Cadastrar';
        }
    },
    
    // Manipula o evento de logout
    handleLogout: async function(e) {
        e.preventDefault();
        
        try {
            await Auth.logout();
            this.state.isAuthenticated = false;
            this.state.userData = null;
            this.renderLoginView();
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
            alert('Erro ao fazer logout. Tente novamente mais tarde.');
        }
    }
};
