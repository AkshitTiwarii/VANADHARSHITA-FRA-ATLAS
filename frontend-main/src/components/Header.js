import React, { useState } from 'react';
import { Button } from './ui/button';
import { Avatar, AvatarFallback } from './ui/avatar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from './ui/dropdown-menu';
import { Menu, X, Bell, LogOut, User, Settings, Trees, Globe } from 'lucide-react';
import { useAuth } from '../App';
import { useTranslation } from '../contexts/LanguageContext';
import LanguageSelector from './LanguageSelector';

const Header = ({ user, sidebarOpen, setSidebarOpen }) => {
  const { logout } = useAuth();
  const { currentLanguage, changeLanguage, translate: t } = useTranslation();

  const handleLogout = () => {
    logout();
  };

  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    changeLanguage(newLanguage);
    console.log('Language changed to:', newLanguage);
  };

  return (
    <header className="bg-white border-b-4 border-orange-500 shadow-sm fixed top-0 left-0 right-0 z-50">
      <div className="flex items-center justify-between px-3 sm:px-4 py-2 sm:py-3">
        {/* Left Section */}
        <div className="flex items-center space-x-2 sm:space-x-4 flex-1 min-w-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-blue-900 hover:bg-blue-50 flex-shrink-0"
          >
            {sidebarOpen ? <X className="w-4 h-4 sm:w-5 sm:h-5" /> : <Menu className="w-4 h-4 sm:w-5 sm:h-5" />}
          </Button>
          
          <div className="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-blue-900 rounded-full flex items-center justify-center flex-shrink-0">
              <Trees className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <div className="min-w-0 flex-1">
              <h1 className="text-base sm:text-xl font-bold text-blue-900 truncate">FRA-Connect</h1>
              <p className="text-xs text-slate-600 hidden md:block truncate">{t('systemSubtitle')}</p>
            </div>
          </div>
        </div>

        {/* Center Section - Breadcrumb/Title */}
        <div className="hidden lg:flex items-center space-x-2 text-sm text-slate-600">
          <Globe className="w-4 h-4" />
          <span>{t('ministryOfTribalAffairs')}</span>
        </div>

        {/* Right Section */}
        <div className="flex items-center space-x-1 sm:space-x-3 flex-shrink-0">
          {/* Enhanced Language Selector */}
          <div className="hidden sm:block">
            <LanguageSelector />
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative text-slate-600 hover:bg-slate-100 p-1 sm:p-2">
            <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full text-[8px] sm:text-xs flex items-center justify-center text-white">
              3
            </span>
          </Button>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center space-x-1 sm:space-x-2 hover:bg-slate-100 p-1 sm:p-2">
                <Avatar className="w-6 h-6 sm:w-8 sm:h-8">
                  <AvatarFallback className="bg-blue-900 text-white text-xs sm:text-sm">
                    {user?.full_name?.split(' ')?.map(n => n[0])?.join('') || 'U'}
                  </AvatarFallback>
                </Avatar>
                <div className="hidden lg:block text-left">
                  <p className="text-sm font-medium text-slate-900">{user?.full_name}</p>
                  <p className="text-xs text-slate-600 capitalize">{user?.role} | {user?.department}</p>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56" sideOffset={5}>
              <div className="px-3 py-2 border-b">
                <p className="font-medium text-slate-900 truncate">{user?.full_name}</p>
                <p className="text-sm text-slate-600 truncate">{user?.email}</p>
                <p className="text-xs text-slate-500 capitalize truncate">{user?.role} - {user?.department}</p>
                {user?.state && (
                  <p className="text-xs text-slate-500 truncate">{user?.district}, {user?.state}</p>
                )}
              </div>
              
              {/* Mobile Language Selector */}
              <div className="sm:hidden px-3 py-2 border-b">
                <LanguageSelector />
              </div>
              
              <DropdownMenuItem className="cursor-pointer">
                <User className="w-4 h-4 mr-2" />
                {t('profile')}
              </DropdownMenuItem>
              
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="w-4 h-4 mr-2" />
                {t('settings')}
              </DropdownMenuItem>
              
              <DropdownMenuSeparator />
              
              <DropdownMenuItem 
                className="cursor-pointer text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                {t('logout')}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Secondary Header Bar */}
      <div className="bg-blue-900 text-white px-3 sm:px-4 py-1">
        <div className="flex items-center justify-between text-xs sm:text-sm">
          <div className="flex items-center space-x-2 sm:space-x-4">
            <span className="text-orange-300">●</span>
            <span className="truncate">{t('secureGovernmentPortal')}</span>
          </div>
          <div className="hidden md:flex items-center space-x-4 text-xs">
            <span>{t('lastLogin')}: {new Date().toLocaleDateString()}</span>
            <span>|</span>
            <span>{t('nicCertified')}</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;