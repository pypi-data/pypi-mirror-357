'use client';

import { CalibrationDataPoint } from '@/types/calibration';
import { useState, useMemo } from 'react';

interface DataTableProps {
  data: CalibrationDataPoint[];
}

export default function DataTable({ data }: DataTableProps) {
  // Find max epoch safely
  const maxEpoch = data.length > 0 ? data.reduce((max, item) => Math.max(max, item.epoch), 0) : 0;
  
  // Get unique epochs
  const allEpochs = Array.from(new Set(data.map(item => item.epoch))).sort((a, b) => a - b);
  
  const [sortField, setSortField] = useState<keyof CalibrationDataPoint | 'random'>('random');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filter, setFilter] = useState('');
  const [epochFilter, setEpochFilter] = useState(maxEpoch);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 50;

  const tableFilteredData = useMemo(() => {
    return data.filter(item => 
      item.epoch === epochFilter &&
      (item.target_name.toLowerCase().includes(filter.toLowerCase()))
    );
  }, [data, filter, epochFilter]);

  const sortedData = useMemo(() => {
    if (sortField === 'random') {
      // Stable shuffle based on data length to be consistent
      return [...tableFilteredData].sort(() => {
        const seed = tableFilteredData.length;
        return (seed * 9301 + 49297) % 233280 / 233280 - 0.5;
      });
    }
    
    return [...tableFilteredData].sort((a, b) => {
      const aVal = a[sortField as keyof CalibrationDataPoint];
      const bVal = b[sortField as keyof CalibrationDataPoint];
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      return sortDirection === 'asc' 
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr);
    });
  }, [tableFilteredData, sortField, sortDirection]);

  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return sortedData.slice(start, start + itemsPerPage);
  }, [sortedData, currentPage]);
  
  if (data.length === 0) {
    return (
      <div className="bg-white border border-gray-300 p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-bold text-gray-800">Detailed results</h2>
        <p className="text-gray-600 mt-4">No data available</p>
      </div>
    );
  }

  const totalPages = Math.ceil(sortedData.length / itemsPerPage);

  const handleSort = (field: keyof CalibrationDataPoint) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const SortButton = ({ field, children }: { field: keyof CalibrationDataPoint, children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="text-left hover:text-gray-900 transition-colors flex items-center"
    >
      {children}
      {sortField === field && (
        <span className="ml-1 text-blue-600">
          {sortDirection === 'asc' ? '↑' : '↓'}
        </span>
      )}
    </button>
  );

  const formatValue = (value: number) => {
    if (Math.abs(value) >= 1000000) {
      return (value / 1000000).toFixed(2) + 'M';
    } else if (Math.abs(value) >= 1000) {
      return (value / 1000).toFixed(1) + 'K';
    }
    return value.toFixed(2);
  };

  return (
    <div className="bg-white border border-gray-300 p-6 rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">Detailed results</h2>
        <div className="flex space-x-4">
          <select
            value={epochFilter}
            onChange={(e) => {
              setEpochFilter(parseInt(e.target.value));
              setCurrentPage(1);
            }}
            className="bg-white border border-gray-300 text-gray-900 px-3 py-2 rounded font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {allEpochs.sort((a, b) => b - a).map(epoch => (
              <option key={epoch} value={epoch}>Epoch {epoch}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Search target names..."
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-white border border-gray-300 text-gray-900 px-3 py-2 rounded font-mono text-sm w-64 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="text-gray-600 py-2 text-sm">
            {sortedData.length} entries
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm font-mono">
          <thead>
            <tr className="border-b border-gray-300 bg-gray-50">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">
                <SortButton field="target_name">Target name</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                <SortButton field="target">Target value</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                <SortButton field="estimate">Estimate</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                <SortButton field="error">Error</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                <SortButton field="abs_error">Abs error</SortButton>
              </th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">
                <SortButton field="rel_abs_error">Rel abs error %</SortButton>
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, i) => {
              const errorClass = row.rel_abs_error < 0.05 ? 'text-green-600' : 
                                row.rel_abs_error < 0.20 ? 'text-yellow-600' : 'text-red-600';
              return (
                <tr key={i} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="py-3 px-4 text-gray-900 max-w-64" title={row.target_name}>
                    <div 
                      className="overflow-x-auto whitespace-nowrap [&::-webkit-scrollbar]:hidden" 
                      style={{ 
                        scrollbarWidth: 'none', 
                        msOverflowStyle: 'none',
                      }}
                    >
                      {row.target_name}
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right text-gray-700 font-mono text-sm">
                    {formatValue(row.target)}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-700 font-mono text-sm">
                    {formatValue(row.estimate)}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-700 font-mono text-sm">
                    {row.error >= 0 ? '+' : ''}{formatValue(row.error)}
                  </td>
                  <td className="py-3 px-4 text-right text-gray-700 font-mono text-sm">
                    {formatValue(row.abs_error)}
                  </td>
                  <td className={`py-3 px-4 text-right font-mono text-sm font-semibold ${errorClass}`}>
                    {(row.rel_abs_error * 100).toFixed(2)}%
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex justify-between items-center mt-6">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:text-gray-500 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Previous
          </button>
          <div className="text-gray-600 font-mono text-sm">
            Page {currentPage} of {totalPages}
          </div>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-gray-300 disabled:text-gray-500 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}