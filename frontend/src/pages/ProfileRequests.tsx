import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useToast } from '@/hooks/use-toast';

interface ChangeRequest {
  id: string;
  field_name: string;
  new_value: string;
  status: 'pending' | 'approved' | 'rejected';
  requested_at: string;
}

const mockRequests: ChangeRequest[] = [
  {
    id: '1',
    field_name: 'department',
    new_value: 'Product',
    status: 'pending',
    requested_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    field_name: 'name',
    new_value: 'John Smith',
    status: 'approved',
    requested_at: '2024-01-10T09:00:00Z',
  },
];

export default function ProfileRequests() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [requests, setRequests] = useState<ChangeRequest[]>(mockRequests);
  const [fieldName, setFieldName] = useState<string>('name');
  const [newValue, setNewValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newRequest: ChangeRequest = {
      id: String(requests.length + 1),
      field_name: fieldName,
      new_value: newValue,
      status: 'pending',
      requested_at: new Date().toISOString(),
    };

    setRequests([newRequest, ...requests]);
    setNewValue('');
    
    toast({
      title: 'Change request submitted',
      description: 'Your request has been sent to team leaders for approval.',
    });
  };

  const getStatusColor = (status: ChangeRequest['status']) => {
    switch (status) {
      case 'approved': return 'bg-success text-white';
      case 'rejected': return 'bg-destructive text-destructive-foreground';
      default: return 'bg-warning text-white';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold text-foreground mb-8">My Profile & Change Requests</h1>

      {/* Current Profile */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Current Profile Information</CardTitle>
          <CardDescription>Your current account details (read-only)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Name</p>
              <p className="text-foreground">{user?.name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Email</p>
              <p className="text-foreground">{user?.email}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Department</p>
              <p className="text-foreground">{user?.department}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Role</p>
              <p className="text-foreground capitalize">{user?.role.replace('_', ' ')}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submit Change Request */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Request Profile Change</CardTitle>
          <CardDescription>
            Submit a request to update your profile information. All changes require approval from a team leader.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="field">Field to Change</Label>
              <Select value={fieldName} onValueChange={setFieldName}>
                <SelectTrigger id="field">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="name">Name</SelectItem>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="department">Department</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="newValue">New Value</Label>
              <Input
                id="newValue"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder={`Enter new ${fieldName}`}
                required
              />
            </div>

            <Button type="submit">Submit Request</Button>
          </form>
        </CardContent>
      </Card>

      {/* Request History */}
      <Card>
        <CardHeader>
          <CardTitle>Request History</CardTitle>
          <CardDescription>All your submitted change requests and their status</CardDescription>
        </CardHeader>
        <CardContent>
          {requests.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">No change requests yet</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Field</TableHead>
                  <TableHead>New Value</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Requested At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {requests.map(request => (
                  <TableRow key={request.id}>
                    <TableCell className="font-medium capitalize">{request.field_name}</TableCell>
                    <TableCell>{request.new_value}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(request.status)}>
                        {request.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(request.requested_at).toLocaleDateString()}
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
