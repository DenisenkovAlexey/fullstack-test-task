'use client';

import { Alert, Button, Card } from 'react-bootstrap';
import { useFiles } from '../files/hooks/useFiles';
import { useAlerts } from '../alerts/hooks/useAlerts';
import { FilesTable } from '../files/components/FilesTable';
import { AddFileModal } from '../files/components/AddFileModal';
import { AlertsTable } from '../alerts/components/AlertsTable';

export function HomePage() {
  const files = useFiles();
  const alerts = useAlerts();

  return (
    <div className="py-4 px-4 bg-light min-vh-100">
      <div className="d-flex justify-content-center">
        <div className="w-100" style={{ maxWidth: '1140px' }}>
          <Card className="shadow-sm border-0 mb-4">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                <div>
                  <h1 className="h3 mb-2">Управление файлами</h1>
                  <p className="text-secondary mb-0">
                    Загрузка файлов, просмотр статусов обработки и ленты алертов.
                  </p>
                </div>
                <div className="d-flex gap-2">
                  <Button variant="outline-secondary" onClick={() => files.loadData()}>
                    Обновить
                  </Button>
                  <Button variant="primary" onClick={() => files.setShowModal(true)}>
                    Добавить файл
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {(files.errorMessage || alerts.errorMessage) && (
            <Alert variant="danger" className="shadow-sm">
              {files.errorMessage ?? alerts.errorMessage}
            </Alert>
          )}

          <Card className="shadow-sm border-0 mb-4">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Файлы</h2>
                <span className="badge bg-secondary">{files.files.length}</span>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <FilesTable files={files.files} isLoading={files.isLoading} />
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Алерты</h2>
                <span className="badge bg-secondary">{alerts.alerts.length}</span>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              <AlertsTable alerts={alerts.alerts} isLoading={alerts.isLoading} />
            </Card.Body>
          </Card>

          <AddFileModal
            show={files.showModal}
            onHide={() => files.setShowModal(false)}
            onSubmit={async (title, file) => {
              await files.handleUpload(title, file);
            }}
            isSubmitting={files.isSubmitting}
          />
        </div>
      </div>
    </div>
  );
}
