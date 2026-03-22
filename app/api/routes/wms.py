"""WMS callback-style routes: tenant from JWT (use a dedicated integration user per tenant in production)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.user import User
from app.schemas.sales_order import SalesOrderFulfillmentUpdate, SalesOrderResponse, sales_order_to_response
from app.services import integration_service

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/callback/sales-orders/{order_id}", response_model=SalesOrderResponse)
def wms_callback_sales_order_fulfillment(
    order_id: int,
    payload: SalesOrderFulfillmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SalesOrderResponse:
    try:
        row = integration_service.apply_wms_fulfillment_update(
            db, current_user.company_id, order_id, payload
        )
    except NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=e.detail) from e
    except BusinessRuleError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=e.detail) from e
    return sales_order_to_response(row)
