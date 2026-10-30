import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
} from 'recharts';
import { ImageStatisticsResponse } from '../../types/api';
import { BarChart3, Activity, Waves } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

interface RGBDistributionChartProps {
  stats: ImageStatisticsResponse | null;
}

export const RGBDistributionChart: React.FC<RGBDistributionChartProps> = ({ stats }) => {
  const { theme } = useTheme();

  if (!stats) {
    return (
      <div className="bg-white dark:bg-[#111C2E] p-6 rounded-xl border border-[#DCE2EA] dark:border-[#24344D] text-center text-xs text-[#657187] dark:text-[#94A3B8]">
        No radiometric color statistics available.
      </div>
    );
  }

  const { rgb_statistics, spatial_noise, dimensions } = stats;
  const isDark = theme === 'dark';

  return (
    <div className="bg-white dark:bg-[#111C2E] rounded-xl border border-[#DCE2EA] dark:border-[#24344D] overflow-hidden shadow-xs">
      <div className="px-5 py-3.5 border-b border-[#DCE2EA] dark:border-[#24344D] flex items-center justify-between bg-[#F8FAFC] dark:bg-[#172B47]/50">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-[#C5A059]" />
          <h3 className="text-sm font-semibold text-[#172033] dark:text-white">
            Color Channel Radiometry & Spatial Noise Distribution
          </h3>
        </div>
        <span className="text-xs text-[#657187] dark:text-[#94A3B8] font-mono">
          {rgb_statistics.total_pixels_sampled.toLocaleString()} Pixels (100% Census)
        </span>
      </div>

      <div className="p-5 space-y-6">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Red Channel */}
          <div className="p-3.5 rounded-lg border border-rose-200/60 dark:border-rose-900/40 bg-rose-50/30 dark:bg-rose-950/20">
            <div className="flex items-center justify-between text-xs font-semibold text-rose-700 dark:text-rose-400">
              <span>Red Channel (R)</span>
              <span className="font-mono">μ = {rgb_statistics.red.mean}</span>
            </div>
            <div className="mt-2 text-xs text-[#657187] dark:text-[#94A3B8] space-y-0.5">
              <div className="flex justify-between">
                <span>Std Dev (σ):</span>
                <span className="font-mono font-medium text-[#172033] dark:text-white">{rgb_statistics.red.std_dev}</span>
              </div>
              <div className="flex justify-between">
                <span>Dynamic Range:</span>
                <span className="font-mono font-medium text-[#172033] dark:text-white">{rgb_statistics.red.min} - {rgb_statistics.red.max}</span>
              </div>
            </div>
          </div>

          {/* Green Channel */}
          <div className="p-3.5 rounded-lg border border-emerald-200/60 dark:border-emerald-900/40 bg-emerald-50/30 dark:bg-emerald-950/20">
            <div className="flex items-center justify-between text-xs font-semibold text-emerald-700 dark:text-emerald-400">
              <span>Green Channel (G)</span>
              <span className="font-mono">μ = {rgb_statistics.green.mean}</span>
            </div>
            <div className="mt-2 text-xs text-[#657187] dark:text-[#94A3B8] space-y-0.5">
              <div className="flex justify-between">
                <span>Std Dev (σ):</span>
                <span className="font-mono font-medium text-[#172033] dark:text-white">{rgb_statistics.green.std_dev}</span>
              </div>
              <div className="flex justify-between">
                <span>Dynamic Range:</span>
                <span className="font-mono font-medium text-[#172033] dark:text-white">{rgb_statistics.green.min} - {rgb_statistics.green.max}</span>
              </div>
            </div>
          </div>

          {/* Blue Channel */}
          <div className="p-3.5 rounded-lg border border-blue-200/60 dark:border-blue-900/40 bg-blue-50/30 dark:bg-blue-950/20">
            <div className="flex items-center justify-between text-xs font-semibold text-blue-700 dark:text-blue-400">
              <span>Blue Channel (B)</span>
              <span className="font-mono">μ = {rgb_statistics.blue.mean}</span>
            </div>
            <div className="mt-2 text-xs text-[#657187] dark:text-[#94A3B8] space-y-0.5">
              <div className="flex justify-between">
                <span>Std Dev (σ):</span>
                <span className="font-mono font-medium text-[#172033] dark:text-white">{rgb_statistics.blue.std_dev}</span>
              </div>
              <div className="flex justify-between">
                <span>Dynamic Range:</span>
                <span className="font-mono font-medium text-[#172033] dark:text-white">{rgb_statistics.blue.min} - {rgb_statistics.blue.max}</span>
              </div>
            </div>
          </div>
        </div>

        {/* 32-Bin Radiometric Histogram */}
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-[#657187] dark:text-[#94A3B8] mb-3 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-[#C5A059]" />
            <span>Full-Frame 32-Bin RGB Intensity Histogram</span>
          </h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={rgb_statistics.histogram}
                margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke={isDark ? '#24344D' : '#E2E8F0'}
                  vertical={false}
                />
                <XAxis
                  dataKey="range"
                  stroke={isDark ? '#64748B' : '#94A3B8'}
                  fontSize={10}
                  tickLine={false}
                  interval={3}
                />
                <YAxis
                  stroke={isDark ? '#64748B' : '#94A3B8'}
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#111C2E' : '#FFFFFF',
                    borderColor: isDark ? '#24344D' : '#DCE2EA',
                    borderRadius: '8px',
                    fontSize: '11px',
                    color: isDark ? '#F1F5F9' : '#172033',
                  }}
                />
                <Legend
                  wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                />
                <Bar dataKey="r" name="Red" fill="#EF4444" opacity={0.8} />
                <Bar dataKey="g" name="Green" fill="#10B981" opacity={0.8} />
                <Bar dataKey="b" name="Blue" fill="#3B82F6" opacity={0.8} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Spatial Noise & Sharpness Measurements */}
        <div className="pt-2 border-t border-[#DCE2EA] dark:border-[#24344D]">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-[#657187] dark:text-[#94A3B8] mb-3 flex items-center gap-1.5">
            <Waves className="w-3.5 h-3.5 text-[#C5A059]" />
            <span>High-Frequency Spatial Texture & Focus Metrics</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-[#F8FAFC] dark:bg-[#152238] border border-[#DCE2EA] dark:border-[#24344D]">
              <span className="text-[#657187] dark:text-[#94A3B8] font-medium block">
                Laplacian Edge Variance:
              </span>
              <span className="text-base font-bold font-mono text-[#172033] dark:text-white mt-1 block">
                {spatial_noise.laplacian_variance}
              </span>
              <p className="text-[10px] text-[#657187] dark:text-[#94A3B8] mt-1">
                Spatial edge frequency & focus depth measure.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-[#F8FAFC] dark:bg-[#152238] border border-[#DCE2EA] dark:border-[#24344D]">
              <span className="text-[#657187] dark:text-[#94A3B8] font-medium block">
                Sobel Gradient Mean:
              </span>
              <span className="text-base font-bold font-mono text-[#172033] dark:text-white mt-1 block">
                {spatial_noise.sobel_gradient_mean}
              </span>
              <p className="text-[10px] text-[#657187] dark:text-[#94A3B8] mt-1">
                Directional spatial luminance transition rate.
              </p>
            </div>

            <div className="p-3 rounded-lg bg-[#F8FAFC] dark:bg-[#152238] border border-[#DCE2EA] dark:border-[#24344D]">
              <span className="text-[#657187] dark:text-[#94A3B8] font-medium block">
                Noise Residual Sigma (σ):
              </span>
              <span className="text-base font-bold font-mono text-[#172033] dark:text-white mt-1 block">
                {spatial_noise.high_freq_noise_sigma}
              </span>
              <p className="text-[10px] text-[#657187] dark:text-[#94A3B8] mt-1">
                Median-filter high-frequency residual estimator.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
