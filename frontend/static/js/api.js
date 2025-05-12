// API сервис для работы с бэкендом
const API_URL = 'http://localhost:8000/api';

const ApiService = {
    // Токен авторизации
    token: null,

    // Установка токена
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    },

    // Получение токена из localStorage при загрузке
    loadToken() {
        const token = localStorage.getItem('token');
        if (token) {
            this.token = token;
            return true;
        }
        return false;
    },

    // Удаление токена
    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    },    // Общий метод для запросов
    async request(endpoint, method = 'GET', data = null) {
        const url = `${API_URL}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const options = {
            method,
            headers
        };
        
        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            
            // Если ответ 401, значит токен истек или недействителен
            if (response.status === 401) {
                this.clearToken();
                // Перенаправляем на страницу входа
                window.dispatchEvent(new CustomEvent('auth:logout'));
                throw new Error('Необходима авторизация');
            }
            
            // Для методов, которые не возвращают контент
            if (response.status === 204) {
                return true;
            }
            
            // Пытаемся получить JSON из ответа
            let responseData;
            try {
                responseData = await response.json();
            } catch (e) {
                // Если невозможно получить JSON, используем текст ответа
                const text = await response.text();
                responseData = { detail: text || 'Ошибка в ответе сервера' };
            }
            
            // Если ответ не успешный, выбрасываем ошибку с деталями
            if (!response.ok) {
                let errorMessage = 'Ошибка запроса';
                
                // Если есть детали ошибки, используем их
                if (responseData.detail) {
                    errorMessage = responseData.detail;
                }
                
                throw new Error(errorMessage);
            }
            
            return responseData;
        } catch (error) {
            console.error('API error:', error);
            throw error;
        }
    },    // Методы авторизации
    auth: {
        // Вход
        async login(username, password) {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            try {
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: formData
                });
                
                // Проверка статуса ответа
                if (!response.ok) {
                    let errorMessage = 'Ошибка авторизации';
                    
                    try {
                        const errorData = await response.json();
                        if (errorData.detail) {
                            errorMessage = errorData.detail;
                        }
                    } catch (e) {
                        // Если JSON не удалось прочитать, используем текст ответа
                        const text = await response.text();
                        errorMessage = text || 'Неверное имя пользователя или пароль';
                    }
                    
                    throw new Error(errorMessage);
                }
                
                return await response.json();
            } catch (error) {
                console.error('API login error:', error);
                throw error;
            }
        },
          // Регистрация
        async register(userData) {
            try {
                return await ApiService.request('/auth/register', 'POST', userData);
            } catch (error) {
                console.error('API register error:', error);
                throw error;
            }
        }
    },

    // Методы для работы с клиентами
    clients: {
        // Получение списка клиентов
        getAll(name = '', skip = 0, limit = 100) {
            return ApiService.request(`/clients?skip=${skip}&limit=${limit}${name ? `&name=${name}` : ''}`);
        },
        
        // Получение клиента по ID
        getById(clientId) {
            return ApiService.request(`/clients/${clientId}`);
        },
        
        // Создание клиента
        create(clientData) {
            return ApiService.request('/clients', 'POST', clientData);
        },
        
        // Обновление клиента
        update(clientId, clientData) {
            return ApiService.request(`/clients/${clientId}`, 'PUT', clientData);
        },
        
        // Удаление клиента
        delete(clientId) {
            return ApiService.request(`/clients/${clientId}`, 'DELETE');
        }
    },

    // Методы для работы с полисами
    policies: {
        // Получение списка полисов
        getAll(skip = 0, limit = 100, clientId = null) {
            let url = `/policies?skip=${skip}&limit=${limit}`;
            if (clientId) {
                url += `&client_id=${clientId}`;
            }
            return ApiService.request(url);
        },
        
        // Получение полиса по ID
        getById(policyId) {
            return ApiService.request(`/policies/${policyId}`);
        },
        
        // Создание полиса
        create(policyData) {
            return ApiService.request('/policies', 'POST', policyData);
        },
        
        // Обновление полиса
        update(policyId, policyData) {
            return ApiService.request(`/policies/${policyId}`, 'PUT', policyData);
        },
        
        // Удаление полиса
        delete(policyId) {
            return ApiService.request(`/policies/${policyId}`, 'DELETE');
        }
    },

    // Методы для работы со страховыми случаями
    claims: {
        // Получение списка страховых случаев
        getAll(skip = 0, limit = 100, policyId = null) {
            let url = `/claims?skip=${skip}&limit=${limit}`;
            if (policyId) {
                url += `&policy_id=${policyId}`;
            }
            return ApiService.request(url);
        },
        
        // Получение страхового случая по ID
        getById(claimId) {
            return ApiService.request(`/claims/${claimId}`);
        },
        
        // Создание страхового случая
        create(claimData) {
            return ApiService.request('/claims', 'POST', claimData);
        },
        
        // Обновление страхового случая
        update(claimId, claimData) {
            return ApiService.request(`/claims/${claimId}`, 'PUT', claimData);
        },
        
        // Удаление страхового случая
        delete(claimId) {
            return ApiService.request(`/claims/${claimId}`, 'DELETE');
        }
    },

    // Методы для работы с платежами
    payments: {
        // Получение списка платежей
        getAll(skip = 0, limit = 100, clientId = null, policyId = null, claimId = null) {
            let url = `/payments?skip=${skip}&limit=${limit}`;
            if (clientId) {
                url += `&client_id=${clientId}`;
            }
            if (policyId) {
                url += `&policy_id=${policyId}`;
            }
            if (claimId) {
                url += `&claim_id=${claimId}`;
            }
            return ApiService.request(url);
        },
        
        // Получение платежа по ID
        getById(paymentId) {
            return ApiService.request(`/payments/${paymentId}`);
        },
        
        // Создание платежа
        create(paymentData) {
            return ApiService.request('/payments', 'POST', paymentData);
        },
        
        // Обновление платежа
        update(paymentId, paymentData) {
            return ApiService.request(`/payments/${paymentId}`, 'PUT', paymentData);
        },
        
        // Удаление платежа
        delete(paymentId) {
            return ApiService.request(`/payments/${paymentId}`, 'DELETE');
        }
    }
};
