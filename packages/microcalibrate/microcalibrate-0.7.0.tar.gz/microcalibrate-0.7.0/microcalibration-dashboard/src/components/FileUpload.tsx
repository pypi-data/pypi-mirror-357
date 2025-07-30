'use client';

import { useState } from 'react';
import { Upload, File as FileIcon, Link, Database } from 'lucide-react';

interface FileUploadProps {
  onFileLoad: (content: string, filename: string) => void;
  onViewDashboard: () => void;
}

export default function FileUpload({ onFileLoad, onViewDashboard }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [activeTab, setActiveTab] = useState<'drop' | 'url' | 'sample'>('drop');
  const [loadedFile, setLoadedFile] = useState<string>('');
  const [error, setError] = useState<string>('');

  async function processFile(file: globalThis.File) {
    setIsLoading(true);
    try {
      const content = await file.text();

      // Basic CSV validation
      if (!content.trim()) {
        throw new Error('The file appears to be empty or contains only whitespace.');
      }

      // Check for basic CSV structure
      const lines = content.trim().split('\n');
      if (lines.length < 2) {
        throw new Error('The file must contain at least a header row and one data row.');
      }

      // Check for required columns
      const headerLine = lines[0].toLowerCase();
      const requiredColumns = ['epoch', 'loss', 'target_name', 'target', 'estimate', 'error'];
      const missingColumns = requiredColumns.filter(col => !headerLine.includes(col));

      if (missingColumns.length > 0) {
        throw new Error(
          `Missing required columns: ${missingColumns.join(', ')}. Please ensure your CSV has the correct format.`
        );
      }

      onFileLoad(content, file.name);
      setLoadedFile(file.name);
    } catch (err) {
      setError(
        err instanceof Error
          ? `File processing error: ${err.message}`
          : 'Failed to read file. Please ensure it is a valid CSV file and try again.'
      );
    } finally {
      setIsLoading(false);
    }
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(true);
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragOver(false);
    setError('');

    const files = Array.from(e.dataTransfer.files);

    if (files.length === 0) {
      setError('No files were dropped. Please try again.');
      return;
    }

    if (files.length > 1) {
      setError('Please drop only one file at a time. Multiple files are not supported.');
      return;
    }

    const file = files[0];

    if (!file.name.endsWith('.csv')) {
      setError(`Invalid file type: "${file.name}". Please drop a CSV file (.csv extension required).`);
      return;
    }

    if (file.size === 0) {
      setError('The dropped file appears to be empty. Please check your file and try again.');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      // 50 MB limit
      setError('File is too large (over 50 MB). Please use a smaller CSV file.');
      return;
    }

    processFile(file);
  }

  function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    setError('');

    if (!file) {
      setError('No file was selected. Please try again.');
      return;
    }

    if (!file.name.endsWith('.csv')) {
      setError(`Invalid file type: "${file.name}". Please select a CSV file (.csv extension required).`);
      return;
    }

    if (file.size === 0) {
      setError('The selected file appears to be empty. Please check your file and try again.');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File is too large (over 50 MB). Please select a smaller CSV file.');
      return;
    }

    processFile(file);
  }

  async function handleUrlLoad() {
    if (!urlInput.trim()) {
      setError('Please enter a URL to load a CSV file.');
      return;
    }

    let url: URL;
    try {
      url = new URL(urlInput.trim());
    } catch {
      setError('Invalid URL format. Please enter a valid URL (e.g., https://example.com/data.csv).');
      return;
    }

    if (!url.pathname.toLowerCase().endsWith('.csv') && !urlInput.toLowerCase().includes('csv')) {
      setError('URL should point to a CSV file. Please ensure the URL ends with .csv or contains CSV data.');
      return;
    }

    if (url.protocol !== 'https:' && url.protocol !== 'http:') {
      setError('Only HTTP and HTTPS URLs are supported. Please use a web URL.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30_000); // 30 s timeout

      const response = await fetch(urlInput.trim(), {
        signal: controller.signal,
        headers: { Accept: 'text/csv, text/plain, */*' }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const status = response.status;
        const map: Record<number, string> = {
          404: 'File not found (404). Please check the URL and try again.',
          403: 'Access forbidden (403). The server denied access to this file.',
          401: 'Authentication required (401). This file requires login credentials.',
          500: 'Server error (500). The remote server encountered an error.',
          503: 'Service unavailable (503). The server is temporarily unavailable.'
        };
        throw new Error(map[status] || `HTTP error ${status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type') || '';
      if (
        !contentType.includes('text/csv') &&
        !contentType.includes('text/plain') &&
        !contentType.includes('application/csv')
      ) {
        setError(`Warning: Server returned content type "${contentType}". This may not be a CSV file.`);
      }

      const content = await response.text();

      if (!content.trim()) {
        throw new Error('The downloaded file appears to be empty.');
      }

      const lines = content.trim().split('\n');
      if (lines.length < 2) {
        throw new Error('The downloaded file must contain at least a header row and one data row.');
      }

      const headerLine = lines[0].toLowerCase();
      const requiredColumns = ['epoch', 'loss', 'target_name', 'target', 'estimate', 'error'];
      const missingColumns = requiredColumns.filter(col => !headerLine.includes(col));

      if (missingColumns.length > 0) {
        throw new Error(
          `Downloaded file is missing required columns: ${missingColumns.join(
            ', '
          )}. Please ensure the URL points to a valid calibration CSV file.`
        );
      }

      const filename = url.pathname.split('/').pop() || 'remote-file.csv';
      onFileLoad(content, filename);
      setLoadedFile(filename);
    } catch (err) {
      if (err instanceof Error) {
        if (err.name === 'AbortError') {
          setError('Request timed out after 30 s. Please check your connection and try again.');
        } else if (err.message.includes('Failed to fetch')) {
          setError('Network error: Unable to reach the URL. Please check the address and your connection.');
        } else {
          setError(`Failed to load from URL: ${err.message}`);
        }
      } else {
        setError('Unknown error occurred while loading the URL. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSampleLoad() {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/sample.csv');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const content = await response.text();
      onFileLoad(content, 'sample.csv');
      setLoadedFile('sample.csv');
    } catch (err) {
      setError(`Failed to load sample data: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Load calibration data</h2>
        <p className="text-gray-600">Choose how you would like to load your CSV file</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {loadedFile && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-md p-3">
          <p className="text-sm text-green-700">Successfully loaded: {loadedFile}</p>
        </div>
      )}

      {/* Tab navigation */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('drop')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'drop'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Upload className="w-4 h-4 inline mr-2" />
          Drop File
        </button>
        <button
          onClick={() => setActiveTab('url')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'url'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Link className="w-4 h-4 inline mr-2" />
          URL
        </button>
        <button
          onClick={() => setActiveTab('sample')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'sample'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Database className="w-4 h-4 inline mr-2" />
          Sample data
        </button>
      </div>

      {/* Tab content */}
      {activeTab === 'drop' && (
        <div className="space-y-4">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <FileIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">Drop your CSV file here</p>
            <p className="text-gray-600 mb-4">or click to browse files</p>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileInput}
              className="hidden"
              id="file-input"
            />
            <label
              htmlFor="file-input"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 cursor-pointer"
            >
              Choose file
            </label>
          </div>
        </div>
      )}

      {activeTab === 'url' && (
        <div className="space-y-4">
          <div>
            <label htmlFor="url-input" className="block text-sm font-medium text-gray-700 mb-2">
              CSV file URL
            </label>
            <div className="flex space-x-2">
              <input
                id="url-input"
                type="url"
                value={urlInput}
                onChange={e => setUrlInput(e.target.value)}
                placeholder="https://example.com/data.csv"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleUrlLoad}
                disabled={isLoading || !urlInput.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Loading...' : 'Load'}
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-2">Enter a direct URL to a CSV file accessible via HTTP/HTTPS</p>
          </div>
        </div>
      )}

      {activeTab === 'sample' && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              <Database className="w-6 h-6 text-blue-600 mt-1" />
              <div className="flex-1">
                <h3 className="text-lg font-medium text-blue-900 mb-2">Load sample calibration data</h3>
                <p className="text-blue-700 mb-4">
                  Try the dashboard with sample calibration data showing income targets by age group over 500+ epochs.
                </p>
                <ul className="text-sm text-blue-600 mb-4 space-y-1">
                  <li>• Contains 100+ data points with loss convergence</li>
                  <li>• Shows calibration for income_aged_20_30 and income_aged_40_50 targets</li>
                  <li>• Demonstrates error reduction over training epochs</li>
                </ul>
                <button
                  onClick={handleSampleLoad}
                  disabled={isLoading}
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Loading Sample...' : 'Load Sample Data'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* View Dashboard Button */}
      {loadedFile && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <button
            onClick={onViewDashboard}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-md transition-colors"
          >
            View Dashboard
          </button>
        </div>
      )}

      {/* Global loading indicator */}
      {isLoading && (
        <div className="mt-4 text-center">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
          <p className="text-sm text-gray-600 mt-2">Loading file...</p>
        </div>
      )}
    </div>
  );
}
