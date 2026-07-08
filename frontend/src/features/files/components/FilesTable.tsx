'use client';

import { Button, Table } from 'react-bootstrap';
import type { FileItem } from '../types';
import { useApiUrl } from '@/ui/providers/ApiUrlProvider';
import { getFileDownloadUrl } from '../api/filesApi';
import { formatDate, formatSize, getProcessingVariant } from '@/shared/utils';
import { StatusBadge } from '@/ui/components/StatusBadge';

type FilesTableProps = {
  files: FileItem[];
  isLoading: boolean;
};

export function FilesTable({ files, isLoading }: FilesTableProps) {
  const apiUrl = useApiUrl();

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center py-5">
        <div className="spinner-border" role="status" />
      </div>
    );
  }

  if (files.length === 0) {
    return (
      <div className="text-center py-4 text-secondary">
        Файлы пока не загружены
      </div>
    );
  }

  return (
    <div className="table-responsive">
      <Table hover bordered className="align-middle mb-0">
        <thead className="table-light">
          <tr>
            <th>Название</th>
            <th>Файл</th>
            <th>MIME</th>
            <th>Размер</th>
            <th>Статус</th>
            <th>Проверка</th>
            <th>Создан</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.id}>
              <td>
                <div className="fw-semibold">{file.title}</div>
                <div className="small text-secondary">{file.id}</div>
              </td>
              <td>{file.original_name}</td>
              <td>{file.mime_type}</td>
              <td>{formatSize(file.size)}</td>
              <td>
                <StatusBadge variant={getProcessingVariant(file.processing_status)}>
                  {file.processing_status}
                </StatusBadge>
              </td>
              <td>
                <div className="d-flex flex-column gap-1">
                  <StatusBadge variant={file.requires_attention ? 'warning' : 'success'}>
                    {file.scan_status ?? 'pending'}
                  </StatusBadge>
                  <span className="small text-secondary">
                    {file.scan_details ?? 'Ожидает обработки'}
                  </span>
                </div>
              </td>
              <td>{formatDate(file.created_at)}</td>
              <td className="text-nowrap">
                <Button
                  as="a"
                  href={getFileDownloadUrl(apiUrl, file.id)}
                  variant="outline-primary"
                  size="sm"
                >
                  Скачать
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
