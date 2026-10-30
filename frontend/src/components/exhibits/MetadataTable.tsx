import React, { useState } from 'react';
import { Search, FileText, ShieldAlert, Lock, Unlock, AlertCircle } from 'lucide-react';
import { MetadataResponse } from '../../types/api';

interface MetadataTableProps {
  metadata: MetadataResponse | null;
}

export const MetadataTable: React.FC<MetadataTableProps> = ({ metadata }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [revealSensitiveGPS, setRevealSensitiveGPS] = useState(false);

  if (!metadata || !metadata.categories || metadata.categories.length === 0) {
    return (
      <div className="bg-white dark:bg-[#111C2E] p-8 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] text-center text-sm text-[#657187] dark:text-[#94A3B8]">
        No container metadata fields found in this evidence file.
      </div>
    );
  }

  const categories = ['All', ...metadata.categories.map(c => c.name)];

  const filteredCategories = metadata.categories
    .filter(cat => selectedCategory === 'All' || cat.name === selectedCategory)
    .map(cat => ({
      ...cat,
      fields: cat.fields.filter(
        f =>
          f.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
          f.tag.toLowerCase().includes(searchTerm.toLowerCase()) ||
          (f.value && f.value.toLowerCase().includes(searchTerm.toLowerCase()))
      ),
    }))
    .filter(cat => cat.fields.length > 0);

  return (
    <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] overflow-hidden shadow-xs">
      {/* Header with Search and Filter */}
      <div className="px-5 py-4 border-b border-[#DCE2EA] dark:border-[#24344D] bg-[#F8FAFC] dark:bg-[#172B47]/50 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-[#C5A059]" />
            <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
              Container & EXIF / IPTC / TIFF Metadata Inspection
            </h3>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-[#172033] dark:text-slate-200">
              {metadata.raw_tag_count} Tags Inspected
            </span>
          </div>

          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-[#657187] absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search tag or value..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9 pr-3 py-1.5 text-xs rounded-lg border border-[#DCE2EA] dark:border-[#24344D] bg-white dark:bg-[#111C2E] text-[#172033] dark:text-white focus:outline-hidden focus:border-[#C5A059]"
            />
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2.5 py-1 rounded-full font-medium transition-colors shrink-0 ${
                selectedCategory === cat
                  ? 'bg-[#0F1E36] text-white dark:bg-[#C5A059] dark:text-slate-900'
                  : 'bg-white dark:bg-[#172B47] border border-[#DCE2EA] dark:border-[#24344D] text-[#657187] dark:text-[#94A3B8] hover:text-[#172033] dark:hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Forensic Doctrine Banner */}
      <div className="px-5 py-2.5 bg-amber-50/60 dark:bg-amber-950/20 border-b border-amber-200/60 dark:border-amber-900/30 text-xs text-amber-900 dark:text-amber-200 flex items-center gap-2">
        <AlertCircle className="w-4 h-4 shrink-0 text-amber-600 dark:text-amber-400" />
        <span>
          {metadata.doctrine_note}
        </span>
      </div>

      {/* Metadata Tables by Category */}
      <div className="divide-y divide-[#DCE2EA] dark:divide-[#24344D]">
        {filteredCategories.length === 0 ? (
          <div className="p-8 text-center text-xs text-[#657187] dark:text-[#94A3B8]">
            No metadata tags match the current search filter.
          </div>
        ) : (
          filteredCategories.map(cat => (
            <div key={cat.name} className="p-5">
              <h4 className="text-xs font-bold uppercase tracking-wider text-[#0F1E36] dark:text-[#C5A059] mb-3">
                {cat.name}
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-[#DCE2EA] dark:border-[#24344D] text-[#657187] dark:text-[#94A3B8]">
                      <th className="pb-2 font-semibold w-1/4">Field / Tag</th>
                      <th className="pb-2 font-semibold w-24">Status</th>
                      <th className="pb-2 font-semibold w-1/3">Recorded Value</th>
                      <th className="pb-2 font-semibold">Forensic Technical Note</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {cat.fields.map(f => {
                      const isProtectedGPS = f.is_sensitive;
                      return (
                        <tr
                          key={f.tag}
                          className={`hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors ${
                            f.is_software_trace ? 'bg-amber-50/20 dark:bg-amber-950/10' : ''
                          }`}
                        >
                          <td className="py-2.5 pr-3 font-medium text-[#172033] dark:text-white">
                            <div>{f.label}</div>
                            <div className="text-[10px] text-[#657187] dark:text-[#94A3B8] font-mono">
                              {f.tag}
                            </div>
                          </td>

                          <td className="py-2.5 pr-3">
                            <span
                              className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${
                                f.status === 'Present'
                                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                                  : f.status === 'Missing'
                                  ? 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400'
                                  : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                              }`}
                            >
                              {f.status}
                            </span>
                          </td>

                          <td className="py-2.5 pr-3 font-mono text-[#172033] dark:text-slate-200">
                            {isProtectedGPS ? (
                              <div className="flex items-center gap-2">
                                {revealSensitiveGPS ? (
                                  <span className="text-rose-600 dark:text-rose-400 font-semibold">
                                    {f.value || 'Not Available'}
                                  </span>
                                ) : (
                                  <span className="text-[#657187] dark:text-[#94A3B8] italic flex items-center gap-1">
                                    <Lock className="w-3.5 h-3.5 text-amber-500" />
                                    [PROTECTED SENSITIVE DATA]
                                  </span>
                                )}
                                <button
                                  type="button"
                                  onClick={() => setRevealSensitiveGPS(!revealSensitiveGPS)}
                                  className="text-[10px] text-[#C5A059] underline hover:text-[#0F1E36] dark:hover:text-white"
                                >
                                  {revealSensitiveGPS ? 'Hide' : 'Reveal (Authorized)'}
                                </button>
                              </div>
                            ) : (
                              <span>{f.value || <span className="text-slate-400 italic">None</span>}</span>
                            )}
                          </td>

                          <td className="py-2.5 text-[#657187] dark:text-[#94A3B8] leading-relaxed">
                            {f.notes}
                            {f.is_software_trace && (
                              <span className="block text-amber-600 dark:text-amber-400 font-semibold text-[10px] mt-0.5">
                                ⚠ Software Trace: Editing software signature detected. Observation only, not proof of tampering.
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
