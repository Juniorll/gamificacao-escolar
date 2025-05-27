/**
 * Módulo de autenticação
 * Este arquivo contém funções para gerenciar autenticação e sessão do usuário
 */

// Gerenciamento de autenticação
const Auth = {
    // Verifica se o usuário está autenticado
    isAuthenticated: function() {
        return localStorage.getItem('userToken') !== null;
    },
    
    // Salva dados do usuário após login
    setUser: function(userData, token) {
        localStorage.setItem('userToken', token || 'session');
        localStorage.setItem('userData', JSON.stringify(userData));
    },
    
    // Obtém dados do usuário atual
    getUser: function() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    },
    
    // Remove dados do usuário ao fazer logout
    clearUser: function() {
        localStorage.removeItem('userToken');
        localStorage.removeItem('userData');
    },
    
    // Realiza login
    login: async function(email, senha) {
        const response = await API.auth.login(email, senha);
        
        if (response.ok) {
            this.setUser(response.data.professor);
            return { success: true, data: response.data };
        } else {
            return { success: false, message: response.data.mensagem || 'Erro ao fazer login' };
        }
    },
    
    // Realiza cadastro
    register: async function(nome, email, senha) {
        const response = await API.auth.cadastro(nome, email, senha);
        
        if (response.ok) {
            return { success: true, data: response.data };
        } else {
            return { success: false, message: response.data.mensagem || 'Erro ao cadastrar' };
        }
    },
    
    // Realiza logout
    logout: async function() {
        await API.auth.logout();
        this.clearUser();
    },
    
    // Verifica se a sessão ainda é válida
    checkSession: async function() {
        if (!this.isAuthenticated()) {
            return false;
        }
        
        const response = await API.auth.perfil();
        
        if (response.ok) {
            this.setUser(response.data.professor);
            return true;
        } else {
            this.clearUser();
            return false;
        }
    }
};
