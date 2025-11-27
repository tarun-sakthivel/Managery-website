import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Search, Edit } from 'lucide-react';
import { EmployeeEditDialog } from '@/components/EmployeeEditDialog';
import { User } from '@/contexts/AuthContext';

const mockEmployees: User[] = [
  {
    id: '1',
    name: 'John Employee',
    email: 'employee@proutask.com',
    department: 'Engineering',
    role: 'employee',
  },
  {
    id: '2',
    name: 'Sarah Leader',
    email: 'leader@proutask.com',
    department: 'Engineering',
    role: 'team_leader',
  },
  {
    id: '3',
    name: 'Mike Developer',
    email: 'mike@proutask.com',
    department: 'Engineering',
    role: 'employee',
  },
  {
    id: '4',
    name: 'Lisa Designer',
    email: 'lisa@proutask.com',
    department: 'Design',
    role: 'employee',
  },
];

export default function EmployeeDirectory() {
  const [employees, setEmployees] = useState<User[]>(mockEmployees);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEmployee, setSelectedEmployee] = useState<User | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const filteredEmployees = employees.filter(emp =>
    emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.department.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleEditEmployee = (employee: User) => {
    setSelectedEmployee(employee);
    setIsDialogOpen(true);
  };

  const handleSaveEmployee = (updatedEmployee: User) => {
    setEmployees(employees.map(emp => 
      emp.id === updatedEmployee.id ? updatedEmployee : emp
    ));
    setIsDialogOpen(false);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Employee Directory</h1>
        <p className="text-muted-foreground">
          Manage all employees and their information
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Employees</CardTitle>
          <CardDescription>Search and edit employee details</CardDescription>
          <div className="relative mt-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, email, or department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Role</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredEmployees.map(employee => (
                <TableRow key={employee.id}>
                  <TableCell className="font-medium">{employee.name}</TableCell>
                  <TableCell>{employee.email}</TableCell>
                  <TableCell>{employee.department}</TableCell>
                  <TableCell>
                    <Badge variant={employee.role === 'team_leader' ? 'default' : 'secondary'}>
                      {employee.role.replace('_', ' ')}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditEmployee(employee)}
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {filteredEmployees.length === 0 && (
            <p className="text-center text-muted-foreground py-8">
              No employees found matching your search
            </p>
          )}
        </CardContent>
      </Card>

      <EmployeeEditDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        employee={selectedEmployee}
        onSave={handleSaveEmployee}
      />
    </div>
  );
}
