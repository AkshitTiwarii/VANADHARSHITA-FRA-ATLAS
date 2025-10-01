import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTranslation } from '../contexts/LanguageContext';
import { 
  Home,
  LayoutDashboard, 
  Map, 
  FileText, 
  BarChart3, 
  Shield,
  Trees,
  Upload,
  Users,
  Settings,
  Eye,
  Briefcase,
  Globe,
  ChevronRight
} from 'lucide-react';

const Sidebar = ({ isOpen, userRole }) => {
  const { translate: t } = useTranslation();
  
  // Organized navigation with sections
  const navigationSections = [
    {
      title: 'Main',
      items: [
        {
          name: 'Home',
          href: '/',
          icon: Home,
          roles: ['admin', 'officer', 'verifier', 'viewer'],
          description: 'Landing page'
        },
        {
          name: 'Overview Dashboard',
          href: '/dashboard',
          icon: LayoutDashboard,
          roles: ['admin', 'officer', 'verifier', 'viewer'],
          description: 'System overview & statistics'
        }
      ]
    },
    {
      title: 'Work Management',
      items: [
        {
          name: 'My Work',
          href: '/officer-dashboard',
          icon: Briefcase,
          roles: ['admin', 'officer'],
          description: 'Your assigned tasks & cases',
          badge: 'Officer'
        },
        {
          name: 'Case Processing',
          href: '/cases',
          icon: FileText,
          roles: ['admin', 'officer', 'verifier'],
          description: 'Manage forest rights claims'
        },
        {
          name: 'Interactive Map',
          href: '/atlas',
          icon: Map,
          roles: ['admin', 'officer', 'verifier', 'viewer'],
          description: 'Forest boundaries & claims'
        }
      ]
    },
    {
      title: 'Analysis & Reports',
      items: [
        {
          name: 'Analytics',
          href: '/analytics',
          icon: BarChart3,
          roles: ['admin', 'officer'],
          description: 'Detailed insights & trends'
        },
        {
          name: 'Public Portal',
          href: '/transparency',
          icon: Globe,
          roles: ['admin', 'officer', 'verifier', 'viewer'],
          description: 'Transparency & public data'
        }
      ]
    },
    {
      title: 'Administration',
      items: [
        {
          name: 'System Admin',
          href: '/admin',
          icon: Settings,
          roles: ['admin'],
          description: 'Users, settings & logs',
          badge: 'Admin Only'
        }
      ]
    }
  ];

  const getFilteredSections = () => {
    return navigationSections.map(section => ({
      ...section,
      items: section.items.filter(item => item.roles.includes(userRole))
    })).filter(section => section.items.length > 0);
  };

  const filteredSections = getFilteredSections();

  return (
    <aside className={`bg-blue-900 text-white fixed left-0 top-0 h-full transition-all duration-300 z-40 ${isOpen ? 'w-64' : 'w-16'} shadow-lg`}>
      {/* Header spacing */}
      <div className="h-[120px]"></div>
      
      <div className={`${isOpen ? 'p-4' : 'p-2'} h-[calc(100%-120px)] overflow-y-auto`}>
        {/* Department Info */}
        {isOpen && (
          <div className="mb-6 pb-4 border-b border-blue-800">
            <div className="flex items-center space-x-2 mb-2">
              <Trees className="w-5 h-5 text-green-400" />
              <span className="font-medium text-sm">Forest Department</span>
            </div>
            <p className="text-xs text-blue-200">Digital India Initiative</p>
          </div>
        )}

        {/* Navigation Menu - Organized by Sections */}
        <nav className={`${isOpen ? 'space-y-6' : 'space-y-3'}`}>
          {filteredSections.map((section, sectionIndex) => (
            <div key={section.title}>
              {/* Section Header */}
              {isOpen && (
                <div className="mb-3">
                  <h3 className="text-xs font-semibold text-blue-300 uppercase tracking-wider px-1">
                    {section.title}
                  </h3>
                </div>
              )}
              
              {/* Section Items */}
              <div className={`${isOpen ? 'space-y-1' : 'space-y-2'}`}>
                {section.items.map((item) => (
                  <NavLink
                    key={item.name}
                    to={item.href}
                    className={({ isActive }) =>
                      `flex items-center ${isOpen ? 'space-x-3 px-3 py-2.5' : 'px-2 py-4 justify-center'} rounded-lg transition-all duration-200 group relative ${
                        isActive
                          ? 'bg-orange-500 text-white shadow-lg'
                          : 'text-blue-100 hover:bg-blue-800 hover:text-white'
                      }`
                    }
                    title={!isOpen ? item.name : item.description}
                  >
                    <item.icon className={`${isOpen ? 'w-5 h-5' : 'w-6 h-6'} flex-shrink-0`} />
                    {isOpen && (
                      <div className="flex-1 flex items-center justify-between">
                        <span className="font-medium text-sm">{item.name}</span>
                        {item.badge && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-orange-400 text-white font-medium">
                            {item.badge}
                          </span>
                        )}
                      </div>
                    )}
                    {!isOpen && (
                      <span className="absolute left-16 bg-gray-900 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                        {item.name}
                        {item.badge && ` (${item.badge})`}
                      </span>
                    )}
                  </NavLink>
                ))}
              </div>
              
              {/* Section Divider */}
              {isOpen && sectionIndex < filteredSections.length - 1 && (
                <div className="mt-4 border-t border-blue-800/50"></div>
              )}
            </div>
          ))}
        </nav>

        {/* User Role & System Status */}
        {isOpen && (
          <div className="mt-8 space-y-3">
            {/* User Role Badge */}
            <div className="p-3 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg shadow-lg">
              <div className="flex items-center space-x-2 mb-1">
                <Eye className="h-4 w-4 text-white" />
                <span className="text-xs font-medium text-white/90">Current Role</span>
              </div>
              <p className="text-sm font-bold text-white capitalize">{userRole}</p>
            </div>
            
            {/* System Status */}
            <div className="p-3 bg-blue-800 rounded-lg">
              <h4 className="text-sm font-medium text-blue-100 mb-3">System Status</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-blue-200">Server Status</span>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-green-400">Online</span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-blue-200">Database</span>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span className="text-green-400">Connected</span>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-blue-200">Last Sync</span>
                  <span className="text-blue-200">2 min ago</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;