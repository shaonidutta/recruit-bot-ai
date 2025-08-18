import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Progress } from '../../../components/ui/Progress';
import { cn } from '../../../utils/cn';
import { getMockData } from '../../../data/mockData';

const PipelineStage = ({ stage, nextStage, isLast }) => {
  const conversionRate = nextStage ?
    Math.round((nextStage.count / stage.count) * 100) : 0;

  return (
    <div className="flex items-center flex-shrink-0">
      {/* Stage Circle */}
      <div className="flex flex-col items-center">
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-xs shadow-lg mb-1"
          style={{ backgroundColor: stage.color }}
        >
          {stage.count}
        </div>
        <p className="text-xs text-slate-600 text-center leading-tight max-w-16 break-words">
          {stage.name}
        </p>
      </div>

      {/* Arrow and Conversion Rate */}
      {!isLast && (
        <div className="flex flex-col items-center mx-2 flex-shrink-0">
          <div className="flex items-center justify-center mb-1">
            <div className="w-6 h-0.5 bg-slate-200 relative">
              <div
                className="h-full transition-all duration-1000 ease-out rounded-full"
                style={{
                  width: `${Math.min(conversionRate, 100)}%`,
                  backgroundColor: stage.color
                }}
              />
            </div>
            <div className="text-slate-400 ml-1 text-xs">→</div>
          </div>
          <div className="text-xs text-slate-500 font-medium">
            {conversionRate}%
          </div>
        </div>
      )}
    </div>
  );
};

const MatchPipeline = () => {
  const pipelineData = getMockData('pipeline');
  
  if (!pipelineData) return null;

  const { stages } = pipelineData;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>📈</span>
          <span>Match Pipeline</span>
        </CardTitle>
        <p className="text-sm text-slate-600">
          AI recruitment funnel from discovery to response
        </p>
      </CardHeader>
      
      <CardContent>
        {/* Pipeline Visualization */}
        <div className="w-full mb-6">
          <div className="flex items-center justify-between overflow-x-auto pb-4 min-w-full">
            {stages.map((stage, index) => (
              <PipelineStage
                key={stage.name}
                stage={stage}
                nextStage={stages[index + 1]}
                isLast={index === stages.length - 1}
              />
            ))}
          </div>
        </div>

        {/* Pipeline Stats */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100">
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">
              {Math.round((stages[stages.length - 1].count / stages[0].count) * 100)}%
            </div>
            <p className="text-xs text-slate-500">Overall Conversion</p>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">
              {stages.reduce((sum, stage) => sum + stage.count, 0)}
            </div>
            <p className="text-xs text-slate-500">Total Pipeline</p>
          </div>
        </div>

        {/* Stage Details */}
        <div className="mt-4 space-y-2">
          {stages.map((stage, index) => {
            const nextStage = stages[index + 1];
            const conversionRate = nextStage ? 
              Math.round((nextStage.count / stage.count) * 100) : 100;
            
            return (
              <div key={stage.name} className="flex items-center justify-between py-2">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: stage.color }}
                  />
                  <span className="text-sm font-medium text-slate-700">
                    {stage.name}
                  </span>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-sm font-bold text-slate-900">
                    {stage.count}
                  </span>
                  {nextStage && (
                    <div className="flex items-center space-x-2">
                      <Progress 
                        value={conversionRate} 
                        className="w-16 h-2"
                      />
                      <span className="text-xs text-slate-500 w-8">
                        {conversionRate}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default MatchPipeline;
