"use client";
import { useState, useEffect, useRef } from "react";
import Link from 'next/link';

interface HeaderProps {
  title: string;
  subtitle?:string;
}

export default function Header({title, subtitle}: HeaderProps) {
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

  return (
    <div className="mb-8 flex items-center justify-between">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-xl font-bold text-gray-900">
          {title}
        </h1>
        {subtitle && <p className="text-gray-600 text-lg">
          {subtitle}
        </p>}
      </div>
    </div>
  );
}
