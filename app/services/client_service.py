from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


def _get_client(db: Session, company_id: int, client_id: int) -> Client:
    row = db.get(Client, client_id)
    if row is None or row.company_id != company_id:
        raise NotFoundError("Client not found.")
    return row


def create_client(db: Session, company_id: int, payload: ClientCreate) -> Client:
    email_val = str(payload.email).lower().strip() if payload.email is not None else None
    row = Client(
        company_id=company_id,
        code=payload.code.strip(),
        name=payload.name.strip(),
        contact_person=payload.contact_person.strip() if payload.contact_person else None,
        phone=payload.phone.strip() if payload.phone else None,
        email=email_val,
        address=payload.address,
        notes=payload.notes,
        is_active=payload.is_active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Client code already exists for this company.") from None
    db.refresh(row)
    return row


def list_clients(
    db: Session,
    *,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    is_active: bool | None = None,
) -> list[Client]:
    stmt = select(Client).where(Client.company_id == company_id)
    if is_active is not None:
        stmt = stmt.where(Client.is_active == is_active)
    if search and (t := search.strip()):
        term = f"%{t}%"
        stmt = stmt.where(
            or_(
                Client.code.ilike(term),
                Client.name.ilike(term),
                Client.phone.ilike(term),
            )
        )
    stmt = stmt.order_by(Client.id).offset(skip).limit(min(limit, 500))
    return list(db.scalars(stmt).all())


def get_client(db: Session, company_id: int, client_id: int) -> Client:
    return _get_client(db, company_id, client_id)


def update_client(db: Session, company_id: int, client_id: int, payload: ClientUpdate) -> Client:
    row = _get_client(db, company_id, client_id)
    email_val = str(payload.email).lower().strip() if payload.email is not None else None
    row.code = payload.code.strip()
    row.name = payload.name.strip()
    row.contact_person = payload.contact_person.strip() if payload.contact_person else None
    row.phone = payload.phone.strip() if payload.phone else None
    row.email = email_val
    row.address = payload.address
    row.notes = payload.notes
    row.is_active = payload.is_active
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Client code already exists for this company.") from None
    db.refresh(row)
    return row


def deactivate_client(db: Session, company_id: int, client_id: int) -> Client:
    row = _get_client(db, company_id, client_id)
    row.is_active = False
    db.commit()
    db.refresh(row)
    return row
