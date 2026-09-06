import { useState, useEffect, useMemo } from "react";
import { api } from "../services/api";
import { FALLBACK_CATALOG, cmsTemplateToCatalog } from "./TemplateCatalog.constants";
import { TemplateCatalogContext } from "./TemplateCatalogContext.context";

export function TemplateCatalogProvider({ children }) {
  const [apiCatalog, setApiCatalog] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await api.templates.getPublished();
        // Normalize: handle both { items: [...] } and bare [...]
        const items = Array.isArray(res) ? res : (res?.items || res?.data?.items || []);
        const catalog = {};
        for (const t of items) {
          catalog[t.id] = cmsTemplateToCatalog(t);
        }
        if (!cancelled) setApiCatalog(catalog);
      } catch {
        // API unavailable — use fallback
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  // Merge: API catalog takes precedence over fallback
  const catalog = useMemo(() => {
    if (apiCatalog) {
      return { ...FALLBACK_CATALOG, ...apiCatalog };
    }
    return FALLBACK_CATALOG;
  }, [apiCatalog]);

  return (
    <TemplateCatalogContext.Provider value={{ catalog, loading }}>
      {children}
    </TemplateCatalogContext.Provider>
  );
}
