'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAdminReturns, useAdminReviewReturn } from '@/hooks';

export default function AdminReturnsPage() {
  const { data: returns } = useAdminReturns();
  const reviewReturn = useAdminReviewReturn();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Returns & Refunds</h1>
        <p className="text-gray-500">Review return requests, inspection outcomes, and refund amounts.</p>
      </div>

      <div className="space-y-4">
        {returns?.map((request) => (
          <Card key={request.id}>
            <CardHeader className="flex flex-row items-start justify-between">
              <div>
                <CardTitle className="text-lg">Return #{request.id} · Order #{request.order_id}</CardTitle>
                <p className="mt-1 text-sm text-gray-500">
                  Reason {request.reason_code} · Requested {new Date(request.created_at).toLocaleString()}
                </p>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                {request.status}
              </span>
            </CardHeader>
            <CardContent className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm text-gray-700">Inspection: {request.inspection_result || 'pending review'}</p>
                <p className="text-sm text-gray-700">Refund amount: EUR {request.refund_amount.toFixed(2)}</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  isLoading={reviewReturn.isPending}
                  onClick={() =>
                    reviewReturn.mutate({
                      returnId: request.id,
                      payload: {
                        status: 'approved',
                        inspection_result: 'Accepted after review',
                        refund_amount: request.refund_amount || 0,
                      },
                    })
                  }
                >
                  Accept
                </Button>
                <Button
                  variant="destructive"
                  isLoading={reviewReturn.isPending}
                  onClick={() =>
                    reviewReturn.mutate({
                      returnId: request.id,
                      payload: {
                        status: 'denied',
                        inspection_result: 'Rejected after review',
                        refund_amount: 0,
                      },
                    })
                  }
                >
                  Reject
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {!returns?.length ? (
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-500">No return requests have been submitted yet.</p>
            </CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
