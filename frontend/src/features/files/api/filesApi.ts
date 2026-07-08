import { apiRequest } from '@/shared/api/client';
import type { FileItem } from '../types';
import { FILES_ENDPOINT, FILE_DOWNLOAD_ENDPOINT } from '@/shared/constants/api';

export async function loadFiles(apiUrl: string): Promise<FileItem[]> {
  return apiRequest<FileItem[]>(apiUrl, FILES_ENDPOINT, { cache: 'no-store' });
}

export async function uploadFile(apiUrl: string, formData: FormData): Promise<void> {
  await apiRequest<void>(apiUrl, FILES_ENDPOINT, {
    method: 'POST',
    body: formData,
  });
}

export function getFileDownloadUrl(apiUrl: string, fileId: string): string {
  return `${apiUrl}${FILE_DOWNLOAD_ENDPOINT(fileId)}`;
}
