import { ReactNode } from 'react';
import Navigation from './Navigation';

type LayoutProps = {
  children: ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Navigation />
      <main className="grow-1 flex flex-col">{children}</main>
    </div>
  );
};

export default Layout;
