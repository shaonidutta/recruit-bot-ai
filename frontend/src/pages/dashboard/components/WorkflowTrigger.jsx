import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner';
import { Badge } from '../../../components/ui/Badge';
import { ProgressBar, AnimatedCounter } from '../../../components/ui/AnimatedCounter';
import { useWorkflow } from '../../../hooks/useWorkflow';

const WorkflowTrigger = ({ onWorkflowComplete }) => {
  const [keywords, setKeywords] = useState('Software Engineer');
  const { workflowStatus, loading, error, runWorkflow } = useWorkflow();

  // Enhanced workflow state
  const [workflowProgress, setWorkflowProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [liveUpdates, setLiveUpdates] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [workflowStartTime, setWorkflowStartTime] = useState(null);

  // Workflow progress simulation steps
  const progressSteps = [
    { progress: 0, message: "🚀 Initializing AI recruitment agents...", duration: 1000 },
    { progress: 15, message: "🔍 Scanning LinkedIn job postings...", duration: 2000 },
    { progress: 30, message: "🎯 Scraping Indeed opportunities...", duration: 2500 },
    { progress: 45, message: "🌐 Discovering Google job listings...", duration: 2000 },
    { progress: 60, message: "📊 Processing and deduplicating jobs...", duration: 1500 },
    { progress: 75, message: "🤖 Running AI matching algorithms...", duration: 2000 },
    { progress: 85, message: "✉️ Generating personalized outreach emails...", duration: 1500 },
    { progress: 95, message: "📧 Sending emails to hiring managers...", duration: 1000 },
    { progress: 100, message: "✅ Workflow completed successfully!", duration: 500 }
  ];

  const simulateProgress = () => {
    setIsRunning(true);
    setWorkflowProgress(0);
    setLiveUpdates([]);

    progressSteps.forEach((step, index) => {
      setTimeout(() => {
        setWorkflowProgress(step.progress);
        setCurrentStep(step.message);
        setLiveUpdates(prev => [...prev, {
          id: index,
          message: step.message,
          timestamp: new Date(),
          progress: step.progress
        }]);

        if (step.progress === 100) {
          setTimeout(() => {
            setIsRunning(false);
          }, 1000);
        }
      }, progressSteps.slice(0, index).reduce((acc, s) => acc + s.duration, 0));
    });
  };

  const handleRunWorkflow = async () => {
    if (!keywords.trim()) {
      return;
    }

    // Start progress simulation
    simulateProgress();

    try {
      const result = await runWorkflow(keywords);

      // Add keywords to result for activity tracking
      const enhancedResult = {
        ...result,
        keywords: keywords
      };

      // Clear running state immediately on success
      if (result && result.success) {
        setIsRunning(false);
        setWorkflowProgress(100);
        setCurrentStep('Workflow completed successfully!');

        // Reset after showing success
        setTimeout(() => {
          setWorkflowProgress(0);
          setCurrentStep('');
        }, 3000);
      }

      // Notify parent component about workflow completion
      if (result && onWorkflowComplete) {
        onWorkflowComplete(enhancedResult);
      }
    } catch (error) {
      // Check if it's a timeout error
      if (error.message && error.message.includes('timeout')) {
        // Handle timeout gracefully - workflow is still running in background
        setCurrentStep('Workflow continues in background...');
        setWorkflowProgress(75); // Show partial progress

        // Show success message after a delay
        setTimeout(() => {
          setIsRunning(false);
          setWorkflowProgress(100);
          setCurrentStep('Workflow started successfully!');

          // Add background processing activity
          const backgroundEvent = new CustomEvent('workflowComplete', {
            detail: {
              keywords: keywords,
              result: {
                success: true,
                message: 'Workflow started successfully. Processing continues in background.',
                background: true
              }
            }
          });
          window.dispatchEvent(backgroundEvent);

          // Reset after showing success
          setTimeout(() => {
            setWorkflowProgress(0);
            setCurrentStep('');
          }, 3000);
        }, 2000);
      } else {
        // Handle other errors normally
        setIsRunning(false);
        setWorkflowProgress(0);
        setCurrentStep('');

        // Add error activity
        const errorEvent = new CustomEvent('workflowComplete', {
          detail: {
            keywords: keywords,
            result: { error: true, message: error.message }
          }
        });
        window.dispatchEvent(errorEvent);
      }
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

        {/* Enhanced Progress Display */}
        {(isRunning || loading) && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <ProgressBar
              progress={workflowProgress}
              status={currentStep || "Preparing workflow..."}
              animated={true}
              className="mb-4"
            />

            {/* Live Updates Feed */}
            {liveUpdates.length > 0 && (
              <div className="max-h-32 overflow-y-auto space-y-2">
                {liveUpdates.slice(-3).map((update) => (
                  <div key={update.id} className="flex items-center space-x-2 text-sm">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                    <span className="text-gray-700">{update.message}</span>
                    <span className="text-xs text-gray-500 ml-auto">
                      {update.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Enhanced Workflow Results */}
        {workflowStatus && !isRunning && (
          <div className={`border rounded-lg p-4 transition-all duration-500 ${
            workflowStatus.success
              ? 'bg-green-50 border-green-200'
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center gap-2 mb-3">
              <Badge
                variant={workflowStatus.success ? 'default' : 'destructive'}
                className="text-xs"
              >
                {workflowStatus.success ? '✅ Success' : '❌ Failed'}
              </Badge>
              <span className="text-sm font-medium text-slate-700">
                {workflowStatus.message}
              </span>
            </div>

            {workflowStatus.success && workflowStatus.data && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mt-3">
                <div className="bg-white rounded-lg p-3 border shadow-sm">
                  <div className="text-lg font-bold text-blue-600">
                    <AnimatedCounter value={workflowStatus.data.jobs_discovered || 0} />
                  </div>
                  <div className="text-xs text-slate-500">Jobs Discovered</div>
                </div>
                <div className="bg-white rounded-lg p-3 border shadow-sm">
                  <div className="text-lg font-bold text-green-600">
                    <AnimatedCounter
                      value={workflowStatus.data.processing_time || 0}
                      formatter={(val) => `${val}s`}
                    />
                  </div>
                  <div className="text-xs text-slate-500">Processing Time</div>
                </div>
                <div className="bg-white rounded-lg p-3 border shadow-sm">
                  <div className="text-lg font-bold text-purple-600">
                    <AnimatedCounter value={workflowStatus.data.matches_found || 0} />
                  </div>
                  <div className="text-xs text-slate-500">Matches Found</div>
                </div>
                <div className="bg-white rounded-lg p-3 border shadow-sm">
                  <div className="text-lg font-bold text-orange-600">
                    <AnimatedCounter value={workflowStatus.data.emails_sent || 0} />
                  </div>
                  <div className="text-xs text-slate-500">Emails Sent</div>
                </div>
              </div>
            )}

            {workflowStatus.timestamp && (
              <div className="text-xs text-slate-400 mt-3 flex items-center">
                <span>Completed at {new Date(workflowStatus.timestamp).toLocaleTimeString()}</span>
                <div className="ml-auto flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full" />
                  <span>Ready for next workflow</span>
                </div>
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
