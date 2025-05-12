// Обработка авторизации и регистрации
const AuthHandler = {
    // DOM элементы
    elements: {
        authSection: document.getElementById('auth-section'),
        mainContent: document.getElementById('main-content'),
        authForm: document.getElementById('auth-form'),
        authTitle: document.getElementById('auth-title'),
        authError: document.getElementById('auth-error'),
        usernameInput: document.getElementById('username'),
        passwordInput: document.getElementById('password'),
        emailInput: document.getElementById('email'),
        fullNameInput: document.getElementById('full_name'),
        toggleButton: document.getElementById('toggle-auth-mode'),
        registerFields: document.querySelectorAll('.register-field'),
        navLogin: document.getElementById('nav-login'),
        navRegister: document.getElementById('nav-register'),
        navLogout: document.getElementById('nav-logout'),
    },

    // Режим авторизации (login или register)
    mode: 'login',

    // Инициализация
    init() {
        // Проверяем, все ли DOM-элементы найдены
        const missingElements = [];
        for (const [key, value] of Object.entries(this.elements)) {
            if (!value && !['registerFields'].includes(key)) {
                missingElements.push(key);
                console.error(`DOM element ${key} is missing`);
            }
        }
        
        if (missingElements.length > 0) {
            console.error('Missing DOM elements:', missingElements);
        }
        
        // Проверяем, есть ли сохраненный токен
        if (ApiService.loadToken()) {
            this.showMainContent();
        } else {
            this.showAuthForm();
        }

        // Обработчики событий
        if (this.elements.authForm) {
            this.elements.authForm.addEventListener('submit', (e) => this.handleAuth(e));
            console.log('Auth form submit handler attached');
        }
        
        if (this.elements.toggleButton) {
            this.elements.toggleButton.addEventListener('click', () => this.toggleMode());
            console.log('Toggle mode button handler attached');
        }
        
        if (this.elements.navLogin) {
            this.elements.navLogin.addEventListener('click', (e) => {
                e.preventDefault();
                this.showLoginForm();
                console.log('Nav login clicked');
            });
        }
        
        if (this.elements.navRegister) {
            this.elements.navRegister.addEventListener('click', (e) => {
                e.preventDefault();
                this.showRegisterForm();
                console.log('Nav register clicked');
            });
        }
        
        if (this.elements.navLogout) {
            this.elements.navLogout.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
                console.log('Nav logout clicked');
            });
        }

        // Прослушиваем событие logout
        window.addEventListener('auth:logout', () => this.logout());
        
        console.log('AuthHandler initialized');
    },

    // Обработка формы авторизации/регистрации
    async handleAuth(event) {
        event.preventDefault();
        console.log("Form submitted in mode:", this.mode);

        const username = this.elements.usernameInput.value.trim();
        const password = this.elements.passwordInput.value.trim();

        if (!username || !password) {
            this.showError('Имя пользователя и пароль обязательны');
            return;
        }

        try {
            this.clearError();

            if (this.mode === 'login') {
                // Обработка входа
                console.log("Attempting login for:", username);
                const response = await ApiService.auth.login(username, password);
                console.log("Login response:", response);
                
                if (response && response.access_token) {
                    ApiService.setToken(response.access_token);
                    this.showMainContent();
                } else {
                    throw new Error('Не удалось получить токен доступа');
                }
            } else {
                // Обработка регистрации
                const email = this.elements.emailInput.value.trim();
                const fullName = this.elements.fullNameInput.value.trim();

                if (!email) {
                    throw new Error('Email обязателен');
                }

                const userData = {
                    username,
                    password,
                    email,
                    full_name: fullName
                };

                console.log("Attempting registration for:", username);
                await ApiService.auth.register(userData);
                console.log("Registration successful");
                
                // После успешной регистрации переключаемся на форму входа
                this.mode = 'login';
                this.updateFormMode();
                this.showSuccess('Регистрация успешна. Теперь вы можете войти.');
            }
        } catch (error) {
            console.error("Auth error:", error);
            this.showError(error.message || 'Произошла ошибка при обработке запроса');
        }
    },

    // Переключение между режимами входа и регистрации
    toggleMode() {
        this.mode = this.mode === 'login' ? 'register' : 'login';
        this.updateFormMode();
    },

    // Обновление формы в соответствии с режимом
    updateFormMode() {
        if (this.mode === 'login') {
            this.elements.authTitle.textContent = 'Авторизация';
            this.elements.toggleButton.textContent = 'Регистрация';
            this.elements.authForm.querySelector('button[type="submit"]').textContent = 'Войти';
            this.elements.registerFields.forEach(field => field.classList.add('d-none'));
        } else {
            this.elements.authTitle.textContent = 'Регистрация';
            this.elements.toggleButton.textContent = 'У меня уже есть аккаунт';
            this.elements.authForm.querySelector('button[type="submit"]').textContent = 'Зарегистрироваться';
            this.elements.registerFields.forEach(field => field.classList.remove('d-none'));
        }
    },

    // Показать форму авторизации
    showLoginForm() {
        console.log("Showing login form");
        this.clearError();
        this.mode = 'login';
        this.updateFormMode();
        this.showAuthForm();
    },

    // Показать форму регистрации
    showRegisterForm() {
        console.log("Showing register form");
        this.clearError();
        this.mode = 'register';
        this.updateFormMode();
        this.showAuthForm();
    },

    // Показать форму авторизации
    showAuthForm() {
        this.elements.mainContent.classList.add('d-none');
        this.elements.authSection.classList.remove('d-none');
        this.elements.navLogout.parentElement.classList.add('d-none');
        this.elements.navLogin.parentElement.classList.remove('d-none');
        this.elements.navRegister.parentElement.classList.remove('d-none');
    },

    // Показать основное содержимое
    showMainContent() {
        this.elements.authSection.classList.add('d-none');
        this.elements.mainContent.classList.remove('d-none');
        this.elements.navLogin.parentElement.classList.add('d-none');
        this.elements.navRegister.parentElement.classList.add('d-none');
        this.elements.navLogout.parentElement.classList.remove('d-none');

        // Показываем секцию клиентов по умолчанию
        document.getElementById('clients-section').classList.remove('d-none');
        document.querySelectorAll('.content-section').forEach(section => {
            if (section.id !== 'clients-section') {
                section.classList.add('d-none');
            }
        });

        // Загружаем данные для отображения
        window.dispatchEvent(new CustomEvent('load:clients'));
    },

    // Выход из системы
    logout() {
        ApiService.clearToken();
        this.showAuthForm();
    },

    // Показать ошибку
    showError(message) {
        this.elements.authError.textContent = message;
        this.elements.authError.classList.remove('d-none');
    },

    // Показать сообщение об успехе
    showSuccess(message) {
        this.elements.authError.textContent = message;
        this.elements.authError.classList.remove('d-none', 'alert-danger');
        this.elements.authError.classList.add('alert-success');
    },

    // Очистить сообщение об ошибке
    clearError() {
        this.elements.authError.textContent = '';
        this.elements.authError.classList.add('d-none');
        this.elements.authError.classList.remove('alert-success');
        this.elements.authError.classList.add('alert-danger');
    }
};
