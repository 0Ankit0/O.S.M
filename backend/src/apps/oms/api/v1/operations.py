from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from src.apps.iam.api.deps import get_current_active_superuser, get_current_user, get_db
from src.apps.iam.models.user import User
from src.apps.oms.constants import DeliveryAssignmentStatus, FulfillmentTaskStatus, OrderStatus, ReturnStatus
from src.apps.oms.models import (
    DeliveryAssignment,
    FulfillmentTask,
    InventoryItem,
    Order,
    ReturnRequest,
)
from src.apps.oms.schemas import (
    AdminOverviewRead,
    DeliveryFailureRequest,
    DeliveryStatusUpdateRequest,
    DeliveryZoneCreate,
    DeliveryZoneRead,
    FulfillmentPackRequest,
    FulfillmentScanRequest,
    FulfillmentTaskRead,
    InventoryItemRead,
    PodSubmitRequest,
    ReturnRequestCreate,
    ReturnRequestRead,
    ReturnReviewRequest,
    WarehouseCreate,
    WarehouseRead,
)
from src.apps.oms.models import DeliveryZone, Product, Warehouse
from src.apps.oms.service import (
    create_or_update_pod,
    map_assignment_status_to_order_status,
    release_inventory_reservations,
    record_order_milestone,
    require_transition,
    utcnow,
)

router = APIRouter()


@router.get("/admin/overview", response_model=AdminOverviewRead)
async def get_admin_overview(
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> AdminOverviewRead:
    del current_user
    orders = (await session.execute(select(Order))).scalars().all()
    fulfillment_tasks = (await session.execute(select(FulfillmentTask))).scalars().all()
    delivery_assignments = (await session.execute(select(DeliveryAssignment))).scalars().all()
    return_requests = (await session.execute(select(ReturnRequest))).scalars().all()
    inventory_items = (await session.execute(select(InventoryItem))).scalars().all()
    products = (await session.execute(select(Product))).scalars().all()
    zones = (await session.execute(select(DeliveryZone))).scalars().all()
    return AdminOverviewRead(
        total_orders=len(orders),
        active_orders=sum(1 for order in orders if order.status not in {OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.REFUNDED}),
        delivered_orders=sum(1 for order in orders if order.status == OrderStatus.DELIVERED),
        cancelled_orders=sum(1 for order in orders if order.status == OrderStatus.CANCELLED),
        return_requests=len(return_requests),
        low_stock_items=sum(1 for item in inventory_items if item.quantity_on_hand <= item.low_stock_threshold),
        active_fulfillment_tasks=sum(1 for task in fulfillment_tasks if task.status in {FulfillmentTaskStatus.PENDING, FulfillmentTaskStatus.IN_PROGRESS, FulfillmentTaskStatus.PICKED}),
        active_delivery_assignments=sum(1 for assignment in delivery_assignments if assignment.status in {DeliveryAssignmentStatus.ASSIGNED, DeliveryAssignmentStatus.PICKED_UP, DeliveryAssignmentStatus.OUT_FOR_DELIVERY, DeliveryAssignmentStatus.FAILED}),
        featured_products=sum(1 for product in products if product.is_featured),
        top_category_names=[zone.name for zone in zones[:3]],
    )


@router.post("/warehouses", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> Warehouse:
    del current_user
    warehouse = Warehouse(**payload.model_dump())
    session.add(warehouse)
    await session.commit()
    await session.refresh(warehouse)
    return warehouse


@router.get("/warehouses", response_model=list[WarehouseRead])
async def list_warehouses(
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> list[Warehouse]:
    del current_user
    result = await session.execute(select(Warehouse).order_by(col(Warehouse.id).desc()))
    return result.scalars().all()


@router.post("/delivery-zones", response_model=DeliveryZoneRead, status_code=status.HTTP_201_CREATED)
async def create_delivery_zone(
    payload: DeliveryZoneCreate,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> DeliveryZone:
    del current_user
    zone = DeliveryZone(**payload.model_dump())
    session.add(zone)
    await session.commit()
    await session.refresh(zone)
    return zone


@router.get("/delivery-zones", response_model=list[DeliveryZoneRead])
async def list_delivery_zones(
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> list[DeliveryZone]:
    del current_user
    result = await session.execute(select(DeliveryZone).order_by(col(DeliveryZone.id).desc()))
    return result.scalars().all()


@router.get("/inventory", response_model=list[InventoryItemRead])
async def list_inventory_items(
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> list[InventoryItem]:
    del current_user
    result = await session.execute(select(InventoryItem).order_by(col(InventoryItem.id).desc()))
    return result.scalars().all()


@router.get("/fulfillment/tasks", response_model=list[FulfillmentTaskRead])
async def list_fulfillment_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[FulfillmentTask]:
    result = await session.execute(select(FulfillmentTask).order_by(FulfillmentTask.id.desc()))
    return result.scalars().all()


@router.post("/fulfillment/tasks/{task_id}/start", response_model=FulfillmentTaskRead)
async def start_fulfillment_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> FulfillmentTask:
    task = await session.get(FulfillmentTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.assigned_user_id = current_user.id
    task.status = FulfillmentTaskStatus.IN_PROGRESS
    await session.commit()
    await session.refresh(task)
    return task


@router.post("/fulfillment/tasks/{task_id}/scan", response_model=FulfillmentTaskRead)
async def scan_fulfillment_item(
    task_id: int,
    payload: FulfillmentScanRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> FulfillmentTask:
    task = await session.get(FulfillmentTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.assigned_user_id = current_user.id
    task.scan_log = [*(task.scan_log or []), {"sku": payload.sku, "quantity": payload.quantity, "scanned_at": utcnow().isoformat()}]
    task.status = FulfillmentTaskStatus.PICKED
    await session.commit()
    await session.refresh(task)
    return task


@router.post("/fulfillment/tasks/{task_id}/pack", response_model=FulfillmentTaskRead)
async def pack_fulfillment_task(
    task_id: int,
    payload: FulfillmentPackRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> FulfillmentTask:
    task = await session.get(FulfillmentTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.assigned_user_id = current_user.id
    task.package_dimensions = {
        "length_cm": payload.length_cm,
        "width_cm": payload.width_cm,
        "height_cm": payload.height_cm,
    }
    task.package_weight_grams = payload.weight_grams
    task.status = FulfillmentTaskStatus.READY
    order = await session.get(Order, task.order_id)
    if order and order.status == OrderStatus.CONFIRMED:
        require_transition(order.status, OrderStatus.READY_FOR_DISPATCH)
        order.status = OrderStatus.READY_FOR_DISPATCH
        await record_order_milestone(
            session,
            order_id=order.id,
            status_value=OrderStatus.READY_FOR_DISPATCH,
            actor_user_id=current_user.id,
            actor_role="warehouse_staff",
            notes="Packing complete",
        )
    await session.commit()
    await session.refresh(task)
    return task


@router.patch("/fulfillment/tasks/{task_id}/assign/{user_id}", response_model=FulfillmentTaskRead)
async def assign_fulfillment_task(
    task_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> FulfillmentTask:
    del current_user
    task = await session.get(FulfillmentTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.assigned_user_id = user_id
    await session.commit()
    await session.refresh(task)
    return task


@router.get("/deliveries/assignments", response_model=list[DeliveryAssignment])
async def list_delivery_assignments(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[DeliveryAssignment]:
    result = await session.execute(select(DeliveryAssignment).order_by(DeliveryAssignment.id.desc()))
    return result.scalars().all()


@router.patch("/deliveries/assignments/{assignment_id}/status", response_model=DeliveryAssignment)
async def update_delivery_status(
    assignment_id: int,
    payload: DeliveryStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DeliveryAssignment:
    assignment = await session.get(DeliveryAssignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if payload.status == DeliveryAssignmentStatus.ASSIGNED:
        raise HTTPException(status_code=409, detail="Assignment status must advance")
    assignment.staff_user_id = current_user.id
    assignment.status = payload.status
    order = await session.get(Order, assignment.order_id)
    if order:
        next_order_status = map_assignment_status_to_order_status(payload.status)
        require_transition(order.status, next_order_status)
        order.status = next_order_status
        if next_order_status == OrderStatus.DELIVERED:
            order.delivered_at = utcnow()
        await record_order_milestone(
            session,
            order_id=order.id,
            status_value=next_order_status,
            actor_user_id=current_user.id,
            actor_role="delivery_staff",
            notes=payload.notes,
        )
    await session.commit()
    await session.refresh(assignment)
    return assignment


@router.post("/deliveries/assignments/{assignment_id}/pod", response_model=DeliveryAssignment)
async def submit_pod(
    assignment_id: int,
    payload: PodSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DeliveryAssignment:
    assignment = await session.get(DeliveryAssignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await create_or_update_pod(
        session,
        order_id=assignment.order_id,
        staff_user_id=current_user.id,
        signature_path=payload.signature_path,
        photo_paths=payload.photo_paths,
        notes=payload.notes,
    )
    assignment.staff_user_id = current_user.id
    await session.commit()
    await session.refresh(assignment)
    return assignment


@router.post("/deliveries/assignments/{assignment_id}/fail", response_model=DeliveryAssignment)
async def record_delivery_failure(
    assignment_id: int,
    payload: DeliveryFailureRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DeliveryAssignment:
    assignment = await session.get(DeliveryAssignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.staff_user_id = current_user.id
    assignment.attempt_count += 1
    assignment.failure_reasons = [*(assignment.failure_reasons or []), payload.reason]
    assignment.status = (
        DeliveryAssignmentStatus.RETURNED
        if assignment.attempt_count >= 3
        else DeliveryAssignmentStatus.FAILED
    )
    order = await session.get(Order, assignment.order_id)
    if order:
        next_status = (
            OrderStatus.RETURNED_TO_WAREHOUSE
            if assignment.attempt_count >= 3
            else OrderStatus.DELIVERY_FAILED
        )
        require_transition(order.status, next_status)
        order.status = next_status
        await record_order_milestone(
            session,
            order_id=order.id,
            status_value=next_status,
            actor_user_id=current_user.id,
            actor_role="delivery_staff",
            notes=payload.reason,
        )
        if next_status == OrderStatus.RETURNED_TO_WAREHOUSE:
            await release_inventory_reservations(
                session,
                order_id=order.id,
                next_status=ReservationStatus.RELEASED,
            )
    await session.commit()
    await session.refresh(assignment)
    return assignment


@router.patch("/deliveries/assignments/{assignment_id}/reassign/{user_id}", response_model=DeliveryAssignment)
async def reassign_delivery_assignment(
    assignment_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> DeliveryAssignment:
    del current_user
    assignment = await session.get(DeliveryAssignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.staff_user_id = user_id
    await session.commit()
    await session.refresh(assignment)
    return assignment


@router.post("/returns/{order_id}", response_model=ReturnRequestRead, status_code=status.HTTP_201_CREATED)
async def request_return(
    order_id: int,
    payload: ReturnRequestCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> ReturnRequest:
    order = await session.get(Order, order_id)
    if order is None or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(status_code=409, detail="Only delivered orders can be returned")
    existing = (
        await session.execute(select(ReturnRequest).where(ReturnRequest.order_id == order.id))
    ).scalars().first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Return already requested for this order")
    return_request = ReturnRequest(
        order_id=order.id,
        user_id=current_user.id,
        reason_code=payload.reason_code,
        evidence_paths=payload.evidence_paths,
        status=ReturnStatus.REQUESTED,
        refund_amount=order.total_amount,
    )
    session.add(return_request)
    require_transition(order.status, OrderStatus.RETURN_REQUESTED)
    order.status = OrderStatus.RETURN_REQUESTED
    await record_order_milestone(
        session,
        order_id=order.id,
        status_value=OrderStatus.RETURN_REQUESTED,
        actor_user_id=current_user.id,
        actor_role="customer",
        notes=payload.reason_code,
    )
    await session.commit()
    await session.refresh(return_request)
    return return_request


@router.get("/returns", response_model=list[ReturnRequestRead])
async def list_returns(
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> list[ReturnRequest]:
    del current_user
    result = await session.execute(select(ReturnRequest).order_by(col(ReturnRequest.id).desc()))
    return result.scalars().all()


@router.patch("/returns/{return_id}/review", response_model=ReturnRequestRead)
async def review_return(
    return_id: int,
    payload: ReturnReviewRequest,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> ReturnRequest:
    return_request = await session.get(ReturnRequest, return_id)
    if return_request is None:
        raise HTTPException(status_code=404, detail="Return request not found")
    return_request.status = payload.status
    return_request.inspection_result = payload.inspection_result
    return_request.refund_amount = payload.refund_amount
    return_request.inspected_by_user_id = current_user.id
    return_request.resolved_at = utcnow()
    order = await session.get(Order, return_request.order_id)
    if order is not None and payload.status == ReturnStatus.REFUNDED:
        order.status = OrderStatus.REFUNDED
        await record_order_milestone(
            session,
            order_id=order.id,
            status_value=OrderStatus.REFUNDED,
            actor_user_id=current_user.id,
            actor_role="superadmin",
            notes=payload.inspection_result or "Return refunded",
        )
    await session.commit()
    await session.refresh(return_request)
    return return_request
