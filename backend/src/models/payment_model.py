from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()

class PaymentModel(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    payment_method_id = Column(Integer, ForeignKey('payment_methods.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_refunded = Column(Boolean, default=False)
    refund_amount = Column(Float, default=0.0)

    user = relationship('UserModel', back_populates='payments')
    payment_method = relationship('PaymentMethodModel', back_populates='payments')

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, currency={self.currency}, status={self.status})>"

    def process_payment(self):
        if self.status != 'pending':
            raise ValueError('Payment is already processed or canceled.')
        if self.external_payment_gateway():
            self.status = 'completed'
            self.updated_at = datetime.utcnow()
        else:
            self.status = 'failed'
            self.updated_at = datetime.utcnow()

    def external_payment_gateway(self):
        return True

    def refund(self, amount=None):
        if self.status != 'completed':
            raise ValueError('Only completed payments can be refunded.')
        if self.is_refunded:
            raise ValueError('Payment is already refunded.')
        if amount is None:
            amount = self.amount
        if amount > self.amount:
            raise ValueError('Refund amount exceeds the original payment amount.')
        self.refund_amount = amount
        self.is_refunded = True
        self.status = 'refunded'
        self.updated_at = datetime.utcnow()

class PaymentMethodModel(Base):
    __tablename__ = 'payment_methods'

    id = Column(Integer, primary_key=True, autoincrement=True)
    method_type = Column(String(50), nullable=False)
    card_number = Column(String(16), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    payments = relationship('PaymentModel', back_populates='payment_method')

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, method_type={self.method_type})>"

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    payments = relationship('PaymentModel', back_populates='user')
    payment_methods = relationship('PaymentMethodModel', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

class PaymentSchema:
    def validate_payment_data(self, data):
        required_fields = ['amount', 'currency', 'user_id', 'payment_method_id']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        if not isinstance(data['amount'], (int, float)) or data['amount'] <= 0:
            raise ValueError("Invalid payment amount")
        if len(data['currency']) != 3:
            raise ValueError("Invalid currency format. Must be 3-letter ISO code.")
        return True

    def to_dict(self, payment):
        return {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "created_at": payment.created_at.isoformat(),
            "updated_at": payment.updated_at.isoformat() if payment.updated_at else None,
            "is_refunded": payment.is_refunded,
            "refund_amount": payment.refund_amount
        }

    def from_dict(self, data, payment=None):
        if payment is None:
            payment = PaymentModel()
        payment.amount = data['amount']
        payment.currency = data['currency']
        payment.user_id = data['user_id']
        payment.payment_method_id = data['payment_method_id']
        return payment

def get_payment_by_id(session: Session, payment_id: int) -> PaymentModel:
    payment = session.query(PaymentModel).filter_by(id=payment_id).first()
    if not payment:
        raise ValueError(f"No payment found with ID: {payment_id}")
    return payment

def create_payment(session: Session, data: dict) -> PaymentModel:
    schema = PaymentSchema()
    schema.validate_payment_data(data)
    new_payment = schema.from_dict(data)
    session.add(new_payment)
    session.commit()
    return new_payment

def update_payment_status(session: Session, payment_id: int, new_status: str) -> PaymentModel:
    payment = get_payment_by_id(session, payment_id)
    payment.status = new_status
    payment.updated_at = datetime.utcnow()
    session.commit()
    return payment

def process_refund(session: Session, payment_id: int, refund_amount: float = None) -> PaymentModel:
    payment = get_payment_by_id(session, payment_id)
    payment.refund(refund_amount)
    session.commit()
    return payment

def list_user_payments(session: Session, user_id: int) -> list:
    return session.query(PaymentModel).filter_by(user_id=user_id).all()

def list_all_payments(session: Session) -> list:
    return session.query(PaymentModel).all()

def delete_payment(session: Session, payment_id: int) -> None:
    payment = get_payment_by_id(session, payment_id)
    session.delete(payment)
    session.commit()

def update_payment_method(session: Session, payment_id: int, new_payment_method_id: int) -> PaymentModel:
    payment = get_payment_by_id(session, payment_id)
    payment.payment_method_id = new_payment_method_id
    payment.updated_at = datetime.utcnow()
    session.commit()
    return payment

def total_user_spent(session: Session, user_id: int) -> float:
    total = session.query(PaymentModel).filter_by(user_id=user_id).with_entities(func.sum(PaymentModel.amount)).scalar()
    return total if total else 0.0

def get_payments_by_status(session: Session, status: str) -> list:
    return session.query(PaymentModel).filter_by(status=status).all()

def get_refunded_payments(session: Session) -> list:
    return session.query(PaymentModel).filter_by(is_refunded=True).all()

def update_payment_amount(session: Session, payment_id: int, new_amount: float) -> PaymentModel:
    payment = get_payment_by_id(session, payment_id)
    if payment.status != 'pending':
        raise ValueError('Cannot update the amount of a processed or completed payment.')
    payment.amount = new_amount
    payment.updated_at = datetime.utcnow()
    session.commit()
    return payment