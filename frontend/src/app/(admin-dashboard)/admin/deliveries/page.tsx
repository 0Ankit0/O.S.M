'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAdminDeliveryAssignments, useAdminDeliveryZones, useAdminOverview } from '@/hooks';

export default function AdminDeliveriesPage() {
  const { data: overview } = useAdminOverview();
  const { data: assignments } = useAdminDeliveryAssignments();
  const { data: zones } = useAdminDeliveryZones();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Deliveries</h1>
        <p className="text-gray-500">Track dispatch load, delivery status progression, and zone coverage.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          ['Active assignments', overview?.active_delivery_assignments ?? 0],
          ['Delivery zones', zones?.length ?? 0],
          ['Failed deliveries', assignments?.filter((item) => item.status === 'failed').length ?? 0],
        ].map(([label, value]) => (
          <Card key={String(label)}>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">{label}</p>
              <p className="mt-2 text-3xl font-semibold text-gray-900">{value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Assignment Board</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {assignments?.map((assignment) => (
            <div key={assignment.id} className="rounded-lg border border-gray-200 p-4 text-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Assignment #{assignment.id} · Order #{assignment.order_id}</p>
                  <p className="text-xs text-gray-500">
                    Zone {assignment.delivery_zone_id} · Staff {assignment.staff_user_id ?? 'unassigned'} · Attempts {assignment.attempt_count}
                  </p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  {assignment.status}
                </span>
              </div>
              {assignment.failure_reasons.length ? (
                <p className="mt-3 text-xs text-rose-700">Failure reasons: {assignment.failure_reasons.join(', ')}</p>
              ) : null}
            </div>
          ))}
          {!assignments?.length ? <p className="text-sm text-gray-500">No delivery assignments yet.</p> : null}
        </CardContent>
      </Card>
    </div>
  );
}
