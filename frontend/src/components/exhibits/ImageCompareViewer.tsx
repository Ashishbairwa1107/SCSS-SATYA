import React, { useState } from 'react';
import { Eye, Layers, ZoomIn, ZoomOut, RotateCcw, Download, Info } from 'lucide-react';
import { ELAResponse, Evidence } from '../../types/api';
import { api } from '../../services/api';

interface ImageCompareViewerProps {
  evidence: Evidence;
  ela: ELAResponse | null;
}

export const ImageCompareViewer: React.FC<ImageCompareViewerProps> = ({ evidence, ela }) => {
  const [opacity, setOpacity] = useState<number>(75);
  const [viewMode, setViewMode] = useState<'blend' | 'side-by-side' | 'original' | 'ela-only'>('blend');
  const [activeArtifact, setActiveArtifact] = useState<'heatmap' | 'grayscale'>('heatmap');
  const [zoomLevel, setZoomLevel] = useState<number>(100);

  const originalUrl = api.resolveAssetUrl(api.getOriginalEvidenceUrl(evidence.id));
  const rawArtifactUrl = activeArtifact === 'heatmap' ? ela?.artifact_url : ela?.grayscale_artifact_url;
  const elaArtifactUrl = api.resolveAssetUrl(rawArtifactUrl);

  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 25, 300));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 25, 50));
  const handleResetZoom = () => setZoomLevel(100);

  return (
    <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] overflow-hidden shadow-xs">
      {/* Control Bar */}
      <div className="px-5 py-3.5 border-b border-[#DCE2EA] dark:border-[#24344D] flex flex-wrap items-center justify-between gap-4 bg-[#F8FAFC] dark:bg-[#172B47]/50">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-[#C5A059]" />
          <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
            Visual Examination & Error Level Analysis (ELA)
          </h3>
          {ela?.format_supported && (
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-[#C5A059]/10 text-[#C5A059] border border-[#C5A059]/30">
              Q={ela.quality} | {ela.scale}x
            </span>
          )}
        </div>

        {/* View Mode Selectors */}
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-lg border border-[#DCE2EA] dark:border-[#24344D] p-0.5 bg-white dark:bg-[#111C2E] text-xs">
            <button
              onClick={() => setViewMode('blend')}
              disabled={!ela?.format_supported}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                viewMode === 'blend'
                  ? 'bg-[#0F1E36] text-white'
                  : 'text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white disabled:opacity-40'
              }`}
            >
              Overlay Blend
            </button>
            <button
              onClick={() => setViewMode('side-by-side')}
              disabled={!ela?.format_supported}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                viewMode === 'side-by-side'
                  ? 'bg-[#0F1E36] text-white'
                  : 'text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white disabled:opacity-40'
              }`}
            >
              Side-by-Side
            </button>
            <button
              onClick={() => setViewMode('original')}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                viewMode === 'original'
                  ? 'bg-[#0F1E36] text-white'
                  : 'text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
              }`}
            >
              Original Only
            </button>
            <button
              onClick={() => setViewMode('ela-only')}
              disabled={!ela?.format_supported}
              className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
                viewMode === 'ela-only'
                  ? 'bg-[#0F1E36] text-white'
                  : 'text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white disabled:opacity-40'
              }`}
            >
              ELA Only
            </button>
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center gap-1 border-l border-[#DCE2EA] dark:border-[#24344D] pl-2">
            <button
              onClick={handleZoomOut}
              className="p-1.5 rounded text-[#657187] hover:text-[#172033] dark:text-[#94A3B8] dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono w-10 text-center text-[#657187] dark:text-[#94A3B8]">
              {zoomLevel}%
            </span>
            <button
              onClick={handleZoomIn}
              className="p-1.5 rounded text-[#657187] hover:text-[#172033] dark:text-[#94A3B8] dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={handleResetZoom}
              className="p-1.5 rounded text-[#657187] hover:text-[#172033] dark:text-[#94A3B8] dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
              title="Reset View"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Sub-bar for Opacity and Artifact Selection */}
      {ela?.format_supported && viewMode === 'blend' && (
        <div className="px-5 py-2.5 bg-slate-50 dark:bg-[#152238] border-b border-[#DCE2EA] dark:border-[#24344D] flex flex-wrap items-center justify-between text-xs gap-4">
          <div className="flex items-center gap-3">
            <span className="font-medium text-[#657187] dark:text-[#94A3B8]">
              ELA Layer Opacity:
            </span>
            <input
              type="range"
              min="0"
              max="100"
              value={opacity}
              onChange={e => setOpacity(Number(e.target.value))}
              className="w-36 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-[#C5A059]"
            />
            <span className="font-mono text-[#0F1E36] dark:text-[#C5A059] font-semibold w-8">
              {opacity}%
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-medium text-[#657187] dark:text-[#94A3B8]">Colormap:</span>
            <button
              onClick={() => setActiveArtifact('heatmap')}
              className={`px-2 py-0.5 rounded text-xs font-medium border ${
                activeArtifact === 'heatmap'
                  ? 'bg-[#C5A059] text-white border-[#C5A059]'
                  : 'border-[#DCE2EA] dark:border-[#24344D] text-[#657187] dark:text-[#94A3B8]'
              }`}
            >
              Thermal Inferno
            </button>
            <button
              onClick={() => setActiveArtifact('grayscale')}
              className={`px-2 py-0.5 rounded text-xs font-medium border ${
                activeArtifact === 'grayscale'
                  ? 'bg-[#C5A059] text-white border-[#C5A059]'
                  : 'border-[#DCE2EA] dark:border-[#24344D] text-[#657187] dark:text-[#94A3B8]'
              }`}
            >
              High-Contrast Grayscale
            </button>
          </div>
        </div>
      )}

      {/* Exhibit Canvas Area */}
      <div className="p-6 bg-slate-900/10 dark:bg-black/30 flex items-center justify-center min-h-[420px] overflow-auto">
        {!ela?.format_supported && (
          <div className="max-w-md p-5 bg-white dark:bg-[#111C2E] border border-amber-300 dark:border-amber-700/60 rounded-xl text-center space-y-3">
            <div className="w-10 h-10 rounded-full bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 mx-auto flex items-center justify-center">
              <Info className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-[#172033] dark:text-white">
              JPEG ELA Not Applicable (Lossless Format)
            </h4>
            <p className="text-xs text-[#657187] dark:text-[#94A3B8] leading-relaxed">
              {ela?.notes || 'Error Level Analysis models DCT lossy recompression error, which is scientifically invalid for lossless formats like PNG/TIFF.'}
            </p>
            <div className="pt-2">
              <img
                src={originalUrl}
                alt="Original Evidence"
                style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'center' }}
                className="max-h-[320px] mx-auto rounded border border-[#DCE2EA] dark:border-[#24344D] transition-transform"
              />
            </div>
          </div>
        )}

        {ela?.format_supported && (
          <div
            style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'center' }}
            className="transition-transform duration-150 flex items-center justify-center"
          >
            {viewMode === 'blend' && (
              <div className="relative inline-block border border-slate-700 rounded overflow-hidden shadow-lg bg-black">
                <img
                  src={originalUrl}
                  alt="Original Evidence Layer"
                  className="max-h-[500px] w-auto block"
                />
                {elaArtifactUrl && (
                  <img
                    src={elaArtifactUrl}
                    alt="ELA Anomaly Heatmap Layer"
                    style={{ opacity: opacity / 100 }}
                    className="absolute inset-0 w-full h-full object-fill pointer-events-none mix-blend-screen"
                  />
                )}
              </div>
            )}

            {viewMode === 'side-by-side' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-5xl">
                <div className="border border-slate-700 rounded overflow-hidden bg-black text-center">
                  <div className="bg-[#172B47] text-slate-200 text-xs py-1 px-3 font-semibold border-b border-slate-700">
                    Original Evidence
                  </div>
                  <img src={originalUrl} alt="Original" className="max-h-[380px] w-auto mx-auto" />
                </div>
                <div className="border border-slate-700 rounded overflow-hidden bg-black text-center">
                  <div className="bg-[#172B47] text-slate-200 text-xs py-1 px-3 font-semibold border-b border-slate-700">
                    ELA Recompression Heatmap (Q={ela.quality})
                  </div>
                  {elaArtifactUrl && (
                    <img src={elaArtifactUrl} alt="ELA Heatmap" className="max-h-[380px] w-auto mx-auto" />
                  )}
                </div>
              </div>
            )}

            {viewMode === 'original' && (
              <div className="border border-slate-700 rounded overflow-hidden bg-black">
                <img src={originalUrl} alt="Original" className="max-h-[500px] w-auto" />
              </div>
            )}

            {viewMode === 'ela-only' && (
              <div className="border border-slate-700 rounded overflow-hidden bg-black">
                {elaArtifactUrl && (
                  <img src={elaArtifactUrl} alt="ELA Heatmap Only" className="max-h-[500px] w-auto" />
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Info & Download Actions */}
      <div className="px-5 py-3 border-t border-[#DCE2EA] dark:border-[#24344D] flex flex-wrap items-center justify-between text-xs text-[#657187] dark:text-[#94A3B8] bg-[#F8FAFC] dark:bg-[#172B47]/30 gap-3">
        <div>
          <span className="font-semibold text-[#172033] dark:text-white">Evidence: </span>
          <span className="font-mono">{evidence.original_filename}</span> ({evidence.width} × {evidence.height} px, {evidence.detected_format})
        </div>

        <div className="flex items-center gap-3">
          <a
            href={originalUrl}
            download={evidence.original_filename}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] hover:text-[#172033] dark:hover:text-white transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-[#C5A059]" />
            <span>Download Original</span>
          </a>

          {ela?.artifact_url && (
            <a
              href={ela.artifact_url}
              download={`ELA_Exhibit_${evidence.id.slice(0, 8)}.png`}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] hover:text-[#172033] dark:hover:text-white transition-colors"
            >
              <Download className="w-3.5 h-3.5 text-[#C5A059]" />
              <span>Download ELA Heatmap</span>
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
