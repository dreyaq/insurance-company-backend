// Обработка функциональности страховых случаев
const ClaimsHandler = {
    // DOM элементы
    elements: {
        claimsSection: document.getElementById('claims-section'),
        claimsTableBody: document.getElementById('claims-table-body'),
        addClaimBtn: document.getElementById('add-claim-btn'),
        claimSearch: document.getElementById('claim-search'),
        claimSearchBtn: document.getElementById('claim-search-btn'),
        formModal: new bootstrap.Modal(document.getElementById('form-modal')),
        modalTitle: document.getElementById('modal-title'),
        modalBody: document.getElementById('modal-body')
    },

    // Текущие данные
    currentClaims: [],
    policiesList: [],
    editingClaimId: null,

    // Инициализация
    init() {
        // Обработчики событий
        this.elements.addClaimBtn.addEventListener('click', () => this.showAddClaimForm());
        this.elements.claimSearchBtn.addEventListener('click', () => this.searchClaims());
        this.elements.claimSearch.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.searchClaims();
        });

        // Обработчик для меню
        document.getElementById('nav-claims').addEventListener('click', (e) => {
            e.preventDefault();
            this.showClaimsSection();
        });
    },    // Загрузка списка страховых случаев
    async loadClaims() {
        try {
            const claims = await ApiService.claims.getAll();
            this.currentClaims = claims;
            
            // Загружаем данные полисов для каждого страхового случая
            await this.loadPolicyData();
            
            this.renderClaimsTable();
        } catch (error) {
            this.showError('Не удалось загрузить список страховых случаев: ' + error.message);
        }
    },
    
    // Загрузка данных полисов для страховых случаев
    async loadPolicyData() {
        try {
            const policies = await ApiService.policies.getAll(0, 1000);
            
            // Создаем словарь полисов по ID
            const policiesMap = {};
            policies.forEach(policy => {
                policiesMap[policy.id] = policy.policy_number;
            });
            
            // Добавляем номера полисов к страховым случаям
            this.currentClaims.forEach(claim => {
                if (claim.policy_id && policiesMap[claim.policy_id]) {
                    claim.policy_number = policiesMap[claim.policy_id];
                }
            });
        } catch (error) {
            console.error('Ошибка загрузки данных полисов:', error);
        }
    },    // Загрузка списка полисов для формы
    async loadPoliciesList() {
        try {
            const policies = await ApiService.policies.getAll(0, 1000);
            
            // Загрузим имена клиентов для всех полисов
            const clients = await ApiService.clients.getAll('', 0, 1000);
            const clientsMap = {};
            clients.forEach(client => {
                clientsMap[client.id] = `${client.last_name} ${client.first_name}`;
            });
            
            // Добавим имена клиентов к полисам
            policies.forEach(policy => {
                if (policy.client_id && clientsMap[policy.client_id]) {
                    policy.client_name = clientsMap[policy.client_id];
                } else {
                    policy.client_name = 'Неизвестный клиент';
                }
            });
            
            this.policiesList = policies;
        } catch (error) {
            console.error('Ошибка загрузки полисов:', error);
            this.policiesList = [];
        }
    },

    // Отображение таблицы страховых случаев
    renderClaimsTable() {
        const tbody = this.elements.claimsTableBody;
        tbody.innerHTML = '';

        if (this.currentClaims.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = '<td colspan="7" class="text-center">Нет данных</td>';
            tbody.appendChild(tr);
            return;
        }        this.currentClaims.forEach(claim => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${claim.id.substring(0, 8)}...</td>
                <td>${claim.incident_date}</td>
                <td>${claim.description}</td>
                <td>${claim.policy_number || 'Загрузка...'}</td>
                <td>${claim.claim_amount}</td>
                <td>${this.getClaimStatusBadge(claim.status)}</td>
                <td>
                    <button class="btn btn-sm btn-primary edit-claim" data-id="${claim.id}">
                        <i class="bi bi-pencil"></i> Изменить
                    </button>
                    <button class="btn btn-sm btn-danger delete-claim" data-id="${claim.id}">
                        <i class="bi bi-trash"></i> Удалить
                    </button>
                </td>
            `;
            tbody.appendChild(tr);

            // Добавляем обработчики для кнопок
            const editBtn = tr.querySelector('.edit-claim');
            const deleteBtn = tr.querySelector('.delete-claim');

            editBtn.addEventListener('click', () => this.showEditClaimForm(claim.id));
            deleteBtn.addEventListener('click', () => this.confirmDeleteClaim(claim.id));
        });
    },    // Получение HTML-кода для отображения статуса страхового случая
    getClaimStatusBadge(status) {
        const statusMap = {
            'pending': '<span class="badge bg-primary">Новый</span>',
            'under_review': '<span class="badge bg-info">В обработке</span>',
            'approved': '<span class="badge bg-success">Утвержден</span>',
            'denied': '<span class="badge bg-danger">Отклонен</span>',
            'paid': '<span class="badge bg-warning text-dark">Оплачен</span>',
            'closed': '<span class="badge bg-secondary">Закрыт</span>'
        };
        
        return statusMap[status] || `<span class="badge bg-secondary">${status}</span>`;
    },

    // Поиск страховых случаев
    searchClaims() {
        const searchText = this.elements.claimSearch.value.trim();
        // В API нет поиска по ID страхового случая, поэтому фильтруем локально
        if (searchText) {
            const filteredClaims = this.currentClaims.filter(claim => 
                claim.id.toLowerCase().includes(searchText.toLowerCase()) ||
                (claim.description && claim.description.toLowerCase().includes(searchText.toLowerCase()))
            );
            this.currentClaims = filteredClaims;
            this.renderClaimsTable();
        } else {
            this.loadClaims();
        }
    },

    // Показ формы добавления страхового случая
    async showAddClaimForm() {
        await this.loadPoliciesList();
        
        this.editingClaimId = null;
        this.elements.modalTitle.textContent = 'Добавить страховой случай';
        
        const policiesOptions = this.policiesList.map(policy => 
            `<option value="${policy.id}">${policy.policy_number} (${policy.client_name})</option>`
        ).join('');
        
        this.elements.modalBody.innerHTML = `
            <form id="claim-form">
                <div class="mb-3">
                    <label for="policy_id" class="form-label">Полис</label>
                    <select class="form-select" id="policy_id" required>
                        <option value="">Выберите полис</option>
                        ${policiesOptions}
                    </select>
                </div>
                <div class="mb-3">
                    <label for="incident_date" class="form-label">Дата происшествия</label>
                    <input type="date" class="form-control" id="incident_date" required>
                </div>
                <div class="mb-3">
                    <label for="report_date" class="form-label">Дата обращения</label>
                    <input type="date" class="form-control" id="report_date" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">Описание</label>
                    <textarea class="form-control" id="description" rows="3" required></textarea>
                </div>
                <div class="mb-3">
                    <label for="claim_amount" class="form-label">Сумма возмещения</label>
                    <input type="number" step="0.01" class="form-control" id="claim_amount" required>
                </div>                <div class="mb-3">
                    <label for="status" class="form-label">Статус</label>
                    <select class="form-select" id="status" required>
                        <option value="pending">Новый</option>
                        <option value="under_review">В обработке</option>
                        <option value="approved">Утвержден</option>
                        <option value="denied">Отклонен</option>
                    </select>
                </div>
                <div class="alert alert-danger d-none" id="claim-form-error"></div>
                <div class="d-flex justify-content-end">
                    <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Отмена</button>
                    <button type="submit" class="btn btn-primary">Сохранить</button>
                </div>
            </form>
        `;

        // Добавляем обработчик отправки формы
        const form = this.elements.modalBody.querySelector('#claim-form');
        form.addEventListener('submit', (e) => this.handleClaimFormSubmit(e));

        // Устанавливаем текущую дату
        const today = new Date();
        form.incident_date.value = today.toISOString().split('T')[0];
        form.report_date.value = today.toISOString().split('T')[0];

        this.elements.formModal.show();
    },

    // Показ формы редактирования страхового случая
    async showEditClaimForm(claimId) {
        try {
            await this.loadPoliciesList();
            
            const claim = await ApiService.claims.getById(claimId);
            this.editingClaimId = claimId;
            
            this.elements.modalTitle.textContent = 'Редактировать страховой случай';
            
            const policiesOptions = this.policiesList.map(policy => 
                `<option value="${policy.id}" ${claim.policy_id === policy.id ? 'selected' : ''}>${policy.policy_number} (${policy.client_name})</option>`
            ).join('');
              const statusOptions = [
                ['pending', 'Новый'],
                ['under_review', 'В обработке'],
                ['approved', 'Утвержден'],
                ['denied', 'Отклонен'],
                ['paid', 'Оплачен'],
                ['closed', 'Закрыт']
            ].map(([value, text]) => 
                `<option value="${value}" ${claim.status === value ? 'selected' : ''}>${text}</option>`
            ).join('');
            
            this.elements.modalBody.innerHTML = `
                <form id="claim-form">
                    <div class="mb-3">
                        <label for="policy_id" class="form-label">Полис</label>
                        <select class="form-select" id="policy_id" required>
                            <option value="">Выберите полис</option>
                            ${policiesOptions}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="incident_date" class="form-label">Дата происшествия</label>
                        <input type="date" class="form-control" id="incident_date" value="${claim.incident_date}" required>
                    </div>
                    <div class="mb-3">
                        <label for="report_date" class="form-label">Дата обращения</label>
                        <input type="date" class="form-control" id="report_date" value="${claim.report_date}" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">Описание</label>
                        <textarea class="form-control" id="description" rows="3" required>${claim.description}</textarea>
                    </div>
                    <div class="mb-3">
                        <label for="claim_amount" class="form-label">Сумма возмещения</label>
                        <input type="number" step="0.01" class="form-control" id="claim_amount" value="${claim.claim_amount}" required>
                    </div>
                    <div class="mb-3">
                        <label for="status" class="form-label">Статус</label>
                        <select class="form-select" id="status" required>
                            ${statusOptions}
                        </select>
                    </div>
                    <div class="alert alert-danger d-none" id="claim-form-error"></div>
                    <div class="d-flex justify-content-end">
                        <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Отмена</button>
                        <button type="submit" class="btn btn-primary">Сохранить</button>
                    </div>
                </form>
            `;

            // Добавляем обработчик отправки формы
            const form = this.elements.modalBody.querySelector('#claim-form');
            form.addEventListener('submit', (e) => this.handleClaimFormSubmit(e));

            this.elements.formModal.show();
        } catch (error) {
            this.showError('Не удалось загрузить данные страхового случая: ' + error.message);
        }
    },    // Обработка отправки формы страхового случая
    async handleClaimFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const errorElement = form.querySelector('#claim-form-error');
        
        try {            
            errorElement.classList.add('d-none');
              
            // Получаем выбранный полис
            const policyId = form.policy_id.value;
            let clientId = null;
            
            // Ищем клиента для выбранного полиса
            if (policyId) {
                const selectedPolicy = this.policiesList.find(policy => policy.id === policyId);
                if (selectedPolicy) {
                    clientId = selectedPolicy.client_id;
                }
            }
            
            const claimData = {
                policy_id: policyId,
                client_id: clientId,
                incident_date: form.incident_date.value,
                report_date: form.report_date.value,
                description: form.description.value.trim(),
                claim_amount: parseFloat(form.claim_amount.value),
                status: form.status.value
            };
            
            if (this.editingClaimId) {
                // Обновление страхового случая
                await ApiService.claims.update(this.editingClaimId, claimData);
            } else {
                // Создание нового страхового случая
                await ApiService.claims.create(claimData);
            }
            
            this.elements.formModal.hide();
            this.loadClaims(); // Перезагружаем список страховых случаев
        } catch (error) {
            errorElement.textContent = error.message;
            errorElement.classList.remove('d-none');
        }
    },

    // Подтверждение удаления страхового случая
    confirmDeleteClaim(claimId) {
        if (confirm('Вы уверены, что хотите удалить этот страховой случай?')) {
            this.deleteClaim(claimId);
        }
    },

    // Удаление страхового случая
    async deleteClaim(claimId) {
        try {
            await ApiService.claims.delete(claimId);
            this.loadClaims(); // Перезагружаем список страховых случаев
        } catch (error) {
            this.showError('Не удалось удалить страховой случай: ' + error.message);
        }
    },

    // Показать секцию страховых случаев
    showClaimsSection() {
        // Скрыть все секции
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('d-none');
        });
        
        // Показать секцию страховых случаев
        this.elements.claimsSection.classList.remove('d-none');
        
        // Загрузить данные, если нужно
        this.loadClaims();
    },

    // Показать ошибку
    showError(message) {
        alert(message);
    }
};
