// import { useParams } from 'react-router-dom';
// import { useEffect, useState } from 'react';
// import { useAuth } from '@/contexts/AuthContext';
// import { Loader } from 'lucide-react';
// import { useQuery } from "@tanstack/react-query";
// import { apiFetch } from "@/lib/api";

// interface Employee {
//   id: number;
//   email: string;
//   name: string;
//   department: string;
//   role: string;
//   hashed_password?: string;
// }

// export function Profile() {
//   const { id } = useParams();
//   const { user } = useAuth();
//   const [employee, setEmployee] = useState<Employee | null>(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);
  
//   useEffect(() => {
//     async function fetchProfile() {
//       try {
//         const token = localStorage.getItem('auth_token');
//         const response = await fetch(`http://localhost:8000/employees/${id}`, {
//           headers: {
//             'Authorization': `Bearer ${token}`,
//             'Content-Type': 'application/json',
//           },
//         });
        
//         if (!response.ok) {
//           throw new Error(`HTTP ${response.status}`);
//         }
        
//         const data = await response.json();
//         setEmployee(data);
//       } catch (err) {
//         setError(err instanceof Error ? err.message : 'Failed to load profile');
//       } finally {
//         setLoading(false);
//       }
//     }

//     if (id) fetchProfile();
//   }, [id]);

//   if (loading) {
//     return (
//       <div className="flex items-center justify-center min-h-screen">
//         <Loader className="h-6 w-6 animate-spin text-purple-700" />
//       </div>
//     );
//   }

//   if (error) {
//     return (
//       <div className="max-w-2xl mx-auto mt-10 p-6 bg-red-50 border border-red-200 rounded-lg">
//         <p className="text-red-700">Error: {error}</p>
//       </div>
//     );
//   }

//   if (!employee) {
//     return <div className="text-center mt-10">No profile found</div>;
//   }

//   return (
//     <div className="max-w-2xl mx-auto mt-10 p-8 bg-white rounded-lg shadow-lg border border-gray-200">
//       <div className="flex items-center gap-6 mb-8">
//         <div className="w-16 h-16 bg-purple-700 rounded-full flex items-center justify-center text-white text-2xl font-bold">
//           {employee.name?.charAt(0).toUpperCase()}
//         </div>
//         <div>
//           <h1 className="text-2xl font-bold text-gray-900">{employee.name}</h1>
//           <p className="text-gray-600">{employee.email}</p>
//         </div>
//       </div>

//       <div className="grid grid-cols-2 gap-6">
//         <div>
//           <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Department</label>
//           <p className="mt-2 text-lg text-gray-900">{employee.department}</p>
//         </div>
//         <div>
//           <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Role</label>
//           <p className="mt-2 text-lg text-gray-900 capitalize">{employee.role.replace('_', ' ')}</p>
//         </div>
//         <div className="col-span-2">
//           <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Email</label>
//           <p className="mt-2 text-lg text-gray-900">{employee.email}</p>
//         </div>
//       </div>

//       <div className="mt-8 pt-8 border-t border-gray-200">
//         <p className="text-sm text-gray-600">
//           This is your employee profile. Contact your team leader to request changes to your information.
//         </p>
//       </div>
//     </div>
//   );
// }

// src/Profile.tsx
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Loader } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface Employee {
  id: string;
  email: string;
  name: string;
  department: string;
  role: string;
}

export function Profile() {
  const params = useParams();
  const { id: paramId } = params as { id?: string };
  const { user, token } = useAuth();
  const { toast } = useToast();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const employeeId = paramId || user?.id;
    if (!token || !employeeId) {
      setLoading(false);
      setError("No user specified or not authenticated.");
      return;
    }
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        const data = await apiFetch(`/employees/${employeeId}`, "GET", undefined, token);
        if (!mounted) return;
        setEmployee(data);
      } catch (err: any) {
        setError(err?.message || String(err));
        toast({ title: "Failed to load profile", description: err?.message || String(err) });
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [paramId, token, user, toast]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader className="h-6 w-6 animate-spin text-purple-700" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-700">Error: {error}</p>
      </div>
    );
  }

  if (!employee) {
    return <div className="text-center mt-10">No profile found</div>;
  }

  return (
    <div className="max-w-2xl mx-auto mt-10 p-8 bg-white rounded-lg shadow-lg border border-gray-200">
      <div className="flex items-center gap-6 mb-8">
        <div className="w-16 h-16 bg-purple-700 rounded-full flex items-center justify-center text-white text-2xl font-bold">
          {employee.name?.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{employee.name}</h1>
          <p className="text-gray-600">{employee.email}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Department</label>
          <p className="mt-2 text-lg text-gray-900">{employee.department}</p>
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Role</label>
          <p className="mt-2 text-lg text-gray-900 capitalize">{employee.role.replace("_", " ")}</p>
        </div>
        <div className="col-span-2">
          <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide">Email</label>
          <p className="mt-2 text-lg text-gray-900">{employee.email}</p>
        </div>
      </div>

      <div className="mt-8 pt-8 border-t border-gray-200">
        <p className="text-sm text-gray-600">
          This is your employee profile. Contact your team leader to request changes to your information.
        </p>
      </div>
    </div>
  );
}
