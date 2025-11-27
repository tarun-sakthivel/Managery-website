import { NavLink } from '@/components/NavLink';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { LogOut, User, Settings } from 'lucide-react';
import manageryLogo from '@/assets/managery-logo.png';
import { useState, useRef, useEffect } from 'react';

export function Navbar() {
  const { user, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="bg-gray-50 py-4 sticky top-0 z-50">
      <nav className="bg-white rounded-full mx-auto max-w-7xl px-6 shadow-lg border border-gray-200">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-2">
            <img src={manageryLogo} alt="Managery" className="h-10" />
          </NavLink>

          {/* Navigation Links */}
          <div className="flex items-center gap-8">
            {!user ? (
              // Guest Navigation
              <>
                <NavLink
                  to="/login"
                  className="text-gray-600 hover:text-gray-900 transition-colors text-sm"
                  activeClassName="text-gray-900 font-semibold"
                >
                  Login
                </NavLink>
                <NavLink to="/register">
                  <Button variant="default" className="rounded-full bg-purple-700 hover:bg-purple-800">Register</Button>
                </NavLink>
              </>
            ) : (
              // Authenticated Navigation
              <>
                <NavLink
                  to="/tasks"
                  className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
                  activeClassName="text-gray-900 font-semibold"
                >
                  Tasks Dashboard
                </NavLink>
                {user.role === 'employee' && (
                  <NavLink
                    to="/profile/requests"
                    className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
                    activeClassName="text-gray-900 font-semibold"
                  >
                    My Profile & Requests
                  </NavLink>
                )}
                {user.role === 'team_leader' && (
                  <>
                    <NavLink
                      to="/employees"
                      className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
                      activeClassName="text-gray-900 font-semibold"
                    >
                      Employee Directory
                    </NavLink>
                    <NavLink
                      to="/requests"
                      className="text-gray-600 hover:text-gray-900 transition-colors text-sm font-medium"
                      activeClassName="text-gray-900 font-semibold"
                    >
                      Approvals
                    </NavLink>
                  </>
                )}
                
                {/* Profile Dropdown */}
                <div ref={dropdownRef} className="flex items-center gap-4 ml-8 border-l border-gray-300 pl-8 relative">
                  <button 
                    onClick={() => setProfileOpen(!profileOpen)}
                    className="flex items-center gap-3 hover:bg-gray-100 px-3 py-2 rounded-full transition-colors cursor-pointer"
                  >
                    <div className="text-right text-xs">
                      <div className="text-gray-900 font-medium">{user.email}</div>
                      <div className="text-gray-600 capitalize">{user.role.replace('_', ' ')}</div>
                    </div>
                    <div className="w-8 h-8 bg-purple-700 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                      {user.email?.charAt(0).toUpperCase()}
                    </div>
                  </button>

                  {/* Dropdown Menu */}
                  {profileOpen && (
                    <div className="absolute top-16 right-0 bg-white rounded-lg shadow-xl border border-gray-200 w-56 py-2 z-50">
                      <div className="px-4 py-3 border-b border-gray-200">
                        <div className="font-semibold text-gray-900">{user.email}</div>
                        <div className="text-xs text-gray-600 capitalize">{user.role.replace('_', ' ')}</div>
                      </div>

                      
                      
                      <button
                        onClick={() => {
                          setProfileOpen(false);
                          logout();
                        }}
                        className="w-full flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors text-sm border-t border-gray-200"
                      >
                        <LogOut className="h-4 w-4" />
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </nav>
    </div>
  );
}
