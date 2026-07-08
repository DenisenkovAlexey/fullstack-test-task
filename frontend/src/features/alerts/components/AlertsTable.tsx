'use client';

import { Table } from 'react-bootstrap';
import type { AlertItem } from '../types';
import { formatDate, getLevelVariant } from '@/shared/utils';
import { StatusBadge } from '@/ui/components/StatusBadge';

type AlertsTableProps = {
  alerts: AlertItem[];
  isLoading: boolean;
};

export function AlertsTable({ alerts, isLoading }: AlertsTableProps) {
  if (isLoading) {
    return (
      <div className="d-flex justify-content-center py-5">
        <div className="spinner-border" role="status" />
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="text-center py-4 text-secondary">
        Алертов пока нет
      </div>
    );
  }

  return (
    <div className="table-responsive">
      <Table hover bordered className="align-middle mb-0">
        <thead className="table-light">
          <tr>
            <th>ID</th>
            <th>File ID</th>
            <th>Уровень</th>
            <th>Сообщение</th>
            <th>Создан</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((item) => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td className="small">{item.file_id}</td>
              <td>
                <StatusBadge variant={getLevelVariant(item.level)}>
                  {item.level}
                </StatusBadge>
              </td>
              <td>{item.message}</td>
              <td>{formatDate(item.created_at)}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
