'use client';

import { useEffect, useState } from 'react';
import type { AlertItem } from '../types';
import { loadAlerts } from '../api/alertsApi';
import { useApiUrl } from '@/ui/providers/ApiUrlProvider';

export function useAlerts() {
  const apiUrl = useApiUrl();
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function loadData() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const data = await loadAlerts(apiUrl);
      setAlerts(data);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, [apiUrl]);

  return {
    alerts,
    isLoading,
    errorMessage,
    setErrorMessage,
    loadData,
  };
}
