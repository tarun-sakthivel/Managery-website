import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface ChangeRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  field_name: string;
  new_value: string;
  status: 'pending' | 'approved' | 'rejected';
  requested_at: string;
}

const mockPendingRequests: ChangeRequest[] = [
  {
    id: '1',
    employee_id: '1',
    employee_name: 'John Employee',
    field_name: 'department',
    new_value: 'Product',
    status: 'pending',
    requested_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '3',
    employee_id: '3',
    employee_name: 'Mike Developer',
    field_name: 'email',
    new_value: 'mike.dev@proutask.com',
    status: 'pending',
    requested_at: '2024-01-16T14:30:00Z',
  },
  {
    id: '4',
    employee_id: '4',
    employee_name: 'Lisa Designer',
    field_name: 'name',
    new_value: 'Lisa Brown',
    status: 'pending',
    requested_at: '2024-01-17T09:15:00Z',
  },
];

export default function ApprovalsDashboard() {
  const [requests, setRequests] = useState<ChangeRequest[]>(mockPendingRequests);
  const { toast } = useToast();

  const handleApprove = (requestId: string, employeeName: string) => {
    setRequests(requests.map(req => 
      req.id === requestId ? { ...req, status: 'approved' as const } : req
    ).filter(req => req.status === 'pending'));
    
    toast({
      title: 'Request Approved',
      description: `${employeeName}'s change request has been approved.`,
    });
  };

  const handleReject = (requestId: string, employeeName: string) => {
    setRequests(requests.map(req => 
      req.id === requestId ? { ...req, status: 'rejected' as const } : req
    ).filter(req => req.status === 'pending'));
    
    toast({
      title: 'Request Rejected',
      description: `${employeeName}'s change request has been rejected.`,
      variant: 'destructive',
    });
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
          {pendingRequests.length === 0 ? (
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
