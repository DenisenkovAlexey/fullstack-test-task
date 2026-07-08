'use client';

import { useState } from 'react';
import { Button, Form, Modal } from 'react-bootstrap';

type AddFileModalProps = {
  show: boolean;
  onHide: () => void;
  onSubmit: (title: string, file: File) => Promise<void>;
  isSubmitting: boolean;
};

export function AddFileModal({ show, onHide, onSubmit, isSubmitting }: AddFileModalProps) {
  const [title, setTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      return;
    }

    onSubmit(title, selectedFile).then(() => {
      setTitle('');
      setSelectedFile(null);
      onHide();
    });
  }

  function handleClose() {
    setTitle('');
    setSelectedFile(null);
    onHide();
  }

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Например, Договор с подрядчиком"
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              onChange={(event) =>
                setSelectedFile((event.target as HTMLInputElement).files?.[0] ?? null)
              }
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={handleClose}>
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? 'Загрузка...' : 'Сохранить'}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
