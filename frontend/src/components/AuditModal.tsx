import { useEffect, useState } from 'react';

interface AuditModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface AuditData {
  rag_engine: { status: string; total_documents: number; last_news_indexed: string };
  ml_engine: { status: string; model_last_trained: string; sources_used: string[] };
  ingestion_engine: { status: string; last_odds_fetch: string; last_xg_fetch: string; normalization_warnings: string[] };
}

export default function AuditModal({ isOpen, onClose }: AuditModalProps) {
  const [data, setData] = useState<AuditData | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetch('http://localhost:8000/api/health/audit')
        .then(res => res.json())
        .then(setData)
        .catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-[#0b203d] border border-[#3b4861] rounded-xl w-[500px] shadow-2xl overflow-hidden">
        <div className="flex justify-between items-center p-4 border-b border-[#3b4861]">
          <h2 className="text-[#6bff8f] font-['Space_Grotesk'] font-bold flex items-center gap-2">
            <span className="material-symbols-outlined">analytics</span>
            Salud del Sistema y Auditoría
          </h2>
          <button onClick={onClose} className="text-[#9eabc8] hover:text-white">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <div className="p-6 space-y-6">
          {!data ? <p className="text-white text-center">Cargando datos de auditoría...</p> : (
            <>
              {/* ML Engine */}
              <div>
                <h3 className="text-xs font-bold text-[#9eabc8] uppercase mb-2">Motor de Machine Learning</h3>
                <div className="bg-[#010e24] p-3 rounded border border-white/5 space-y-1">
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Estado:</span> {data.ml_engine.status}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Último Entrenamiento:</span> {data.ml_engine.model_last_trained}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Fuentes:</span> {data.ml_engine.sources_used.join(", ")}</p>
                </div>
              </div>
              
              {/* RAG Engine */}
              <div>
                <h3 className="text-xs font-bold text-[#9eabc8] uppercase mb-2">Motor de Contexto RAG</h3>
                <div className="bg-[#010e24] p-3 rounded border border-white/5 space-y-1">
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Estado:</span> {data.rag_engine.status}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Fragmentos Indexados:</span> {data.rag_engine.total_documents}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Última Noticia:</span> {data.rag_engine.last_news_indexed}</p>
                </div>
              </div>

              {/* Ingestion Engine */}
              <div>
                <h3 className="text-xs font-bold text-[#9eabc8] uppercase mb-2">Motor de Ingesta</h3>
                <div className="bg-[#010e24] p-3 rounded border border-white/5 space-y-1">
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Estado:</span> {data.ingestion_engine.status}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Datos de Cuotas:</span> {data.ingestion_engine.last_odds_fetch}</p>
                  <p className="text-xs text-white"><span className="text-[#47c4ff]">Datos xG:</span> {data.ingestion_engine.last_xg_fetch}</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}