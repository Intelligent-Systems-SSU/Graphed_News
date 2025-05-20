import { Links, Meta, Outlet, Scripts, ScrollRestoration } from '@remix-run/react';
import type { LinksFunction, MetaFunction } from '@remix-run/cloudflare';

import styles from './tailwind.css?url';

export const links: LinksFunction = () => [
  {
    rel: 'stylesheet',
    href: styles,
  },
];
export const meta: MetaFunction = () => {
  return [
    {
      property: 'og:site_name',
      content: 'SSU KA Worlds',
    },
  ];
};

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}
