// import { useState, useEffect } from 'react';
// import { Button } from '@/components/ui/button';
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
// import { Input } from '@/components/ui/input';
// import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
// import { Badge } from '@/components/ui/badge';
// import { Search, Edit, Loader2 } from 'lucide-react';
// import { EmployeeEditDialog } from '@/components/EmployeeEditDialog';
// import { User } from '@/contexts/AuthContext';
// import { apiFetch } from '@/lib/api';
// import { useAuth } from '@/contexts/AuthContext';
// import { useToast } from '@/hooks/use-toast';

// export default function EmployeeDirectory() {
//   const [employees, setEmployees] = useState<User[]>([]);
//   const [searchTerm, setSearchTerm] = useState('');
//   const [selectedEmployee, setSelectedEmployee] = useState<User | null>(null);
//   const [isDialogOpen, setIsDialogOpen] = useState(false);
//   const [loading, setLoading] = useState(true);
//   const { token } = useAuth();
//   const { toast } = useToast();

//   useEffect(() => {
//     async function fetchEmployees() {
//       try {
//         setLoading(true);
//         const data = await apiFetch('/employees/?skip=0&limit=100', 'GET', undefined, token);
//         setEmployees(data || []);
//       } catch (error: any) {
//         toast({
//           title: 'Error',
//           description: error?.message || 'Failed to fetch employees',
//           variant: 'destructive'
//         });
//       } finally {
//         setLoading(false);
//       }
//     }

//     if (token) {
//       fetchEmployees();
//     }
//   }, [token, toast]);

//   const filteredEmployees = employees.filter(emp =>
//     emp.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
//     emp.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
//     emp.department?.toLowerCase().includes(searchTerm.toLowerCase())
//   );

//   const handleEditEmployee = (employee: User) => {
//     setSelectedEmployee(employee);
//     setIsDialogOpen(true);
//   };

//   const handleSaveEmployee = (updatedEmployee: User) => {
//     setEmployees(employees.map(emp =>
//       emp.id === updatedEmployee.id ? updatedEmployee : emp
//     ));
//     setIsDialogOpen(false);
//   };

//   return (
//     <div className="container mx-auto px-4 py-8">
//       <div className="mb-8">
//         <h1 className="text-3xl font-bold text-foreground mb-2">Employee Directory</h1>
//         <p className="text-muted-foreground">
//           Manage all employees and their information
//         </p>
//       </div>

//       <Card>
//         <CardHeader>
//           <CardTitle>All Employees</CardTitle>
//           <CardDescription>Search and edit employee details</CardDescription>
//           <div className="relative mt-4">
//             <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
//             <Input
//               placeholder="Search by name, email, or department..."
//               value={searchTerm}
//               onChange={(e) => setSearchTerm(e.target.value)}
//               className="pl-10"
//             />
//           </div>
//         </CardHeader>
//         <CardContent>
//           {loading ? (
//             <div className="flex justify-center items-center py-12">
//               <Loader2 className="h-8 w-8 animate-spin text-purple-700" />
//             </div>
//           ) : (
//             <Table>
//               <TableHeader>
//                 <TableRow>
//                   <TableHead>Name</TableHead>
//                   <TableHead>Email</TableHead>
//                   <TableHead>Department</TableHead>
//                   <TableHead>Role</TableHead>
//                   <TableHead className="text-right">Actions</TableHead>
//                 </TableRow>
//               </TableHeader>
//               <TableBody>
//                 {filteredEmployees.map(employee => (
//                   <TableRow key={employee.id}>
//                     <TableCell className="font-medium">{employee.name}</TableCell>
//                     <TableCell>{employee.email}</TableCell>
//                     <TableCell>{employee.department}</TableCell>
//                     <TableCell>
//                       <Badge variant={employee.role === 'team_leader' ? 'default' : 'secondary'}>
//                         {employee.role.replace('_', ' ')}
//                       </Badge>
//                     </TableCell>
//                     <TableCell className="text-right">
//                       <Button
//                         variant="outline"
//                         size="sm"
//                         onClick={() => handleEditEmployee(employee)}
//                       >
//                         <Edit className="h-4 w-4 mr-2" />
//                         Edit
//                       </Button>
//                     </TableCell>
//                   </TableRow>
//                 ))}
//               </TableBody>
//             </Table>

//             {filteredEmployees.length === 0 && (
//             <p className="text-center text-muted-foreground py-8">
//               No employees found matching your search
//             </p>
//           )}
//           )}
//         </CardContent>
//       </Card>

//       <EmployeeEditDialog
//         open={isDialogOpen}
//         onOpenChange={setIsDialogOpen}
//         employee={selectedEmployee}
//         onSave={handleSaveEmployee}
//       />
//     </div>
//   );
// }

// src/EmployeeDirectory.tsx
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Search, Edit, Loader2 } from "lucide-react";
import { EmployeeEditDialog } from "@/components/EmployeeEditDialog";
import type { User } from "@/contexts/AuthContext";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

/**
 * Normalize a raw employee object coming from the backend into the UI-friendly User shape.
 * - Ensures id is a string (prefers _id -> string)
 * - Converts potential nested/Date fields into strings
 * - Protects against unexpected shapes
 */
function normalizeEmployee(raw: any): User {
  const _id =
    raw.id ??
    raw._id ??
    (raw._id && raw._id.$oid) ??
    (raw._id && String(raw._id)) ??
    String(Math.random()); // fallback (shouldn't happen)

  // ensure strings for fields we display
  const name = raw.name ?? raw.fullName ?? raw.firstName ?? "";
  const email = raw.email ?? "";
  const department =
    typeof raw.department === "string"
      ? raw.department
      : raw.department?.name ?? JSON.stringify(raw.department ?? "") ?? "";
  const role = raw.role ?? "employee";

  return {
    id: String(_id),
    name: String(name),
    email: String(email),
    department: String(department),
    role: String(role) as User["role"],
  } as User;
}

export default function EmployeeDirectory() {
  const [employees, setEmployees] = useState<User[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<User | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  // Make sure your AuthContext actually exposes a token. If not, adapt accordingly.
  const auth = useAuth();
  // adapt for both shapes: { token } or { user, token } etc.
  // If your useAuth returns token directly, change to: const { token } = useAuth();
  const token = (auth as any)?.token ?? (localStorage.getItem("auth_token") ?? null);

  const { toast } = useToast();

  useEffect(() => {
    let mounted = true;

    async function fetchEmployees() {
      if (!token) {
        // If token missing, don't try calling API
        setEmployees([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        // call endpoint (no need to append query here; API helper can accept path)
        const data = await apiFetch("/employees/?skip=0&limit=100", "GET", undefined, token);

        if (!mounted) return;

        // defensive: normalize array or single object responses
        if (Array.isArray(data)) {
          setEmployees(data.map(normalizeEmployee));
        } else if (data && typeof data === "object") {
          // sometimes backend returns { items: [...], meta: {...} }
          if (Array.isArray((data as any).items)) {
            setEmployees((data as any).items.map(normalizeEmployee));
          } else {
            // single object -> convert into array
            setEmployees([normalizeEmployee(data)]);
          }
        } else {
          setEmployees([]);
        }
      } catch (error: any) {
        toast({
          title: "Error fetching employees",
          description: error?.message ?? JSON.stringify(error) ?? "Unknown error",
          // variant: 'destructive' // uncomment if your toast supports variant
        });
        setEmployees([]);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchEmployees();

    return () => {
      mounted = false;
    };
  }, [token, toast]);

  const filteredEmployees = employees.filter((emp) => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return true;
    return (
      (emp.name ?? "").toLowerCase().includes(q) ||
      (emp.email ?? "").toLowerCase().includes(q) ||
      (emp.department ?? "").toLowerCase().includes(q)
    );
  });

  const handleEditEmployee = (employee: User) => {
    setSelectedEmployee(employee);
    setIsDialogOpen(true);
  };

  const handleSaveEmployee = (updatedEmployee: User) => {
    // keep state normalized
    setEmployees((prev) =>
      prev.map((emp) => (emp.id === updatedEmployee.id ? normalizeEmployee(updatedEmployee) : emp))
    );
    setIsDialogOpen(false);
  };

  const roleBadgeClass = (role: string) => {
    return role === "team_leader"
      ? "bg-purple-600 text-white px-2 py-0.5 rounded text-xs"
      : "bg-gray-100 text-gray-800 px-2 py-0.5 rounded text-xs";
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Employee Directory</h1>
        <p className="text-muted-foreground">Manage all employees and their information</p>
      </div>

      <Card>
        <CardHeader className="flex flex-col gap-4">
          <div className="flex items-start justify-between w-full">
            <div>
              <CardTitle>All Employees</CardTitle>
              <CardDescription>Search and edit employee details</CardDescription>
            </div>
          </div>

          <div className="relative w-full mt-2">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, email, or department..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardHeader>

        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-purple-700" />
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Role</TableHead>
                    {/* <TableHead className="text-right">Actions</TableHead> */}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEmployees.map((employee) => (
                    <TableRow key={employee.id}>
                      <TableCell className="font-medium">{employee.name}</TableCell>
                      <TableCell>{employee.email}</TableCell>
                      <TableCell>{employee.department}</TableCell>
                      <TableCell>
                        <span className={roleBadgeClass(employee.role)}>{employee.role.replace("_", " ")}</span>
                      </TableCell>
                      {/* <TableCell className="text-right">
                        <Button variant="outline" size="sm" onClick={() => handleEditEmployee(employee)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                      </TableCell> */}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {filteredEmployees.length === 0 && (
                <p className="text-center text-muted-foreground py-8">No employees found matching your search</p>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <EmployeeEditDialog open={isDialogOpen} onOpenChange={setIsDialogOpen} employee={selectedEmployee} onSave={handleSaveEmployee} />
    </div>
  );
}
