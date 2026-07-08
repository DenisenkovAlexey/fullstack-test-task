'use client';

import { Badge } from 'react-bootstrap';

type StatusBadgeProps = {
  variant?: string;
  children: React.ReactNode;
};

export function StatusBadge({ variant = 'secondary', children }: StatusBadgeProps) {
  return <Badge bg={variant}>{children}</Badge>;
}
