"""
Фабрики для создания тестовых данных
"""
import factory
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from faker import Faker

from insurance_app.domain.models.client import Client
from insurance_app.domain.models.policy import Policy, PolicyStatus, PolicyType
from insurance_app.domain.models.claim import Claim, ClaimStatus
from insurance_app.domain.models.payment import Payment, PaymentStatus, PaymentType
from insurance_app.domain.models.user import User

fake = Faker('ru_RU')


class ClientFactory(factory.Factory):
    """Фабрика для создания клиентов"""
    
    class Meta:
        model = Client
    
    id = factory.LazyFunction(uuid.uuid4)
    first_name = factory.Faker('first_name', locale='ru_RU')
    last_name = factory.Faker('last_name', locale='ru_RU')
    email = factory.Faker('email', locale='ru_RU')
    phone = factory.Faker('phone_number', locale='ru_RU')
    birth_date = factory.LazyFunction(lambda: fake.date_of_birth(minimum_age=18, maximum_age=80))
    address = factory.Faker('address', locale='ru_RU')
    passport_number = factory.LazyFunction(lambda: f"{fake.random_int(min=1000, max=9999)} {fake.random_int(min=100000, max=999999)}")
    created_at = factory.LazyFunction(datetime.utcnow)
    is_active = True


class PolicyFactory(factory.Factory):
    """Фабрика для создания полисов"""
    
    class Meta:
        model = Policy
    
    id = factory.LazyFunction(uuid.uuid4)
    policy_number = factory.LazyFunction(lambda: f"POL-{fake.random_int(min=10000, max=99999)}")
    client_id = factory.LazyFunction(uuid.uuid4)
    type = factory.LazyFunction(lambda: fake.random_element(elements=list(PolicyType)))
    status = PolicyStatus.ACTIVE
    start_date = factory.LazyFunction(lambda: datetime.utcnow().date())
    end_date = factory.LazyFunction(lambda: (datetime.utcnow() + timedelta(days=365)).date())
    coverage_amount = factory.LazyFunction(lambda: Decimal(fake.random_int(min=10000, max=1000000)))
    premium_amount = factory.LazyFunction(lambda: Decimal(fake.random_int(min=1000, max=50000)))
    payment_frequency = factory.LazyFunction(lambda: fake.random_element(elements=["monthly", "quarterly", "annually"]))
    description = factory.Faker('text', max_nb_chars=200, locale='ru_RU')
    created_at = factory.LazyFunction(datetime.utcnow)
    is_active = True


class ClaimFactory(factory.Factory):
    """Фабрика для создания страховых случаев"""
    
    class Meta:
        model = Claim
    
    id = factory.LazyFunction(uuid.uuid4)
    claim_number = factory.LazyFunction(lambda: f"CLM-{fake.random_int(min=10000, max=99999)}")
    policy_id = factory.LazyFunction(uuid.uuid4)
    client_id = factory.LazyFunction(uuid.uuid4)
    incident_date = factory.LazyFunction(lambda: datetime.utcnow().date() - timedelta(days=fake.random_int(min=1, max=30)))
    report_date = factory.LazyFunction(lambda: datetime.utcnow().date())
    description = factory.Faker('text', max_nb_chars=300, locale='ru_RU')
    status = ClaimStatus.PENDING
    claim_amount = factory.LazyFunction(lambda: Decimal(fake.random_int(min=1000, max=100000)))
    approved_amount = None
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
    is_active = True


class PaymentFactory(factory.Factory):
    """Фабрика для создания платежей"""
    
    class Meta:
        model = Payment
    
    id = factory.LazyFunction(uuid.uuid4)
    payment_number = factory.LazyFunction(lambda: f"PAY-{fake.random_int(min=10000, max=99999)}")
    client_id = factory.LazyFunction(uuid.uuid4)
    policy_id = factory.LazyFunction(uuid.uuid4)
    claim_id = None
    amount = factory.LazyFunction(lambda: Decimal(fake.random_int(min=1000, max=10000)))
    payment_date = factory.LazyFunction(lambda: datetime.utcnow().date())
    due_date = factory.LazyFunction(lambda: datetime.utcnow().date() + timedelta(days=30))
    status = PaymentStatus.PENDING
    payment_type = PaymentType.PREMIUM
    payment_method = factory.LazyFunction(lambda: fake.random_element(elements=["card", "bank_transfer", "cash"]))
    description = factory.Faker('text', max_nb_chars=100, locale='ru_RU')
    created_at = factory.LazyFunction(datetime.utcnow)
    is_active = True


class UserFactory(factory.Factory):
    """Фабрика для создания пользователей"""
    
    class Meta:
        model = User
    
    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    full_name = factory.Faker('name', locale='ru_RU')
    hashed_password = "hashed_password"  # Для тестов это значение не важно
    is_active = True
    is_superuser = False
    roles = ["user"]
    created_at = factory.LazyFunction(datetime.utcnow)
