// Обработка функциональности полисов
const PoliciesHandler = {
    // DOM элементы
    elements: {
        policiesSection: document.getElementById('policies-section'),
        policiesTableBody: document.getElementById('policies-table-body'),
        addPolicyBtn: document.getElementById('add-policy-btn'),
        policySearch: document.getElementById('policy-search'),
        policySearchBtn: document.getElementById('policy-search-btn'),
        formModal: new bootstrap.Modal(document.getElementById('form-modal')),
        modalTitle: document.getElementById('modal-title'),
        modalBody: document.getElementById('modal-body')
    },

    // Текущие данные
    currentPolicies: [],
    clientsList: [],
    editingPolicyId: null,

    // Инициализация
    init() {
        // Обработчики событий
        this.elements.addPolicyBtn.addEventListener('click', () => this.showAddPolicyForm());
        this.elements.policySearchBtn.addEventListener('click', () => this.searchPolicies());
        this.elements.policySearch.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.searchPolicies();
        });

        // Обработчик для меню
        document.getElementById('nav-policies').addEventListener('click', (e) => {
            e.preventDefault();
            this.showPoliciesSection();
        });
    },    // Загрузка списка полисов
    async loadPolicies() {
        try {
            const policies = await ApiService.policies.getAll();
            this.currentPolicies = policies;
            
            // Загружаем данные клиентов для каждого полиса
            await this.loadClientNames();
            
            this.renderPoliciesTable();
        } catch (error) {
            this.showError('Не удалось загрузить список полисов: ' + error.message);
        }
    },
    
    // Загрузка имен клиентов для полисов
    async loadClientNames() {
        try {
            const clients = await ApiService.clients.getAll('', 0, 1000);
            
            // Создаем словарь клиентов по ID
            const clientsMap = {};
            clients.forEach(client => {
                clientsMap[client.id] = `${client.last_name} ${client.first_name}`;
            });
            
            // Добавляем имена клиентов к полисам
            this.currentPolicies.forEach(policy => {
                if (policy.client_id && clientsMap[policy.client_id]) {
                    policy.client_name = clientsMap[policy.client_id];
                }
            });
        } catch (error) {
            console.error('Ошибка загрузки данных клиентов:', error);
        }
    },

    // Загрузка списка клиентов для формы
    async loadClientsList() {
        try {
            this.clientsList = await ApiService.clients.getAll('', 0, 1000);
        } catch (error) {
            console.error('Ошибка загрузки клиентов:', error);
            this.clientsList = [];
        }
    },

    // Отображение таблицы полисов
    renderPoliciesTable() {
        const tbody = this.elements.policiesTableBody;
        tbody.innerHTML = '';

        if (this.currentPolicies.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="9" class="text-center">Нет данных</td>';
            tbody.appendChild(tr);
            return;
        }        this.currentPolicies.forEach(policy => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${policy.id.substring(0, 8)}...</td>
                <td>${policy.policy_number}</td>
                <td>${this.getPolicyTypeName(policy.type)}</td>
                <td>${policy.client_name || 'Загрузка...'}</td>
                <td>${policy.start_date}</td>
                <td>${policy.end_date}</td>
                <td>${policy.premium_amount}</td>
                <td>${this.getPolicyStatusBadge(policy.status)}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-policy" data-id="${policy.id}">
                        <i class="bi bi-pencil"></i> Изменить
                    </button>
                    <button class="btn btn-sm btn-danger delete-policy" data-id="${policy.id}">
                        <i class="bi bi-trash"></i> Удалить
                    </button>
                </td>
            `;
            tbody.appendChild(tr);

            // Добавляем обработчики для кнопок
            const editBtn = tr.querySelector('.edit-policy');
            const deleteBtn = tr.querySelector('.delete-policy');

            editBtn.addEventListener('click', () => this.showEditPolicyForm(policy.id));
            deleteBtn.addEventListener('click', () => this.confirmDeletePolicy(policy.id));
        });
    },    // Получение HTML-кода для отображения статуса полиса
    getPolicyStatusBadge(status) {
        const statusMap = {
            'pending': '<span class="badge bg-secondary">В ожидании</span>',
            'active': '<span class="badge bg-success">Активен</span>',
            'expired': '<span class="badge bg-warning text-dark">Истек</span>',
            'canceled': '<span class="badge bg-danger">Отменен</span>'
        };
        
        return statusMap[status] || `<span class="badge bg-secondary">${status}</span>`;
    },
    
    // Получение читаемого имени типа полиса
    getPolicyTypeName(type) {
        const typeMap = {
            'life': 'Страхование жизни',
            'health': 'Медицинское страхование',
            'property': 'Страхование имущества',
            'vehicle': 'Автострахование',
            'travel': 'Страхование путешествий'
        };
        
        return typeMap[type] || type;
    },

    // Поиск полисов
    searchPolicies() {
        const searchText = this.elements.policySearch.value.trim();
        // В API нет поиска по номеру полиса, поэтому фильтруем локально
        if (searchText) {
            const filteredPolicies = this.currentPolicies.filter(policy => 
                policy.policy_number.toLowerCase().includes(searchText.toLowerCase())
            );
            this.currentPolicies = filteredPolicies;
            this.renderPoliciesTable();
        } else {
            this.loadPolicies();
        }
    },

    // Показ формы добавления полиса
    async showAddPolicyForm() {
        await this.loadClientsList();
        
        this.editingPolicyId = null;
        this.elements.modalTitle.textContent = 'Добавить полис';
        
        const clientsOptions = this.clientsList.map(client => 
            `<option value="${client.id}">${client.last_name} ${client.first_name}</option>`
        ).join('');
        
        this.elements.modalBody.innerHTML = `
            <form id="policy-form">
                <div class="mb-3">
                    <label for="policy_number" class="form-label">Номер полиса</label>
                    <input type="text" class="form-control" id="policy_number" required>
                </div>
                <div class="mb-3">
                    <label for="client_id" class="form-label">Клиент</label>
                    <select class="form-select" id="client_id" required>
                        <option value="">Выберите клиента</option>
                        ${clientsOptions}
                    </select>
                </div>                <div class="mb-3">
                    <label for="insurance_type" class="form-label">Тип страхования</label>
                    <select class="form-select" id="insurance_type" required>
                        <option value="life">Страхование жизни</option>
                        <option value="health">Медицинское страхование</option>
                        <option value="property">Страхование имущества</option>
                        <option value="vehicle">Автострахование</option>
                        <option value="travel">Страхование путешествий</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="start_date" class="form-label">Дата начала</label>
                    <input type="date" class="form-control" id="start_date" required>
                </div>
                <div class="mb-3">
                    <label for="end_date" class="form-label">Дата окончания</label>
                    <input type="date" class="form-control" id="end_date" required>
                </div>
                <div class="mb-3">
                    <label for="premium_amount" class="form-label">Сумма страховой премии</label>
                    <input type="number" step="0.01" class="form-control" id="premium_amount" required>
                </div>
                <div class="mb-3">
                    <label for="coverage_amount" class="form-label">Сумма страхового покрытия</label>
                    <input type="number" step="0.01" class="form-control" id="coverage_amount" required>
                </div>                <div class="mb-3">
                    <label for="status" class="form-label">Статус</label>
                    <select class="form-select" id="status" required>
                        <option value="pending">В ожидании</option>
                        <option value="active">Активен</option>
                        <option value="expired">Истек</option>
                        <option value="canceled">Отменен</option>
                    </select>
                </div>
                <div class="alert alert-danger d-none" id="policy-form-error"></div>
                <div class="d-flex justify-content-end">
                    <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Отмена</button>
                    <button type="submit" class="btn btn-primary">Сохранить</button>
                </div>
            </form>
        `;

        // Добавляем обработчик отправки формы
        const form = this.elements.modalBody.querySelector('#policy-form');
        form.addEventListener('submit', (e) => this.handlePolicyFormSubmit(e));

        // Устанавливаем текущую дату и дату через год
        const today = new Date();
        const nextYear = new Date();
        nextYear.setFullYear(today.getFullYear() + 1);
        
        form.start_date.value = today.toISOString().split('T')[0];
        form.end_date.value = nextYear.toISOString().split('T')[0];

        this.elements.formModal.show();
    },

    // Показ формы редактирования полиса
    async showEditPolicyForm(policyId) {
        try {
            await this.loadClientsList();
            
            const policy = await ApiService.policies.getById(policyId);
            this.editingPolicyId = policyId;
            
            this.elements.modalTitle.textContent = 'Редактировать полис';
            
            const clientsOptions = this.clientsList.map(client => 
                `<option value="${client.id}" ${policy.client_id === client.id ? 'selected' : ''}>${client.last_name} ${client.first_name}</option>`
            ).join('');            const insuranceTypes = {
                'life': 'Страхование жизни',
                'health': 'Медицинское страхование',
                'property': 'Страхование имущества',
                'vehicle': 'Автострахование',
                'travel': 'Страхование путешествий'
            };
            
            const insuranceTypeOptions = Object.entries(insuranceTypes).map(([value, text]) => 
                `<option value="${value}" ${policy.type === value ? 'selected' : ''}>${text}</option>`
            ).join('');const statusOptions = [
                ['pending', 'В ожидании'],
                ['active', 'Активен'],
                ['expired', 'Истек'],
                ['canceled', 'Отменен']
            ].map(([value, text]) => 
                `<option value="${value}" ${policy.status === value ? 'selected' : ''}>${text}</option>`
            ).join('');
            
            this.elements.modalBody.innerHTML = `
                <form id="policy-form">
                    <div class="mb-3">
                        <label for="policy_number" class="form-label">Номер полиса</label>
                        <input type="text" class="form-control" id="policy_number" value="${policy.policy_number}" required>
                    </div>
                    <div class="mb-3">
                        <label for="client_id" class="form-label">Клиент</label>
                        <select class="form-select" id="client_id" required>
                            <option value="">Выберите клиента</option>
                            ${clientsOptions}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="insurance_type" class="form-label">Тип страхования</label>
                        <select class="form-select" id="insurance_type" required>
                            ${insuranceTypeOptions}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="start_date" class="form-label">Дата начала</label>
                        <input type="date" class="form-control" id="start_date" value="${policy.start_date}" required>
                    </div>
                    <div class="mb-3">
                        <label for="end_date" class="form-label">Дата окончания</label>
                        <input type="date" class="form-control" id="end_date" value="${policy.end_date}" required>
                    </div>
                    <div class="mb-3">
                        <label for="premium_amount" class="form-label">Сумма страховой премии</label>
                        <input type="number" step="0.01" class="form-control" id="premium_amount" value="${policy.premium_amount}" required>
                    </div>
                    <div class="mb-3">
                        <label for="coverage_amount" class="form-label">Сумма страхового покрытия</label>
                        <input type="number" step="0.01" class="form-control" id="coverage_amount" value="${policy.coverage_amount}" required>
                    </div>
                    <div class="mb-3">
                        <label for="status" class="form-label">Статус</label>
                        <select class="form-select" id="status" required>
                            ${statusOptions}
                        </select>
                    </div>
                    <div class="alert alert-danger d-none" id="policy-form-error"></div>
                    <div class="d-flex justify-content-end">
                        <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Отмена</button>
                        <button type="submit" class="btn btn-primary">Сохранить</button>
                    </div>
                </form>
            `;

            // Добавляем обработчик отправки формы
            const form = this.elements.modalBody.querySelector('#policy-form');
            form.addEventListener('submit', (e) => this.handlePolicyFormSubmit(e));

            this.elements.formModal.show();
        } catch (error) {
            this.showError('Не удалось загрузить данные полиса: ' + error.message);
        }
    },    // Обработка отправки формы полиса
    async handlePolicyFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const errorElement = form.querySelector('#policy-form-error');
        
        try {            errorElement.classList.add('d-none');            
            const policyData = {
                policy_number: form.policy_number.value.trim(),
                client_id: form.client_id.value,
                type: form.insurance_type.value,
                start_date: form.start_date.value,
                end_date: form.end_date.value,
                premium_amount: parseFloat(form.premium_amount.value),
                coverage_amount: parseFloat(form.coverage_amount.value),
                status: form.status.value
            };
            
            if (this.editingPolicyId) {
                // Обновление полиса
                await ApiService.policies.update(this.editingPolicyId, policyData);
            } else {
                // Создание нового полиса
                await ApiService.policies.create(policyData);
            }
            
            this.elements.formModal.hide();
            this.loadPolicies(); // Перезагружаем список полисов
        } catch (error) {
            errorElement.textContent = error.message;
            errorElement.classList.remove('d-none');
        }
    },

    // Подтверждение удаления полиса
    confirmDeletePolicy(policyId) {
        if (confirm('Вы уверены, что хотите удалить этот полис?')) {
            this.deletePolicy(policyId);
        }
    },

    // Удаление полиса
    async deletePolicy(policyId) {
        try {
            await ApiService.policies.delete(policyId);
            this.loadPolicies(); // Перезагружаем список полисов
        } catch (error) {
            this.showError('Не удалось удалить полис: ' + error.message);
        }
    },

    // Показать секцию полисов
    showPoliciesSection() {
        // Скрыть все секции
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // Показать секцию полисов
        this.elements.policiesSection.classList.remove('d-none');
        
        // Загрузить данные, если нужно
        this.loadPolicies();
    },

    // Показать ошибку
    showError(message) {
        alert(message);
    }
};
