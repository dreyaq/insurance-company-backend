// Главный файл JavaScript для инициализации всех компонентов
document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, что все необходимые модули загружены
    if (!window.ApiService) {
        console.error('ApiService is not loaded!');
    }
    if (!window.AuthHandler) {
        console.error('AuthHandler is not loaded!');
    }
    
    console.log('Initializing app...');
    
    // Инициализируем обработчики и модули
    try {
        AuthHandler.init();
        ClientsHandler.init();
        PoliciesHandler.init();
        ClaimsHandler.init();
        PaymentsHandler.init();
        console.log('All handlers initialized successfully');
    } catch (error) {
        console.error('Error initializing handlers:', error);
    }// Обработчики для навигационного меню
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            // Предотвращаем стандартное поведение для всех навигационных ссылок
            e.preventDefault();
            
            // Проверяем, относится ли ссылка к авторизации
            if (this.id === 'nav-login' || this.id === 'nav-register' || this.id === 'nav-logout') {
                // Обработчики уже настроены в AuthHandler, дополнительные действия не требуются
                return;
            }
            
            // Для навигационных ссылок основных секций
            if (this.id.startsWith('nav-')) {
                // Активация ссылки
                document.querySelectorAll('.navbar-nav .nav-link').forEach(l => {
                    l.classList.remove('active');
                });
                this.classList.add('active');
                
                // Переключение на соответствующую секцию
                const section = this.id.replace('nav-', '');
                switch(section) {
                    case 'clients':
                        ClientsHandler.showClientsSection();
                        break;
                    case 'policies':
                        PoliciesHandler.showPoliciesSection();
                        break;
                    case 'claims':
                        ClaimsHandler.showClaimsSection();
                        break;
                    case 'payments':
                        PaymentsHandler.showPaymentsSection();
                        break;
                }
            }
        });
    });

    // Обработчик закрытия модального окна
    document.addEventListener('click', function(e) {
        // Если кликнули по кнопке закрытия (крестик) или кнопке "Отмена"
        if (e.target.classList.contains('btn-close') || 
            (e.target.tagName === 'BUTTON' && e.target.textContent.trim() === 'Отмена')) {
            // Найдем и закроем модальное окно
            const modalElem = document.getElementById('form-modal');
            if (modalElem) {
                const modalInstance = bootstrap.Modal.getInstance(modalElem);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
    });

    // По умолчанию активируем ссылку на клиентов
    document.getElementById('nav-clients').classList.add('active');
});
