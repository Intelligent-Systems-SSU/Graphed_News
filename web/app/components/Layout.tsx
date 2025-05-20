import { ReactNode } from 'react';
import Navigation from './Navigation';

type LayoutProps = {
  children: ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      <main className="pt-5">
        {children}
      </main>
    </div>
  );
};

export default Layout;
