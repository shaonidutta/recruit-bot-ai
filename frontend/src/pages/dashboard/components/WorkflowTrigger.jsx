import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner';
import { Badge } from '../../../components/ui/Badge';
import { useWorkflow } from '../../../hooks/useWorkflow';

const WorkflowTrigger = ({ onWorkflowComplete }) => {
  const [keywords, setKeywords] = useState('Software Engineer');
  const { workflowStatus, loading, error, runWorkflow } = useWorkflow();

  const handleRunWorkflow = async () => {
    if (!keywords.trim()) {
      return;
    }

    const result = await runWorkflow(keywords);
    
    // Notify parent component about workflow completion
    if (result && onWorkflowComplete) {
      onWorkflowComplete(result);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleRunWorkflow();
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          Job Discovery Workflow
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Input Section */}
        <div className="flex gap-2">
          <Input
            placeholder="Enter job keywords (e.g., Software Engineer, Data Scientist)"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            className="flex-1"
          />
          <Button 
            onClick={handleRunWorkflow} 
            disabled={loading || !keywords.trim()}
            className="min-w-[100px]"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <LoadingSpinner size="sm" />
                <span>Running...</span>
              </div>
            ) : (
              'Run Workflow'
            )}
          </Button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <span className="text-red-500">❌</span>
              <span className="text-red-700 text-sm font-medium">Error</span>
            </div>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
        )}

        {/* Workflow Status Display */}
        {workflowStatus && (
          <div className={`border rounded-lg p-4 ${
            workflowStatus.success 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <Badge 
                variant={workflowStatus.success ? 'default' : 'destructive'}
                className="text-xs"
              >
                {workflowStatus.success ? '✅ Success' : '❌ Failed'}
              </Badge>
              <span className="text-sm text-slate-600">
                {workflowStatus.message}
              </span>
            </div>
            
            {workflowStatus.success && workflowStatus.data && (
              <div className="grid grid-cols-2 gap-4 mt-3">
                <div className="bg-white rounded-lg p-3 border">
                  <div className="text-lg font-semibold text-blue-600">
                    {workflowStatus.data.jobs_discovered || 0}
                  </div>
                  <div className="text-xs text-slate-500">Jobs Discovered</div>
                </div>
                <div className="bg-white rounded-lg p-3 border">
                  <div className="text-lg font-semibold text-green-600">
                    {workflowStatus.data.processing_time || 0}s
                  </div>
                  <div className="text-xs text-slate-500">Processing Time</div>
                </div>
              </div>
            )}

            {workflowStatus.timestamp && (
              <div className="text-xs text-slate-400 mt-2">
                Completed at {new Date(workflowStatus.timestamp).toLocaleTimeString()}
              </div>
            )}
          </div>
        )}

        {/* Help Text */}
        <div className="text-xs text-slate-500 bg-slate-50 rounded-lg p-3">
          <p className="font-medium mb-1">💡 How it works:</p>
          <ul className="space-y-1 ml-4">
            <li>• Enter job keywords to search for</li>
            <li>• AI agents will scrape job boards (LinkedIn, Indeed, Google)</li>
            <li>• Jobs are processed, enriched, and stored in the database</li>
            <li>• Results will appear in the jobs list below</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default WorkflowTrigger;
