import { FileItem } from "../../entities/file/types";
import { API_BASE_URL, apiDelete, apiGetJson, apiSendJson } from "./client";

export async function getFiles(): Promise<FileItem[]> {
  return apiGetJson<FileItem[]>("/files", "Не удалось загрузить данные");
}

export async function createFile(title: string, file: File): Promise<FileItem> {
  const formData = new FormData();
  formData.append("title", title);
  formData.append("file", file);

  return apiSendJson<FileItem>(
    "/files",
    { method: "POST", body: formData },
    "Не удалось загрузить файл",
  );
}

export async function updateFile(fileId: string, title: string): Promise<FileItem> {
  return apiSendJson<FileItem>(
    `/files/${fileId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    },
    "Не удалось обновить файл",
  );
}

export async function deleteFile(fileId: string): Promise<void> {
  await apiDelete(`/files/${fileId}`, "Не удалось удалить файл");
}

export function getDownloadUrl(fileId: string): string {
  return `${API_BASE_URL}/files/${fileId}/download`;
}
