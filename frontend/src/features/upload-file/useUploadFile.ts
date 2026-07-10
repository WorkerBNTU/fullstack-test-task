import { FormEvent, useState } from "react";

import { createFile } from "../../shared/api/files";

export function useUploadFile(onUploaded: () => Promise<void>) {
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  function openModal() {
    setShowModal(true);
  }

  function closeModal() {
    setShowModal(false);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      setErrorMessage("Укажите название и выберите файл");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await createFile(title.trim(), selectedFile);
      setShowModal(false);
      setTitle("");
      setSelectedFile(null);
      await onUploaded();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsSubmitting(false);
    }
  }

  return {
    showModal,
    openModal,
    closeModal,
    title,
    setTitle,
    selectedFile,
    setSelectedFile,
    isSubmitting,
    errorMessage,
    handleSubmit,
  };
}
