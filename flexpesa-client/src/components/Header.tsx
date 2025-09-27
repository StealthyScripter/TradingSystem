"use client";

interface HeaderProps {
  title: string;
  subtitle?: string;
  children?: React.ReactNode; // For additional content like buttons
}

export default function Header({ title, subtitle, children }: HeaderProps) {
  return (
    <div className="page-header flex items-start justify-between">
      <div className="flex-1">
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle mt-2">{subtitle}</p>}
      </div>
      {children && (
        <div className="flex items-center gap-3 ml-6">
          {children}
        </div>
      )}
    </div>
  );
}
