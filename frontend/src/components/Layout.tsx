import React from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

interface LayoutProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}

export default function Layout({ title, subtitle, children }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-paper">
      <Sidebar />
      <div className="flex-1 min-w-0">
        <Topbar title={title} subtitle={subtitle} />
        <main className="px-6 lg:px-10 py-8">{children}</main>
      </div>
    </div>
  );
}
