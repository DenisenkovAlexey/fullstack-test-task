import { apiRequest } from '@/shared/api/client';
import type { AlertItem } from '../types';
import { ALERTS_ENDPOINT } from '@/shared/constants/api';

export async function loadAlerts(apiUrl: string): Promise<AlertItem[]> {
  return apiRequest<AlertItem[]>(apiUrl, ALERTS_ENDPOINT, { cache: 'no-store' });
}
