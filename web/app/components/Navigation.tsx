import { Link, useLocation } from '@remix-run/react';

const Navigation = () => {
  const location = useLocation();

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold text-gray-900">
              📰 SSU KA NEWS
            </Link>
            <div className="hidden md:flex items-center space-x-6">
              <NavLink to="/" label="홈" />
              <NavLink to="/article" label="기사 목록" />
            </div>
          </div>
        </div>

        {/* Mobile menu - always visible */}
        <div className="md:hidden py-2 border-t border-gray-200">
          <div className="flex space-x-4">
            <NavLink to="/" label="홈" />
            <NavLink to="/article" label="기사 목록" />
          </div>
        </div>
      </div>
    </nav>
  );
};

const NavLink = ({ to, label }: { to: string; label: string }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`${isActive ? 'text-blue-600 font-medium' : 'text-gray-500 hover:text-gray-700'} 
        text-sm md:text-base px-2 py-1 md:px-3 md:py-2 rounded-md transition-colors`}
    >
      {label}
    </Link>
  );
};

export default Navigation;
