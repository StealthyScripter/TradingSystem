"use client";
import { useState, useEffect, useRef } from "react";
import Link from 'next/link';

interface MenuItem {
  href: string;
  label: string;
}

interface HamburgerMenuProps {
  menuItems?: MenuItem[];
  className?: string;
}

const defaultMenuItems: MenuItem[] = [
  { href: "/", label: "Dashboard" },
  { href: "/accounts", label: "Accounts" },
  { href: "/assets", label: "Assets" },
  { href: "/performance", label: "Performance" },
  { href: "/new", label: "Analytics" },
  { href: "/pricing", label: "Pricing" },
  { href: "/help", label: "Help Center" },
  { href: "/docs", label: "Documentation" },
  { href: "/api-docs", label: "API Docs" },
  { href: "/settings", label: "Settings" },
];

export default function HamburgerMenu({
  menuItems = defaultMenuItems,
  className = ""
}: HamburgerMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Close menu when pressing Escape
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  return (
    <div className={`relative ${className}`} ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-md text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="Menu"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <svg
          className="h-6 w-6"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="py-2">
            {/* Main Navigation Items */}
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-100">
              Navigation
            </div>
            {menuItems.slice(0, 5).map((item, index) => (
              <Link
                key={index}
                href={item.href}
                className="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors duration-150"
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </Link>
            ))}

            {/* Support & Resources */}
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-100 mt-2">
              Support & Resources
            </div>
            {menuItems.slice(5, 9).map((item, index) => (
              <Link
                key={index + 5}
                href={item.href}
                className="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors duration-150"
                onClick={() => setIsOpen(false)}
              >
                {item.label}
              </Link>
            ))}

            {/* Settings */}
            <div className="border-t border-gray-100 mt-2">
              {menuItems.slice(9).map((item, index) => (
                <Link
                  key={index + 9}
                  href={item.href}
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors duration-150"
                  onClick={() => setIsOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* Footer Links */}
            <div className="border-t border-gray-100 mt-2 pt-2">
              <div className="flex flex-col space-y-1 px-4 py-2">
                <Link
                  href="/security"
                  className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Security
                </Link>
                <Link
                  href="/status"
                  className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  System Status
                </Link>
                <Link
                  href="/privacy"
                  className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Privacy Policy
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
