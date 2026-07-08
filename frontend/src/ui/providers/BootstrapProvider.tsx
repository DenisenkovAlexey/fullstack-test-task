'use client';

import 'bootstrap/dist/css/bootstrap.min.css';
import { ReactNode } from 'react';

export function BootstrapProvider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
