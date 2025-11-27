import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiFetch } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

interface ChangeRequest {
  id: string;
  employee_id: string;
  employee_name?: string;
  field_name: string;
  new_value: string;
  reason?: string;
  status: 'pending' | 'approved' | 'rejected';
  requested_at: string;
}

export default function ApprovalsDashboard() {
  const [requests, setRequests] = useState<ChangeRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  const { token } = useAuth();

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const data = await apiFetch('/requests/', 'GET', undefined, token);
      setRequests(data || []);
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error?.message || 'Failed to fetch requests',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId: string, employeeName: string) => {
    try {
      await apiFetch(`/requests/${requestId}/approve`, 'PUT', undefined, token);
      toast({
        title: 'Request Approved',
        description: `${employeeName || 'Employee'}'s change request has been approved.`,
      });
      // Refresh the list
      fetchRequests();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error?.message || 'Failed to approve request',
        variant: 'destructive'
      });
    }
  };

  const handleReject = async (requestId: string, employeeName: string) => {
    try {
      await apiFetch(`/requests/${requestId}/reject`, 'PUT', undefined, token);
      toast({
        title: 'Request Rejected',
        description: `${employeeName || 'Employee'}'s change request has been rejected.`,
        variant: 'destructive',
      });
      // Refresh the list
      fetchRequests();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error?.message || 'Failed to reject request',
        variant: 'destructive'
      });
    }
  };

  const pendingRequests = requests.filter(req => req.status === 'pending');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Approvals Dashboard</h1>
        <p className="text-muted-foreground">
          Review and approve employee profile change requests
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pending Change Requests</CardTitle>
          <CardDescription>
            {pendingRequests.length} request{pendingRequests.length !== 1 ? 's' : ''} awaiting your approval
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-purple-700" />
            </div>
          ) : pendingRequests.length === 0 ? (
            <div className="text-center py-12">
              <CheckCircle className="h-12 w-12 text-success mx-auto mb-4" />
              <p className="text-muted-foreground">No pending requests. All caught up!</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Request ID</TableHead>
                  <TableHead>Employee</TableHead>
                  <TableHead>Field</TableHead>
                  <TableHead>New Value</TableHead>
                  <TableHead>Date Requested</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pendingRequests.map(request => (
                  <TableRow key={request.id}>
                    <TableCell className="font-mono text-sm">{request.id}</TableCell>
                    <TableCell className="font-medium">{request.employee_name}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {request.field_name}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">{request.new_value}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(request.requested_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleApprove(request.id, request.employee_name)}
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleReject(request.id, request.employee_name)}
                        >
                          <XCircle className="h-4 w-4 mr-2" />
                          Reject
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
