import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, UserCheck, DollarSign, User, LogOut, Menu, X } from 'lucide-react';
import { Button } from '../ui/button';
import referralAgentApi from '../../services/referralAgentApi';

const Layout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const handleLogout = () => {
    referralAgentApi.logout();
    navigate('/referral-agent/login');
  };

  const navigation = [
    { name: 'Dashboard', path: '/referral-agent/dashboard', icon: LayoutDashboard },
    { name: 'Leads', path: '/referral-agent/leads', icon: Users },
    { name: 'Clients', path: '/referral-agent/clients', icon: UserCheck },
    { name: 'Commissions', path: '/referral-agent/commissions', icon: DollarSign },
    { name: 'Profile', path: '/referral-agent/profile', icon: User },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 transition-transform duration-300 ease-in-out lg:static`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-slate-800">
            <div>
              <h1 className="text-2xl font-bold text-white">FIDUS</h1>
              <p className="text-xs text-cyan-400">Agent Portal</p>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-slate-400 hover:text-white"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    active
                      ? 'bg-cyan-600 text-white'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-slate-800">
            <Button
              onClick={handleLogout}
              variant="ghost"
              className="w-full justify-start text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <LogOut className="h-5 w-5 mr-3" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:ml-64 min-h-screen">
        {/* Mobile Header */}
        <header className="lg:hidden bg-slate-900 border-b border-slate-800 p-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-slate-400 hover:text-white"
            >
              <Menu className="h-6 w-6" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-white">FIDUS</h1>
              <p className="text-xs text-cyan-400">Agent Portal</p>
            </div>
            <div className="w-6" /> {/* Spacer for centering */}
          </div>
        </header>

        {/* Page Content */}
        <main className="p-4 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;