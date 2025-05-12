// Обработка функциональности клиентов
const ClientsHandler = {
    // DOM элементы
    elements: {
        clientsSection: document.getElementById('clients-section'),
        clientsTableBody: document.getElementById('clients-table-body'),
        addClientBtn: document.getElementById('add-client-btn'),
        clientSearch: document.getElementById('client-search'),
        clientSearchBtn: document.getElementById('client-search-btn'),
        formModal: new bootstrap.Modal(document.getElementById('form-modal')),
        modalTitle: document.getElementById('modal-title'),
        modalBody: document.getElementById('modal-body')
    },

    // Текущие данные
    currentClients: [],
    editingClientId: null,

    // Инициализация
    init() {
        // Обработчики событий
        this.elements.addClientBtn.addEventListener('click', () => this.showAddClientForm());
        this.elements.clientSearchBtn.addEventListener('click', () => this.searchClients());
        this.elements.clientSearch.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.searchClients();
        });

        // Прослушиваем событие загрузки клиентов
        window.addEventListener('load:clients', () => this.loadClients());
        
        // Обработчик для меню
        document.getElementById('nav-clients').addEventListener('click', (e) => {
            e.preventDefault();
            this.showClientsSection();
        });
    },

    // Загрузка списка клиентов
    async loadClients(nameFilter = '') {
        try {
            const clients = await ApiService.clients.getAll(nameFilter);
            this.currentClients = clients;
            this.renderClientsTable();
        } catch (error) {
            this.showError('Не удалось загрузить список клиентов: ' + error.message);
        }
    },

    // Отображение таблицы клиентов
    renderClientsTable() {
        const tbody = this.elements.clientsTableBody;
        tbody.innerHTML = '';

        if (this.currentClients.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="6" class="text-center">Нет данных</td>';
            tbody.appendChild(tr);
            return;
        }

        this.currentClients.forEach(client => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${client.id.substring(0, 8)}...</td>
                <td>${client.first_name}</td>
                <td>${client.last_name}</td>
                <td>${client.email}</td>
                <td>${client.phone || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-client" data-id="${client.id}">
                        <i class="bi bi-pencil"></i> Изменить
                    </button>
                    <button class="btn btn-sm btn-danger delete-client" data-id="${client.id}">
                        <i class="bi bi-trash"></i> Удалить
                    </button>
                </td>
            `;
            tbody.appendChild(tr);

            // Добавляем обработчики для кнопок
            const editBtn = tr.querySelector('.edit-client');
            const deleteBtn = tr.querySelector('.delete-client');

            editBtn.addEventListener('click', () => this.showEditClientForm(client.id));
            deleteBtn.addEventListener('click', () => this.confirmDeleteClient(client.id));
        });
    },

    // Поиск клиентов
    searchClients() {
        const searchText = this.elements.clientSearch.value.trim();
        this.loadClients(searchText);
    },

    // Показ формы добавления клиента
    showAddClientForm() {
        this.editingClientId = null;
        this.elements.modalTitle.textContent = 'Добавить клиента';
        
        this.elements.modalBody.innerHTML = `
            <form id="client-form">
                <div class="mb-3">
                    <label for="first_name" class="form-label">Имя</label>
                    <input type="text" class="form-control" id="first_name" required>
                </div>
                <div class="mb-3">
                    <label for="last_name" class="form-label">Фамилия</label>
                    <input type="text" class="form-control" id="last_name" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" required>
                </div>
                <div class="mb-3">
                    <label for="phone" class="form-label">Телефон</label>
                    <input type="tel" class="form-control" id="phone">
                </div>
                <div class="mb-3">
                    <label for="birth_date" class="form-label">Дата рождения</label>
                    <input type="date" class="form-control" id="birth_date" required>
                </div>
                <div class="mb-3">
                    <label for="address" class="form-label">Адрес</label>
                    <input type="text" class="form-control" id="address">
                </div>                <div class="mb-3">
                    <label for="passport_number" class="form-label">Паспорт</label>
                    <input type="text" class="form-control" id="passport_number">
                </div>
                <div class="alert alert-danger d-none" id="client-form-error"></div>
                <div class="d-flex justify-content-end">
                    <button type="button" class="btn btn-secondary me-2" id="cancel-btn">Отмена</button>
                    <button type="submit" class="btn btn-primary">Сохранить</button>
                </div>
            </form>
        `;

        // Добавляем обработчик отправки формы
        const form = this.elements.modalBody.querySelector('#client-form');
        form.addEventListener('submit', (e) => this.handleClientFormSubmit(e));
        
        // Добавляем обработчик для кнопки отмены
        const cancelBtn = this.elements.modalBody.querySelector('#cancel-btn');
        cancelBtn.addEventListener('click', () => this.elements.formModal.hide());

        this.elements.formModal.show();
    },

    // Показ формы редактирования клиента
    async showEditClientForm(clientId) {
        try {
            const client = await ApiService.clients.getById(clientId);
            this.editingClientId = clientId;
            
            this.elements.modalTitle.textContent = 'Редактировать клиента';
            
            this.elements.modalBody.innerHTML = `
                <form id="client-form">
                    <div class="mb-3">
                        <label for="first_name" class="form-label">Имя</label>
                        <input type="text" class="form-control" id="first_name" value="${client.first_name}" required>
                    </div>
                    <div class="mb-3">
                        <label for="last_name" class="form-label">Фамилия</label>
                        <input type="text" class="form-control" id="last_name" value="${client.last_name}" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" value="${client.email}" required>
                    </div>
                    <div class="mb-3">
                        <label for="phone" class="form-label">Телефон</label>
                        <input type="tel" class="form-control" id="phone" value="${client.phone || ''}">
                    </div>
                    <div class="mb-3">
                        <label for="birth_date" class="form-label">Дата рождения</label>
                        <input type="date" class="form-control" id="birth_date" value="${client.birth_date}" required>
                    </div>
                    <div class="mb-3">
                        <label for="address" class="form-label">Адрес</label>
                        <input type="text" class="form-control" id="address" value="${client.address || ''}">
                    </div>
                    <div class="mb-3">
                        <label for="passport_number" class="form-label">Паспорт</label>
                        <input type="text" class="form-control" id="passport_number" value="${client.passport_number || ''}">
                    </div>                <div class="alert alert-danger d-none" id="client-form-error"></div>
                    <div class="d-flex justify-content-end">
                        <button type="button" class="btn btn-secondary me-2" id="cancel-btn">Отмена</button>
                        <button type="submit" class="btn btn-primary">Сохранить</button>
                    </div>
                </form>
            `;

            // Добавляем обработчик отправки формы
            const form = this.elements.modalBody.querySelector('#client-form');
            form.addEventListener('submit', (e) => this.handleClientFormSubmit(e));
            
            // Добавляем обработчик для кнопки отмены
            const cancelBtn = this.elements.modalBody.querySelector('#cancel-btn');
            cancelBtn.addEventListener('click', () => this.elements.formModal.hide());

            this.elements.formModal.show();
        } catch (error) {
            this.showError('Не удалось загрузить данные клиента: ' + error.message);
        }
    },

    // Обработка отправки формы клиента
    async handleClientFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const errorElement = form.querySelector('#client-form-error');
        
        try {
            errorElement.classList.add('d-none');
            
            const clientData = {
                first_name: form.first_name.value.trim(),
                last_name: form.last_name.value.trim(),
                email: form.email.value.trim(),
                phone: form.phone.value.trim() || null,
                birth_date: form.birth_date.value,
                address: form.address.value.trim() || null,
                passport_number: form.passport_number.value.trim() || null
            };
            
            if (this.editingClientId) {
                // Обновление клиента
                await ApiService.clients.update(this.editingClientId, clientData);
            } else {
                // Создание нового клиента
                await ApiService.clients.create(clientData);
            }
            
            this.elements.formModal.hide();
            this.loadClients(); // Перезагружаем список клиентов
        } catch (error) {
            errorElement.textContent = error.message;
            errorElement.classList.remove('d-none');
        }
    },

    // Подтверждение удаления клиента
    confirmDeleteClient(clientId) {
        if (confirm('Вы уверены, что хотите удалить этого клиента?')) {
            this.deleteClient(clientId);
        }
    },    // Удаление клиента
    async deleteClient(clientId) {
        try {
            await ApiService.clients.delete(clientId);
            this.loadClients(); // Перезагружаем список клиентов
        } catch (error) {
            // Отображаем более подробное сообщение об ошибке
            if (error.message && error.message.includes('полис')) {
                this.showError('Невозможно удалить клиента, так как у него есть связанные полисы. Пожалуйста, сначала удалите все полисы клиента.');
            } else {
                this.showError('Не удалось удалить клиента: ' + error.message);
            }
        }
    },

    // Показать секцию клиентов
    showClientsSection() {
        // Скрыть все секции
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // Показать секцию клиентов
        this.elements.clientsSection.classList.remove('d-none');
        
        // Загрузить данные, если нужно
        this.loadClients();
    },

    // Показать ошибку
    showError(message) {
        alert(message);
    }
};
