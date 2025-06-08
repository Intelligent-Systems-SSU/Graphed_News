import { ReactNode } from 'react';
import Navigation, { NavContextProv, useNavState } from './Navigation';

type LayoutProps = {
  children: ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
  const navState = useNavState();
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {navState.isEnable && <Navigation />}
      <NavContextProv value={navState}>
        <main className="grow-1 flex flex-col">{children}</main>
      </NavContextProv>
    </div>
  );
};

export default Layout;
