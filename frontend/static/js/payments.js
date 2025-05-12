// Обработка функциональности платежей
const PaymentsHandler = {
    // DOM элементы
    elements: {
        paymentsSection: document.getElementById('payments-section'),
        paymentsTableBody: document.getElementById('payments-table-body'),
        addPaymentBtn: document.getElementById('add-payment-btn'),
        paymentSearch: document.getElementById('payment-search'),
        paymentSearchBtn: document.getElementById('payment-search-btn'),
        formModal: new bootstrap.Modal(document.getElementById('form-modal')),
        modalTitle: document.getElementById('modal-title'),
        modalBody: document.getElementById('modal-body')
    },

    // Текущие данные
    currentPayments: [],
    clientsList: [],
    policiesList: [],
    claimsList: [],
    editingPaymentId: null,

    // Инициализация
    init() {
        // Обработчики событий
        this.elements.addPaymentBtn.addEventListener('click', () => this.showAddPaymentForm());
        this.elements.paymentSearchBtn.addEventListener('click', () => this.searchPayments());
        this.elements.paymentSearch.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.searchPayments();
        });

        // Обработчик для меню
        document.getElementById('nav-payments').addEventListener('click', (e) => {
            e.preventDefault();
            this.showPaymentsSection();
        });
    },    // Загрузка списка платежей
    async loadPayments() {
        try {
            const payments = await ApiService.payments.getAll();
            this.currentPayments = payments;
            
            // Загружаем связанные данные для платежей
            await this.loadRelatedData();
            
            this.renderPaymentsTable();
        } catch (error) {
            this.showError('Не удалось загрузить список платежей: ' + error.message);
        }
    },
    
    // Загрузка связанных данных (клиенты, полисы, страховые случаи)
    async loadRelatedData() {
        try {
            // Загружаем клиентов
            const clients = await ApiService.clients.getAll('', 0, 1000);
            const clientsMap = {};
            clients.forEach(client => {
                clientsMap[client.id] = `${client.last_name} ${client.first_name}`;
            });
            
            // Загружаем полисы
            const policies = await ApiService.policies.getAll(0, 1000);
            const policiesMap = {};
            policies.forEach(policy => {
                policiesMap[policy.id] = policy.policy_number;
            });
            
            // Загружаем страховые случаи
            const claims = await ApiService.claims.getAll(0, 1000);
            const claimsMap = {};
            claims.forEach(claim => {
                claimsMap[claim.id] = claim.description;
            });
            
            // Добавляем данные к платежам
            this.currentPayments.forEach(payment => {
                if (payment.client_id && clientsMap[payment.client_id]) {
                    payment.client_name = clientsMap[payment.client_id];
                }
                
                if (payment.policy_id && policiesMap[payment.policy_id]) {
                    payment.policy_number = policiesMap[payment.policy_id];
                }
                
                if (payment.claim_id && claimsMap[payment.claim_id]) {
                    payment.claim_description = claimsMap[payment.claim_id];
                }
            });
        } catch (error) {
            console.error('Ошибка загрузки связанных данных:', error);
        }
    },

    // Загрузка списков для формы
    async loadOptionsLists() {
        try {
            this.clientsList = await ApiService.clients.getAll('', 0, 1000);
            this.policiesList = await ApiService.policies.getAll(0, 1000);
            this.claimsList = await ApiService.claims.getAll(0, 1000);
        } catch (error) {
            console.error('Ошибка загрузки списков:', error);
            this.clientsList = [];
            this.policiesList = [];
            this.claimsList = [];
        }
    },

    // Отображение таблицы платежей
    renderPaymentsTable() {
        const tbody = this.elements.paymentsTableBody;
        tbody.innerHTML = '';

        if (this.currentPayments.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="8" class="text-center">Нет данных</td>';
            tbody.appendChild(tr);
            return;
        }        this.currentPayments.forEach(payment => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${payment.id.substring(0, 8)}...</td>
                <td>${payment.payment_date}</td>
                <td>${this.getPaymentTypeBadge(payment.payment_type)}</td>
                <td>${payment.amount}</td>
                <td>${this.getPaymentStatusBadge(payment.status)}</td>
                <td>${payment.client_name || 'Загрузка...'}</td>
                <td>${payment.policy_number || payment.claim_description || 'Загрузка...'}</td>
                <td>                    <button class="btn btn-sm btn-primary edit-payment" data-id="${payment.id}">
                        <i class="bi bi-pencil"></i> Изменить
                    </button>
                    <button class="btn btn-sm btn-success process-payment" data-id="${payment.id}" ${payment.status === 'completed' ? 'disabled' : ''}>
                        <i class="bi bi-check-circle"></i> Обработать
                    </button>
                    <button class="btn btn-sm btn-danger delete-payment" data-id="${payment.id}">
                        <i class="bi bi-trash"></i> Удалить
                    </button>
                </td>
            `;
            tbody.appendChild(tr);

            // Добавляем обработчики для кнопок
            const editBtn = tr.querySelector('.edit-payment');
            const processBtn = tr.querySelector('.process-payment');
            const deleteBtn = tr.querySelector('.delete-payment');

            editBtn.addEventListener('click', () => this.showEditPaymentForm(payment.id));
            processBtn.addEventListener('click', () => this.processPayment(payment.id));
            deleteBtn.addEventListener('click', () => this.confirmDeletePayment(payment.id));
        });
    },    // Получение HTML-кода для отображения типа платежа
    getPaymentTypeBadge(type) {
        const typeMap = {
            'premium': '<span class="badge bg-primary">Страховой взнос</span>',
            'claim_payout': '<span class="badge bg-success">Страховая выплата</span>',
            'refund': '<span class="badge bg-warning text-dark">Возврат</span>'
        };
        
        return typeMap[type] || `<span class="badge bg-secondary">${type}</span>`;
    },

    // Получение HTML-кода для отображения статуса платежа
    getPaymentStatusBadge(status) {
        const statusMap = {
            'pending': '<span class="badge bg-warning text-dark">В ожидании</span>',
            'completed': '<span class="badge bg-success">Завершен</span>',
            'failed': '<span class="badge bg-danger">Ошибка</span>',
            'refunded': '<span class="badge bg-secondary">Возврат</span>'
        };
        
        return statusMap[status] || `<span class="badge bg-secondary">${status}</span>`;
    },

    // Поиск платежей
    searchPayments() {
        const searchText = this.elements.paymentSearch.value.trim();
        // В API нет поиска по ID платежа, поэтому фильтруем локально
        if (searchText) {
            const filteredPayments = this.currentPayments.filter(payment => 
                payment.id.toLowerCase().includes(searchText.toLowerCase())
            );
            this.currentPayments = filteredPayments;
            this.renderPaymentsTable();
        } else {
            this.loadPayments();
        }
    },

    // Показ формы добавления платежа
    async showAddPaymentForm() {
        await this.loadOptionsLists();
        
        this.editingPaymentId = null;
        this.elements.modalTitle.textContent = 'Добавить платеж';
        
        const clientsOptions = this.clientsList.map(client => 
            `<option value="${client.id}">${client.last_name} ${client.first_name}</option>`
        ).join('');
        
        const policiesOptions = this.policiesList.map(policy => 
            `<option value="${policy.id}">${policy.policy_number} (${policy.client_name})</option>`
        ).join('');
        
        const claimsOptions = this.claimsList.map(claim => 
            `<option value="${claim.id}">${claim.description.substring(0, 30)}... (${claim.policy_number})</option>`
        ).join('');
        
        this.elements.modalBody.innerHTML = `
            <form id="payment-form">                <div class="mb-3">
                    <label for="payment_type" class="form-label">Тип платежа</label>
                    <select class="form-select" id="payment_type" required>
                        <option value="premium">Страховой взнос</option>
                        <option value="claim_payout">Страховая выплата</option>
                        <option value="refund">Возврат</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="client_id" class="form-label">Клиент</label>
                    <select class="form-select" id="client_id" required>
                        <option value="">Выберите клиента</option>
                        ${clientsOptions}
                    </select>
                </div>
                <div class="mb-3 policy-group">
                    <label for="policy_id" class="form-label">Полис</label>
                    <select class="form-select" id="policy_id">
                        <option value="">Выберите полис</option>
                        ${policiesOptions}
                    </select>
                </div>
                <div class="mb-3 claim-group d-none">
                    <label for="claim_id" class="form-label">Страховой случай</label>
                    <select class="form-select" id="claim_id">
                        <option value="">Выберите страховой случай</option>
                        ${claimsOptions}
                    </select>
                </div>
                <div class="mb-3">
                    <label for="payment_date" class="form-label">Дата платежа</label>
                    <input type="date" class="form-control" id="payment_date" required>
                </div>
                <div class="mb-3">
                    <label for="amount" class="form-label">Сумма</label>
                    <input type="number" step="0.01" class="form-control" id="amount" required>
                </div>                <div class="mb-3">
                    <label for="status" class="form-label">Статус</label>
                    <select class="form-select" id="status" required>
                        <option value="pending">В ожидании</option>
                        <option value="completed">Завершен</option>
                        <option value="failed">Ошибка</option>
                        <option value="refunded">Возврат</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">Описание</label>
                    <textarea class="form-control" id="description" rows="3"></textarea>
                </div>
                <div class="alert alert-danger d-none" id="payment-form-error"></div>
                <div class="d-flex justify-content-end">
                    <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Отмена</button>
                    <button type="submit" class="btn btn-primary">Сохранить</button>
                </div>
            </form>
        `;

        // Добавляем обработчик отправки формы
        const form = this.elements.modalBody.querySelector('#payment-form');
        form.addEventListener('submit', (e) => this.handlePaymentFormSubmit(e));

        // Добавляем обработчик изменения типа платежа
        const paymentTypeSelect = form.querySelector('#payment_type');
        paymentTypeSelect.addEventListener('change', this.handlePaymentTypeChange.bind(this));

        // Устанавливаем текущую дату
        const today = new Date();
        form.payment_date.value = today.toISOString().split('T')[0];

        this.elements.formModal.show();
    },    // Обработчик изменения типа платежа
    handlePaymentTypeChange(event) {
        const paymentType = event.target.value;
        const policyGroup = document.querySelector('.policy-group');
        const claimGroup = document.querySelector('.claim-group');
        
        if (paymentType === 'claim_payout') {
            // Для выплаты нужен страховой случай
            policyGroup.classList.add('d-none');
            claimGroup.classList.remove('d-none');
            document.getElementById('claim_id').setAttribute('required', 'required');
            document.getElementById('policy_id').removeAttribute('required');
        } else {
            // Для других типов нужен полис
            policyGroup.classList.remove('d-none');
            claimGroup.classList.add('d-none');
            document.getElementById('policy_id').setAttribute('required', 'required');
            document.getElementById('claim_id').removeAttribute('required');
        }
    },

    // Показ формы редактирования платежа
    async showEditPaymentForm(paymentId) {
        try {
            await this.loadOptionsLists();
            
            const payment = await ApiService.payments.getById(paymentId);
            this.editingPaymentId = paymentId;
            
            this.elements.modalTitle.textContent = 'Редактировать платеж';
            
            const clientsOptions = this.clientsList.map(client => 
                `<option value="${client.id}" ${payment.client_id === client.id ? 'selected' : ''}>${client.last_name} ${client.first_name}</option>`
            ).join('');
            
            const policiesOptions = this.policiesList.map(policy => 
                `<option value="${policy.id}" ${payment.policy_id === policy.id ? 'selected' : ''}>${policy.policy_number} (${policy.client_name})</option>`
            ).join('');
            
            const claimsOptions = this.claimsList.map(claim => 
                `<option value="${claim.id}" ${payment.claim_id === claim.id ? 'selected' : ''}>${claim.description.substring(0, 30)}... (${claim.policy_number})</option>`
            ).join('');
              const paymentTypes = {
                'premium': 'Страховой взнос',
                'claim_payout': 'Страховая выплата',
                'refund': 'Возврат'
            };
            
            const paymentTypeOptions = Object.entries(paymentTypes).map(([value, text]) => 
                `<option value="${value}" ${payment.payment_type === value ? 'selected' : ''}>${text}</option>`
            ).join('');
            
            const statusOptions = [
                ['pending', 'В ожидании'],
                ['completed', 'Завершен'],
                ['failed', 'Ошибка'],
                ['refunded', 'Возврат']
            ].map(([value, text]) => 
                `<option value="${value}" ${payment.status === value ? 'selected' : ''}>${text}</option>`
            ).join('');
            
            // Определяем видимость групп в зависимости от типа платежа
            const isPayout = payment.payment_type === 'claim_payout';
            
            this.elements.modalBody.innerHTML = `
                <form id="payment-form">
                    <div class="mb-3">
                        <label for="payment_type" class="form-label">Тип платежа</label>
                        <select class="form-select" id="payment_type" required>
                            ${paymentTypeOptions}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="client_id" class="form-label">Клиент</label>
                        <select class="form-select" id="client_id" required>
                            <option value="">Выберите клиента</option>
                            ${clientsOptions}
                        </select>
                    </div>
                    <div class="mb-3 policy-group ${isPayout ? 'd-none' : ''}">
                        <label for="policy_id" class="form-label">Полис</label>
                        <select class="form-select" id="policy_id" ${isPayout ? '' : 'required'}>
                            <option value="">Выберите полис</option>
                            ${policiesOptions}
                        </select>
                    </div>
                    <div class="mb-3 claim-group ${isPayout ? '' : 'd-none'}">
                        <label for="claim_id" class="form-label">Страховой случай</label>
                        <select class="form-select" id="claim_id" ${isPayout ? 'required' : ''}>
                            <option value="">Выберите страховой случай</option>
                            ${claimsOptions}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="payment_date" class="form-label">Дата платежа</label>
                        <input type="date" class="form-control" id="payment_date" value="${payment.payment_date}" required>
                    </div>
                    <div class="mb-3">
                        <label for="amount" class="form-label">Сумма</label>
                        <input type="number" step="0.01" class="form-control" id="amount" value="${payment.amount}" required>
                    </div>
                    <div class="mb-3">
                        <label for="status" class="form-label">Статус</label>
                        <select class="form-select" id="status" required>
                            ${statusOptions}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">Описание</label>
                        <textarea class="form-control" id="description" rows="3">${payment.description || ''}</textarea>
                    </div>
                    <div class="alert alert-danger d-none" id="payment-form-error"></div>
                    <div class="d-flex justify-content-end">
                        <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Отмена</button>
                        <button type="submit" class="btn btn-primary">Сохранить</button>
                    </div>
                </form>
            `;

            // Добавляем обработчик отправки формы
            const form = this.elements.modalBody.querySelector('#payment-form');
            form.addEventListener('submit', (e) => this.handlePaymentFormSubmit(e));

            // Добавляем обработчик изменения типа платежа
            const paymentTypeSelect = form.querySelector('#payment_type');
            paymentTypeSelect.addEventListener('change', this.handlePaymentTypeChange.bind(this));

            this.elements.formModal.show();
        } catch (error) {
            this.showError('Не удалось загрузить данные платежа: ' + error.message);
        }
    },    // Обработка отправки формы платежа
    async handlePaymentFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const errorElement = form.querySelector('#payment-form-error');
        
        try {
            errorElement.classList.add('d-none');
            
            const paymentType = form.payment_type.value;
            const isPayout = paymentType === 'claim_payout';
            
            const paymentData = {
                payment_type: paymentType,
                client_id: form.client_id.value,
                policy_id: isPayout ? null : form.policy_id.value,
                claim_id: isPayout ? form.claim_id.value : null,
                payment_date: form.payment_date.value,
                amount: parseFloat(form.amount.value),
                status: form.status.value,
                description: form.description.value.trim() || null
            };
            
            if (this.editingPaymentId) {
                // Обновление платежа
                await ApiService.payments.update(this.editingPaymentId, paymentData);
            } else {
                // Создание нового платежа
                await ApiService.payments.create(paymentData);
            }
            
            this.elements.formModal.hide();
            this.loadPayments(); // Перезагружаем список платежей
        } catch (error) {
            errorElement.textContent = error.message;
            errorElement.classList.remove('d-none');
        }
    },    // Обработка платежа (изменение статуса на "Завершен")
    async processPayment(paymentId) {
        try {
            const processData = {
                status: 'completed'
            };
            
            await ApiService.payments.update(paymentId, processData);
            this.loadPayments(); // Перезагружаем список платежей
        } catch (error) {
            this.showError('Не удалось обработать платеж: ' + error.message);
        }
    },

    // Подтверждение удаления платежа
    confirmDeletePayment(paymentId) {
        if (confirm('Вы уверены, что хотите удалить этот платеж?')) {
            this.deletePayment(paymentId);
        }
    },

    // Удаление платежа
    async deletePayment(paymentId) {
        try {
            await ApiService.payments.delete(paymentId);
            this.loadPayments(); // Перезагружаем список платежей
        } catch (error) {
            this.showError('Не удалось удалить платеж: ' + error.message);
        }
    },

    // Показать секцию платежей
    showPaymentsSection() {
        // Скрыть все секции
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // Показать секцию платежей
        this.elements.paymentsSection.classList.remove('d-none');
        
        // Загрузить данные, если нужно
        this.loadPayments();
    },

    // Показать ошибку
    showError(message) {
        alert(message);
    }
};
