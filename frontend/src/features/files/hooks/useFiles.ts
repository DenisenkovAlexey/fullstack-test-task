'use client';

import { useEffect, useState } from 'react';
import type { FileItem } from '../types';
import { loadFiles, uploadFile } from '../api/filesApi';
import { useApiUrl } from '@/ui/providers/ApiUrlProvider';

export function useFiles() {
  const apiUrl = useApiUrl();
  const [files, setFiles] = useState<FileItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  async function loadData() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const data = await loadFiles(apiUrl);
      setFiles(data);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Произошла ошибка');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, [apiUrl]);

  async function handleUpload(title: string, file: File) {
    setIsSubmitting(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append('title', title.trim());
    formData.append('file', file);

    try {
      await uploadFile(apiUrl, formData);
      setShowModal(false);
      await loadData();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Произошла ошибка');
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  }

  return {
    files,
    isLoading,
    isSubmitting,
    errorMessage,
    setErrorMessage,
    loadData,
    handleUpload,
    showModal,
    setShowModal,
  };
}
