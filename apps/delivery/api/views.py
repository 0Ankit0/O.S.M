from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery.models import DeliveryAssignment
from delivery.services import DeliveryServiceabilityService, DeliveryTransitionService

from .serializers import AssignmentStatusUpdateSerializer, DeliveryTimelineSerializer, ServiceabilitySerializer


class ServiceabilityCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Check delivery serviceability", responses={200: ServiceabilitySerializer})
    def get(self, request):
        serializer = ServiceabilitySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        postcode = serializer.validated_data["postcode"]
        is_serviceable, zone = DeliveryServiceabilityService.is_serviceable(postcode=postcode)

        return Response(
            {
                "postcode": postcode,
                "serviceable": is_serviceable,
                "zone": {"id": zone.id, "name": zone.name, "default_eta_minutes": zone.default_eta_minutes} if zone else None,
            },
            status=status.HTTP_200_OK,
        )


class AssignmentStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update delivery assignment status",
        request_body=AssignmentStatusUpdateSerializer,
        responses={200: "Assignment status updated"},
    )
    def patch(self, request, assignment_id):
        assignment = get_object_or_404(DeliveryAssignment, id=assignment_id)
        if not request.user.is_staff and assignment.assignee_id != request.user.id:
            return Response({"detail": "You do not have permission to update this assignment."}, status=403)

        serializer = AssignmentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assignment = DeliveryTransitionService.transition(
            assignment=assignment,
            to_status=serializer.validated_data["status"],
            actor=request.user,
            note=serializer.validated_data.get("note", ""),
        )

        return Response(
            {
                "id": assignment.id,
                "status": assignment.status,
            },
            status=status.HTTP_200_OK,
        )


class OrderDeliveryTimelineAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_summary="Get order delivery timeline", responses={200: DeliveryTimelineSerializer})
    def get(self, request, order_id):
        queryset = DeliveryAssignment.objects.filter(order_id=order_id).prefetch_related("events__actor").select_related(
            "assignee", "order"
        )

        if not request.user.is_staff:
            queryset = queryset.filter(order__user=request.user)

        assignment = get_object_or_404(queryset.order_by("-created_at"))
        return Response(DeliveryTimelineSerializer(assignment).data, status=status.HTTP_200_OK)
