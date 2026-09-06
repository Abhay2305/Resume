import { useContext } from "react";
import { TemplateCatalogContext } from "../context/TemplateCatalogContext.context";
import { FALLBACK_CATALOG } from "../context/TemplateCatalog.constants";

export function useTemplateCatalog() {
  const ctx = useContext(TemplateCatalogContext);
  if (!ctx) {
    return { catalog: FALLBACK_CATALOG, loading: false };
  }
  return ctx;
}
