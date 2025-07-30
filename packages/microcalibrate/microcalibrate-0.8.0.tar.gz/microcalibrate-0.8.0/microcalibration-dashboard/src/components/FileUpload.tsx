'use client';

import { useState } from 'react';
import { Upload, File as FileIcon, Link, Database, GitBranch } from 'lucide-react';
import JSZip from 'jszip';

interface FileUploadProps {
  onFileLoad: (content: string, filename: string) => void;
  onViewDashboard: () => void;
}

interface GitHubCommit {
  sha: string;
  commit: {
    message: string;
    author: {
      date: string;
    };
  };
}

interface GitHubBranch {
  name: string;
  commit: {
    sha: string;
  };
}

interface GitHubArtifact {
  id: number;
  name: string;
  archive_download_url: string;
  size_in_bytes: number;
  created_at: string;
}

export default function FileUpload({ onFileLoad, onViewDashboard }: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [activeTab, setActiveTab] = useState<'drop' | 'url' | 'sample' | 'github'>('drop');
  const [loadedFile, setLoadedFile] = useState<string>('');
  const [error, setError] = useState<string>('');

  // GitHub-specific state
  const [githubRepo, setGithubRepo] = useState('');
  const [githubBranches, setGithubBranches] = useState<GitHubBranch[]>([]);
  const [selectedBranch, setSelectedBranch] = useState('');
  const [githubCommits, setGithubCommits] = useState<GitHubCommit[]>([]);
  const [selectedCommit, setSelectedCommit] = useState('');
  const [availableArtifacts, setAvailableArtifacts] = useState<GitHubArtifact[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState('');
  const [isLoadingGithubData, setIsLoadingGithubData] = useState(false);

  function sampleEpochs(csvContent: string, maxEpochs = 20): { content: string; wasSampled: boolean; originalEpochs: number; sampledEpochs: number } {
    const lines = csvContent.trim().split('\n');
    const header = lines[0];
    const dataLines = lines.slice(1);
    
    if (dataLines.length === 0) return { content: csvContent, wasSampled: false, originalEpochs: 0, sampledEpochs: 0 };
    
    // Parse epoch column index
    const headerCols = header.toLowerCase().split(',');
    const epochIndex = headerCols.findIndex(col => col.trim() === 'epoch');
    
    if (epochIndex === -1) return { content: csvContent, wasSampled: false, originalEpochs: 0, sampledEpochs: 0 };
    
    // Group data by epoch
    const epochData = new Map<number, string[]>();
    dataLines.forEach(line => {
      const cols = line.split(',');
      const epoch = parseInt(cols[epochIndex]);
      if (!isNaN(epoch)) {
        if (!epochData.has(epoch)) {
          epochData.set(epoch, []);
        }
        epochData.get(epoch)!.push(line);
      }
    });
    
    // Get sorted unique epochs
    const allEpochs = Array.from(epochData.keys()).sort((a, b) => a - b);
    const originalEpochCount = allEpochs.length;
    
    if (allEpochs.length <= maxEpochs) {
      return { content: csvContent, wasSampled: false, originalEpochs: originalEpochCount, sampledEpochs: originalEpochCount };
    }
    
    // Sample evenly spaced epochs
    const sampledEpochs: number[] = [];
    for (let i = 0; i < maxEpochs; i++) {
      const index = Math.round((i / (maxEpochs - 1)) * (allEpochs.length - 1));
      sampledEpochs.push(allEpochs[index]);
    }
    
    // Collect sampled data
    const sampledLines: string[] = [header];
    sampledEpochs.forEach(epoch => {
      const epochLines = epochData.get(epoch) || [];
      sampledLines.push(...epochLines);
    });
    
    return { 
      content: sampledLines.join('\n'), 
      wasSampled: true, 
      originalEpochs: originalEpochCount, 
      sampledEpochs: maxEpochs 
    };
  }

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

      // Sample epochs to limit data size
      const samplingResult = sampleEpochs(content);
      
      onFileLoad(samplingResult.content, file.name);
      if (samplingResult.wasSampled) {
        setLoadedFile(`${file.name} (sampled ${samplingResult.sampledEpochs}/${samplingResult.originalEpochs} epochs)`);
      } else {
        setLoadedFile(file.name);
      }
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

      // Sample epochs to limit data size
      const samplingResult = sampleEpochs(content);
      
      const filename = url.pathname.split('/').pop() || 'remote-file.csv';
      onFileLoad(samplingResult.content, filename);
      if (samplingResult.wasSampled) {
        setLoadedFile(`${filename} (sampled ${samplingResult.sampledEpochs}/${samplingResult.originalEpochs} epochs)`);
      } else {
        setLoadedFile(filename);
      }
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
      
      // Sample epochs to limit data size
      const samplingResult = sampleEpochs(content);
      
      onFileLoad(samplingResult.content, 'sample.csv');
      if (samplingResult.wasSampled) {
        setLoadedFile(`sample.csv (sampled ${samplingResult.sampledEpochs}/${samplingResult.originalEpochs} epochs)`);
      } else {
        setLoadedFile('sample.csv');
      }
    } catch (err) {
      setError(`Failed to load sample data: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchGithubBranches() {
    if (!githubRepo.trim()) {
      setError('Please enter a GitHub repository (e.g., owner/repo)');
      return;
    }

    const repoMatch = githubRepo.trim().match(/^([^/]+)\/([^/]+)$/);
    if (!repoMatch) {
      setError('Invalid repository format. Use "owner/repo" format (e.g., "PolicyEngine/microcalibrate")');
      return;
    }

    setIsLoadingGithubData(true);
    setError('');

    try {
      // Note: Using unauthenticated requests for public repo metadata (branches/commits)
      // This has lower rate limits but works for public repos
      const response = await fetch(`https://api.github.com/repos/${githubRepo}/branches`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Repository not found. Please check the repository name and ensure it is public.');
        }
        throw new Error(`Failed to fetch branches: ${response.status} ${response.statusText}`);
      }

      const branches: GitHubBranch[] = await response.json();
      setGithubBranches(branches);
      
      // Auto-select main/master branch if available
      const defaultBranch = branches.find(b => b.name === 'main' || b.name === 'master');
      if (defaultBranch) {
        setSelectedBranch(defaultBranch.name);
        await fetchGithubCommits(defaultBranch.name);
      }
    } catch (err) {
      setError(`GitHub API error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoadingGithubData(false);
    }
  }

  async function fetchGithubCommits(branch: string) {
    if (!githubRepo.trim() || !branch) return;

    setIsLoadingGithubData(true);
    try {
      const response = await fetch(`https://api.github.com/repos/${githubRepo}/commits?sha=${branch}&per_page=20`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Branch not found or repository is private.');
        }
        throw new Error(`Failed to fetch commits: ${response.status} ${response.statusText}`);
      }

      const commits: GitHubCommit[] = await response.json();
      setGithubCommits(commits);
      
      // Auto-select latest commit and fetch its artifacts
      if (commits.length > 0) {
        setSelectedCommit(commits[0].sha);
        await fetchGithubArtifacts(commits[0].sha);
      }
    } catch (err) {
      setError(`GitHub API error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoadingGithubData(false);
    }
  }

  async function fetchGithubArtifacts(commitSha: string) {
    if (!githubRepo.trim() || !commitSha) return;

    const githubToken = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
    if (!githubToken) {
      setError('GitHub token not configured. Please set NEXT_PUBLIC_GITHUB_TOKEN environment variable.');
      return;
    }

    setIsLoadingGithubData(true);
    setAvailableArtifacts([]);
    setSelectedArtifact('');

    try {
      const [owner, repo] = githubRepo.split('/');
      
      // Get workflow runs for the commit
      const runsResponse = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/actions/runs?head_sha=${commitSha}`,
        {
          headers: {
            'Authorization': `Bearer ${githubToken}`,
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'PolicyEngine-Dashboard/1.0'
          }
        }
      );

      if (!runsResponse.ok) {
        throw new Error(`Failed to fetch workflow runs: ${runsResponse.status}`);
      }

      const runsData = await runsResponse.json();
      const runs = runsData.workflow_runs;

      if (!runs || runs.length === 0) {
        setError('No workflow runs found for this commit.');
        return;
      }

      // Collect all calibration artifacts from completed runs
      const allArtifacts: GitHubArtifact[] = [];
      
      for (const run of runs) {
        if (run.status !== 'completed') continue;

        try {
          const artifactsResponse = await fetch(
            `https://api.github.com/repos/${owner}/${repo}/actions/runs/${run.id}/artifacts`,
            {
              headers: {
                'Authorization': `Bearer ${githubToken}`,
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'PolicyEngine-Dashboard/1.0'
              }
            }
          );

          if (!artifactsResponse.ok) continue;

          const artifactsData = await artifactsResponse.json();
          const artifacts = artifactsData.artifacts;

          // Filter for calibration artifacts
          const calibrationArtifacts = artifacts.filter((artifact: GitHubArtifact) => 
            artifact.name.toLowerCase().includes('calibration') || 
            artifact.name.toLowerCase().includes('log') ||
            artifact.name.toLowerCase().includes('.csv')
          );

          allArtifacts.push(...calibrationArtifacts);
        } catch {
          continue;
        }
      }

      if (allArtifacts.length === 0) {
        setError('No calibration artifacts found for this commit.');
        return;
      }

      // Remove duplicates and sort by creation date (newest first)
      const uniqueArtifacts = allArtifacts
        .filter((artifact, index, self) => 
          index === self.findIndex(a => a.name === artifact.name)
        )
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

      setAvailableArtifacts(uniqueArtifacts);
      
      // Auto-select the first artifact
      if (uniqueArtifacts.length > 0) {
        setSelectedArtifact(uniqueArtifacts[0].id.toString());
      }

    } catch (err) {
      setError(`Failed to fetch artifacts: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoadingGithubData(false);
    }
  }

  async function loadGithubArtifact() {
    if (!selectedArtifact) {
      setError('Please select an artifact to load');
      return;
    }

    const artifact = availableArtifacts.find(a => a.id.toString() === selectedArtifact);
    if (!artifact) {
      setError('Selected artifact not found');
      return;
    }

    const githubToken = process.env.NEXT_PUBLIC_GITHUB_TOKEN;
    if (!githubToken) {
      setError('GitHub token not configured. Please set NEXT_PUBLIC_GITHUB_TOKEN environment variable.');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      setError('🔄 Downloading and extracting CSV from artifact...');
      
      const downloadResponse = await fetch(artifact.archive_download_url, {
        headers: {
          'Authorization': `Bearer ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json',
          'User-Agent': 'PolicyEngine-Dashboard/1.0'
        }
      });

      if (!downloadResponse.ok) {
        throw new Error(`Failed to download artifact: ${downloadResponse.status}`);
      }

      const zipBuffer = await downloadResponse.arrayBuffer();
      const zip = new JSZip();
      const zipContent = await zip.loadAsync(zipBuffer);

      // Find CSV files in the ZIP
      const csvFiles = Object.keys(zipContent.files).filter(filename => 
        filename.toLowerCase().endsWith('.csv') && !zipContent.files[filename].dir
      );

      if (csvFiles.length === 0) {
        throw new Error('No CSV files found in the artifact ZIP');
      }

      // Use the first CSV file found
      const csvFilename = csvFiles[0];
      const csvFile = zipContent.files[csvFilename];
      const csvContent = await csvFile.async('text');

      // Validate the CSV content
      if (!csvContent.trim()) {
        throw new Error('The extracted CSV file is empty');
      }

      // Check for basic CSV structure
      const lines = csvContent.trim().split('\n');
      if (lines.length < 2) {
        throw new Error('The CSV must contain at least a header row and one data row');
      }

      // Check for required columns
      const headerLine = lines[0].toLowerCase();
      const requiredColumns = ['epoch', 'loss', 'target_name', 'target', 'estimate', 'error'];
      const missingColumns = requiredColumns.filter(col => !headerLine.includes(col));

      if (missingColumns.length > 0) {
        throw new Error(`Missing required columns: ${missingColumns.join(', ')}`);
      }

      // Sample epochs to limit data size
      const samplingResult = sampleEpochs(csvContent);

      // Success! Load the CSV into the dashboard
      const baseDisplayName = `${csvFilename} (from ${artifact.name})`;
      const displayName = samplingResult.wasSampled 
        ? `${baseDisplayName} - sampled ${samplingResult.sampledEpochs}/${samplingResult.originalEpochs} epochs`
        : baseDisplayName;
      
      onFileLoad(samplingResult.content, displayName);
      setLoadedFile(displayName);
      setError('');
      
      // Clear the GitHub state since we successfully loaded the file
      setGithubRepo('');
      setGithubBranches([]);
      setSelectedBranch('');
      setGithubCommits([]);
      setSelectedCommit('');
      setAvailableArtifacts([]);
      setSelectedArtifact('');

    } catch (extractError) {
      console.error('CSV extraction error:', extractError);
      setError(`❌ Failed to extract CSV: ${extractError instanceof Error ? extractError.message : 'Unknown error'}. Try using the URL tab with a direct CSV link.`);
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
          onClick={() => setActiveTab('github')}
          className={`px-4 py-2 text-sm font-medium border-b-2 ${
            activeTab === 'github'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <GitBranch className="w-4 h-4 inline mr-2" />
          GitHub
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

      {activeTab === 'github' && (
        <div className="space-y-6">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <div className="flex items-start space-x-3">
              <GitBranch className="w-6 h-6 text-gray-600 mt-1" />
              <div className="flex-1">
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Load from GitHub repository
                </h3>
                <p className="text-gray-700 mb-4">
                  Load calibration data from GitHub Actions artifacts in public repositories.
                </p>
                
                {/* Repository Input */}
                <div className="mb-4">
                  <label htmlFor="github-repo" className="block text-sm font-medium text-gray-700 mb-2">
                    Repository (owner/repo)
                  </label>
                  <div className="flex space-x-2">
                    <input
                      id="github-repo"
                      type="text"
                      value={githubRepo}
                      onChange={(e) => setGithubRepo(e.target.value)}
                      placeholder="PolicyEngine/microcalibrate"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={fetchGithubBranches}
                      disabled={isLoadingGithubData || !githubRepo.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      {isLoadingGithubData ? 'Loading...' : 'Fetch'}
                    </button>
                  </div>
                </div>

                {/* Branch Selection */}
                {githubBranches.length > 0 && (
                  <div className="mb-4">
                    <label htmlFor="github-branch" className="block text-sm font-medium text-gray-700 mb-2">
                      Branch
                    </label>
                    <select
                      id="github-branch"
                      value={selectedBranch}
                      onChange={(e) => {
                        setSelectedBranch(e.target.value);
                        fetchGithubCommits(e.target.value);
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select a branch</option>
                      {githubBranches.map((branch) => (
                        <option key={branch.name} value={branch.name}>
                          {branch.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Commit Selection */}
                {githubCommits.length > 0 && (
                  <div className="mb-4">
                    <label htmlFor="github-commit" className="block text-sm font-medium text-gray-700 mb-2">
                      Commit
                    </label>
                    <select
                      id="github-commit"
                      value={selectedCommit}
                      onChange={(e) => {
                        setSelectedCommit(e.target.value);
                        fetchGithubArtifacts(e.target.value);
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select a commit</option>
                      {githubCommits.map((commit) => (
                        <option key={commit.sha} value={commit.sha}>
                          {commit.sha.slice(0, 8)} - {commit.commit.message.slice(0, 60)}
                          {commit.commit.message.length > 60 ? '...' : ''}
                        </option>
                      ))}
                    </select>
                    {selectedCommit && (
                      <p className="text-sm text-gray-500 mt-1">
                        {githubCommits.find(c => c.sha === selectedCommit)?.commit.author.date && 
                          new Date(githubCommits.find(c => c.sha === selectedCommit)!.commit.author.date).toLocaleString()
                        }
                      </p>
                    )}
                  </div>
                )}

                {/* Artifact Selection */}
                {availableArtifacts.length > 0 && (
                  <div className="mb-4">
                    <label htmlFor="github-artifact" className="block text-sm font-medium text-gray-700 mb-2">
                      Artifact ({availableArtifacts.length} available)
                    </label>
                    <select
                      id="github-artifact"
                      value={selectedArtifact}
                      onChange={(e) => setSelectedArtifact(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select an artifact</option>
                      {availableArtifacts.map((artifact) => (
                        <option key={artifact.id} value={artifact.id.toString()}>
                          {artifact.name} ({(artifact.size_in_bytes / 1024).toFixed(1)} KB)
                        </option>
                      ))}
                    </select>
                    {selectedArtifact && (
                      <p className="text-sm text-gray-500 mt-1">
                        {availableArtifacts.find(a => a.id.toString() === selectedArtifact)?.created_at && 
                          `Created: ${new Date(availableArtifacts.find(a => a.id.toString() === selectedArtifact)!.created_at).toLocaleString()}`
                        }
                      </p>
                    )}
                  </div>
                )}

                {/* Load Button */}
                {selectedArtifact && (
                  <button
                    onClick={loadGithubArtifact}
                    disabled={isLoading}
                    className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50"
                  >
                    {isLoading ? 'Loading Artifact...' : 'Load Calibration Data'}
                  </button>
                )}

                <div className="mt-4 text-sm text-gray-600">
                  <p className="mb-2">📌 <strong>Note:</strong> This feature finds calibration CSV files in GitHub Actions artifacts.</p>
                  <ul className="space-y-1 text-xs">
                    <li>• ✅ Works with PolicyEngine public repositories</li>
                    <li>• ✅ Authenticated access to download artifacts</li>
                    <li>• ✅ Automatically finds calibration logs from CI/CD runs</li>
                    <li>• ✅ Full CSV extraction from ZIP artifacts</li>
                  </ul>
                  
                  {process.env.NODE_ENV === 'development' && (
                    <button
                      onClick={async () => {
                        try {
                          const response = await fetch('/api/test');
                          const data = await response.json();
                          alert(`API Test: ${JSON.stringify(data, null, 2)}`);
                        } catch (err) {
                          alert(`API Test Error: ${err}`);
                        }
                      }}
                      className="mt-2 text-xs bg-gray-200 px-2 py-1 rounded"
                    >
                      Test API
                    </button>
                  )}
                </div>
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
      {(isLoading || isLoadingGithubData) && (
        <div className="mt-4 text-center">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
          <p className="text-sm text-gray-600 mt-2">
            {isLoadingGithubData ? 'Loading GitHub data...' : 'Loading file...'}
          </p>
        </div>
      )}
    </div>
  );
}
