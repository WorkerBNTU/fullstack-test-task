import { AlertItem } from "../../entities/alert/types";
import { apiGetJson } from "./client";

export async function getAlerts(): Promise<AlertItem[]> {
  return apiGetJson<AlertItem[]>("/alerts", "Не удалось загрузить данные");
}
