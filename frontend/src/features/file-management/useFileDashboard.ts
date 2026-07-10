import { useCallback, useEffect, useState } from "react";

import { AlertItem } from "../../entities/alert/types";
import { FileItem } from "../../entities/file/types";
import { getAlerts } from "../../shared/api/alerts";
import { getFiles } from "../../shared/api/files";

export function useFileDashboard() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [filesData, alertsData] = await Promise.all([getFiles(), getAlerts()]);
      setFiles(filesData);
      setAlerts(alertsData);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  return { files, alerts, isLoading, errorMessage, setErrorMessage, refresh: loadData };
}
