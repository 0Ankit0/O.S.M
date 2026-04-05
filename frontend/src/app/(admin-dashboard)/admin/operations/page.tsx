'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAdminFulfillmentTasks, useAdminOverview } from '@/hooks';

export default function AdminOperationsPage() {
  const { data: overview } = useAdminOverview();
  const { data: tasks } = useAdminFulfillmentTasks();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Kitchen Queue</h1>
        <p className="text-gray-500">Monitor orders currently being prepared in the kitchen.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {[
          ['Active orders', overview?.active_orders ?? 0],
          ['Preparing now', overview?.active_fulfillment_tasks ?? 0],
          ['Delivered today', overview?.delivered_orders ?? 0],
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
          <CardTitle>Orders in Kitchen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {tasks?.map((task) => (
            <div key={task.id} className="rounded-lg border border-gray-200 p-4 text-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Order #{task.order_id}</p>
                  <p className="text-xs text-gray-500">
                    Assigned to: {task.assigned_user_id ? `Staff #${task.assigned_user_id}` : 'Unassigned'}
                  </p>
                </div>
                <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-medium text-orange-700 capitalize">
                  {task.status}
                </span>
              </div>
            </div>
          ))}
          {!tasks?.length ? <p className="text-sm text-gray-500">No orders currently being prepared.</p> : null}
        </CardContent>
      </Card>
    </div>
  );
}
