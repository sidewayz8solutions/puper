import React from 'react';

import {
  MapPin,
  Menu,
  Settings,
  Star,
  User,
} from 'lucide-react';
import {
  Link,
  useNavigate,
} from 'react-router-dom';

import {
  useAuthStore,
  useUIStore,
} from '../lib/store';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore();
  const { sidebarOpen, setSidebarOpen } = useUIStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-primary-50 to-primary-100">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 bg-white shadow-lg border-r border-primary-200`}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-4 border-b border-primary-200">
            <PuperLogo
              size={sidebarOpen ? "md" : "sm"}
              showText={sidebarOpen}
              className="transition-all duration-300"
            />
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 rounded-lg hover:bg-primary-100 transition-colors"
              aria-label="Toggle sidebar"
            >
              <Menu className="w-5 h-5 text-primary-600" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            <Link
              to="/"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-primary-100 transition-colors group"
            >
              <MapPin className="w-5 h-5 text-primary-600 group-hover:text-psychedelic-purple" />
              {sidebarOpen && <span className="text-primary-700 font-medium">Map</span>}
            </Link>
            
            <Link
              to="/favorites"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-primary-100 transition-colors group"
            >
              <Star className="w-5 h-5 text-primary-600 group-hover:text-psychedelic-pink" />
              {sidebarOpen && <span className="text-primary-700 font-medium">Favorites</span>}
            </Link>
            
            <Link
              to="/profile"
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-primary-100 transition-colors group"
            >
              <User className="w-5 h-5 text-primary-600 group-hover:text-psychedelic-orange" />
              {sidebarOpen && <span className="text-primary-700 font-medium">Profile</span>}
            </Link>
          </nav>

          {/* User Info */}
          <div className="p-4 border-t border-primary-200">
            {sidebarOpen ? (
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-psychedelic-2 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold">
                      {user?.username?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-primary-800 truncate">
                      {user?.username}
                    </p>
                    <p className="text-xs text-primary-600">
                      {user?.points} points
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="w-full text-left text-sm text-primary-600 hover:text-primary-800 transition-colors"
                >
                  Sign out
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={handleLogout}
                className="w-full flex justify-center p-2 rounded-lg hover:bg-primary-100 transition-colors"
                aria-label="Sign out"
              >
                <Settings className="w-5 h-5 text-primary-600" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {children}
      </div>
    </div>
  );
};

export default Layout;
