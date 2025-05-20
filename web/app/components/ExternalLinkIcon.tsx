import React from 'react';

interface ExternalLinkIconProps extends React.SVGProps<SVGSVGElement> {
  className?: string;
}

const ExternalLinkIcon: React.FC<ExternalLinkIconProps> = ({ className = '', ...props }) => (
  <span className="inline-flex items-center">
    <svg
      className={`w-4 h-4 ml-1 ${className}`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      focusable="false"
      role="img"
      {...props}
    >
      <title>외부 링크</title>
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
      />
    </svg>
    <span className="sr-only">(새 창에서 열기)</span>
  </span>
);

export default ExternalLinkIcon;
