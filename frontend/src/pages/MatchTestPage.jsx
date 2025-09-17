import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { RecentMatchesList } from '../components/ui/MatchesList';
import { MatchStats } from '../components/ui/MatchStats';
import { useMatches, useMatchStats } from '../hooks/useMatches';

/**
 * Match Test Page
 * A dedicated page for testing match functionality
 */
const MatchTestPage = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const { 
    matches, 
    loading: matchesLoading, 
    error: matchesError, 
    refresh: refreshMatches 
  } = useMatches({ limit: 10 });
  
  const { 
    stats, 
    loading: statsLoading, 
    error: statsError, 
    refresh: refreshStats 
  } = useMatchStats();

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    refreshMatches();
    refreshStats();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Match System Test
          </h1>
          <p className="text-gray-600">
            Testing the complete match display and statistics system
          </p>
          <Button 
            onClick={handleRefresh}
            className="mt-4"
          >
            Refresh All Data
          </Button>
        </div>

        {/* Stats Section */}
        <div className="mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Match Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2">Loading statistics...</span>
                </div>
              ) : statsError ? (
                <div className="text-red-600 py-4">
                  Error loading statistics: {statsError}
                </div>
              ) : (
                <MatchStats stats={stats} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Recent Matches Section */}
        <div className="mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Recent Matches</CardTitle>
            </CardHeader>
            <CardContent>
              {matchesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2">Loading matches...</span>
                </div>
              ) : matchesError ? (
                <div className="text-red-600 py-4">
                  Error loading matches: {matchesError}
                </div>
              ) : (
                <RecentMatchesList 
                  key={refreshKey}
                  limit={10}
                  showHeader={false}
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* API Test Section */}
        <div className="mb-8">
          <Card>
            <CardHeader>
              <CardTitle>API Test Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-900">Match Statistics API</h4>
                  <div className="mt-2 p-3 bg-gray-100 rounded text-sm">
                    {statsLoading ? (
                      'Loading...'
                    ) : statsError ? (
                      <span className="text-red-600">Error: {statsError}</span>
                    ) : (
                      <pre>{JSON.stringify(stats, null, 2)}</pre>
                    )}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-900">Recent Matches API</h4>
                  <div className="mt-2 p-3 bg-gray-100 rounded text-sm">
                    {matchesLoading ? (
                      'Loading...'
                    ) : matchesError ? (
                      <span className="text-red-600">Error: {matchesError}</span>
                    ) : (
                      <pre>{JSON.stringify(matches?.slice(0, 2), null, 2)}</pre>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Component Status */}
        <div className="mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Component Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 border rounded">
                  <h4 className="font-semibold text-gray-900">MatchStats</h4>
                  <div className={`mt-2 px-2 py-1 rounded text-sm ${
                    !statsLoading && !statsError ? 'bg-green-100 text-green-800' : 
                    statsError ? 'bg-red-100 text-red-800' : 
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {!statsLoading && !statsError ? 'Working' : 
                     statsError ? 'Error' : 'Loading'}
                  </div>
                </div>
                
                <div className="p-4 border rounded">
                  <h4 className="font-semibold text-gray-900">RecentMatchesList</h4>
                  <div className={`mt-2 px-2 py-1 rounded text-sm ${
                    !matchesLoading && !matchesError ? 'bg-green-100 text-green-800' : 
                    matchesError ? 'bg-red-100 text-red-800' : 
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {!matchesLoading && !matchesError ? 'Working' : 
                     matchesError ? 'Error' : 'Loading'}
                  </div>
                </div>
                
                <div className="p-4 border rounded">
                  <h4 className="font-semibold text-gray-900">useMatches Hook</h4>
                  <div className={`mt-2 px-2 py-1 rounded text-sm ${
                    matches ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {matches ? `${matches.length} matches loaded` : 'No data'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MatchTestPage;
