'use client';

import { createContext, useContext, ReactNode } from 'react';

const ApiUrlContext = createContext<string>('');

export function useApiUrl(): string {
  return useContext(ApiUrlContext);
}

export function ApiUrlProvider({
  value,
  children,
}: {
  value: string;
  children: ReactNode;
}) {
  return <ApiUrlContext.Provider value={value}>{children}</ApiUrlContext.Provider>;
}
