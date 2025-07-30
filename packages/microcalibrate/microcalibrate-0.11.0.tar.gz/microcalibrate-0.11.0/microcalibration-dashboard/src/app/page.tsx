'use client';

import { useState } from 'react';
import FileUpload from '@/components/FileUpload';
import MetricsOverview from '@/components/MetricsOverview';
import LossChart from '@/components/LossChart';
import ErrorDistribution from '@/components/ErrorDistribution';
import CalibrationSummary from '@/components/CalibrationSummary';
import ComparisonSummary from '@/components/ComparisonSummary';
import ComparisonQualitySummary from '@/components/ComparisonQualitySummary';
import RegressionAnalysis from '@/components/RegressionAnalysis';
import TargetConvergenceComparison from '@/components/TargetConvergenceComparison';
import DataTable from '@/components/DataTable';
import { CalibrationDataPoint } from '@/types/calibration';
import { parseCalibrationCSV } from '@/utils/csvParser';

export default function Dashboard() {
  const [data, setData] = useState<CalibrationDataPoint[]>([]);
  const [filename, setFilename] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [showDashboard, setShowDashboard] = useState<boolean>(false);
  
  // Comparison mode state
  const [comparisonMode, setComparisonMode] = useState<boolean>(false);
  const [secondData, setSecondData] = useState<CalibrationDataPoint[]>([]);
  const [secondFilename, setSecondFilename] = useState<string>('');

  const handleFileLoad = (content: string, name: string) => {
    try {
      const parsedData = parseCalibrationCSV(content);
      console.log('Parsed data length:', parsedData.length);
      setData(parsedData);
      setFilename(name);
      setError('');
      setComparisonMode(false);
      // Do not automatically show dashboard - let user click the button
    } catch (err) {
      console.error('Error parsing CSV:', err);
      setError(err instanceof Error ? err.message : 'Failed to parse CSV file');
      setData([]);
      setFilename('');
      setShowDashboard(false);
    }
  };

  const handleComparisonLoad = (content1: string, filename1: string, content2: string, filename2: string) => {
    try {
      const parsedData1 = parseCalibrationCSV(content1);
      const parsedData2 = parseCalibrationCSV(content2);
      console.log('Parsed comparison data lengths:', parsedData1.length, parsedData2.length);
      
      setData(parsedData1);
      setFilename(filename1);
      setSecondData(parsedData2);
      setSecondFilename(filename2);
      setComparisonMode(true);
      setError('');
      setShowDashboard(true); // Automatically show comparison dashboard
    } catch (err) {
      console.error('Error parsing comparison CSV:', err);
      setError(err instanceof Error ? err.message : 'Failed to parse comparison CSV files');
      setData([]);
      setSecondData([]);
      setFilename('');
      setSecondFilename('');
      setComparisonMode(false);
      setShowDashboard(false);
    }
  };

  console.log('Current state - showDashboard:', showDashboard, 'data.length:', data.length);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 text-gray-900">
            Calibration dashboard
          </h1>
          <p className="text-gray-600 text-lg">
            Microdata weight calibration assessment
          </p>
          {filename && (
            <p className="mt-1 text-sm text-blue-600">
              {comparisonMode 
                ? `Comparing: ${filename} vs ${secondFilename}`
                : `Loaded: ${filename}`
              }
            </p>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error loading file
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  {error}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* File Upload */}
        {!showDashboard && (
          <div className="mb-8">
            <FileUpload 
              onFileLoad={handleFileLoad}
              onCompareLoad={handleComparisonLoad}
              onViewDashboard={() => {
                console.log('View Dashboard clicked, data length:', data.length);
                setShowDashboard(true);
              }}
            />
          </div>
        )}

        {/* Dashboard Content */}
        {showDashboard && (
          <div className="space-y-6">
            {/* Load New File Button */}
            <div className="flex justify-end">
              <button
                onClick={() => {
                  setData([]);
                  setSecondData([]);
                  setFilename('');
                  setSecondFilename('');
                  setComparisonMode(false);
                  setError('');
                  setShowDashboard(false);
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                {comparisonMode ? 'Load new comparison' : 'Load new file'}
              </button>
            </div>

            {data.length > 0 ? (
              <>
                {comparisonMode ? (
                  // Comparison Mode Dashboard
                  <>
                    <ComparisonQualitySummary 
                      firstData={data} 
                      secondData={secondData} 
                      firstName={filename} 
                      secondName={secondFilename} 
                    />
                    <ComparisonSummary 
                      firstData={data} 
                      secondData={secondData} 
                      firstName={filename} 
                      secondName={secondFilename} 
                    />
                    <RegressionAnalysis 
                      firstData={data} 
                      secondData={secondData} 
                      firstName={filename} 
                      secondName={secondFilename} 
                    />
                    <TargetConvergenceComparison 
                      firstData={data} 
                      secondData={secondData} 
                      firstName={filename} 
                      secondName={secondFilename} 
                    />
                  </>
                ) : (
                  // Regular Single Dataset Dashboard
                  <>
                    <MetricsOverview data={data} />
                    <ErrorDistribution data={data} />
                    <CalibrationSummary data={data} />
                    <LossChart data={data} />
                    <DataTable data={data} />
                  </>
                )}
              </>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
                <div className="text-yellow-800">
                  <h3 className="text-sm font-medium">No data loaded</h3>
                  <p className="text-sm mt-1">
                    Data length: {data.length}. There seems to be an issue with the data loading.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}