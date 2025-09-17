import React from 'react';
import { Card, CardContent, CardHeader } from './Card';
import { Badge } from './Badge';
import { Button } from './Button';
import { formatTimeAgo } from '../../utils/dateUtils';

/**
 * MatchCard Component
 * Displays individual job-candidate match with score, details, and actions
 */
export const MatchCard = ({ 
  match, 
  onViewDetails, 
  onContact, 
  onApprove, 
  onReject,
  showActions = true,
  compact = false 
}) => {
  if (!match) return null;

  const {
    id,
    candidate_name,
    candidate_email,
    candidate_location,
    job_title,
    company_name,
    job_location,
    match_score,
    match_reasons = [],
    created_at
  } = match;

  // Calculate match score percentage and color
  const scorePercentage = Math.round(match_score * 100);
  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getScoreBadgeColor = (score) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  // Format creation date
  const timeAgo = created_at ? formatTimeAgo(created_at) : '';

  return (
    <Card className={`transition-all duration-200 hover:shadow-md border-l-4 ${getScoreColor(match_score)} ${compact ? 'p-3' : ''}`}>
      <CardHeader className={`${compact ? 'pb-2' : 'pb-3'}`}>
        <div className="flex justify-between items-start">
          <div className="flex-1 min-w-0">
            {/* Candidate Info */}
            <div className="flex items-center space-x-2 mb-1">
              <h4 className="font-semibold text-gray-900 truncate">
                {candidate_name || 'Unknown Candidate'}
              </h4>
              <Badge className={`text-xs font-medium ${getScoreBadgeColor(match_score)}`}>
                {scorePercentage}% Match
              </Badge>
            </div>
            
            {/* Job Info */}
            <div className="text-sm text-gray-600 mb-1">
              <span className="font-medium">{job_title || 'Unknown Position'}</span>
              {company_name && (
                <>
                  <span className="mx-1">•</span>
                  <span>{company_name}</span>
                </>
              )}
            </div>

            {/* Location Info */}
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              {candidate_location && (
                <span>📍 {candidate_location}</span>
              )}
              {job_location && candidate_location !== job_location && (
                <span>🏢 {job_location}</span>
              )}
              {timeAgo && (
                <span>⏰ {timeAgo}</span>
              )}
            </div>
          </div>

          {/* Match Score Visual */}
          <div className="flex flex-col items-center ml-4">
            <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center ${getScoreColor(match_score)}`}>
              <span className="text-sm font-bold">{scorePercentage}%</span>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className={`${compact ? 'pt-0' : ''}`}>
        {/* Match Reasons */}
        {match_reasons.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-1">
              {match_reasons.slice(0, compact ? 2 : 3).map((reason, index) => (
                <Badge 
                  key={index} 
                  variant="outline" 
                  className="text-xs bg-blue-50 text-blue-700 border-blue-200"
                >
                  {reason}
                </Badge>
              ))}
              {match_reasons.length > (compact ? 2 : 3) && (
                <Badge variant="outline" className="text-xs text-gray-500">
                  +{match_reasons.length - (compact ? 2 : 3)} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Contact Info */}
        {candidate_email && !compact && (
          <div className="text-xs text-gray-600 mb-3">
            📧 {candidate_email}
          </div>
        )}

        {/* Actions */}
        {showActions && (
          <div className="flex space-x-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => onViewDetails?.(match)}
              className="flex-1 text-xs"
            >
              View Details
            </Button>
            
            {onContact && (
              <Button
                size="sm"
                onClick={() => onContact(match)}
                className="flex-1 text-xs bg-blue-600 hover:bg-blue-700"
              >
                Contact
              </Button>
            )}
            
            {onApprove && (
              <Button
                size="sm"
                onClick={() => onApprove(match)}
                className="text-xs bg-green-600 hover:bg-green-700"
              >
                ✓
              </Button>
            )}
            
            {onReject && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onReject(match)}
                className="text-xs text-red-600 border-red-200 hover:bg-red-50"
              >
                ✗
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Compact Match Card for lists and summaries
 */
export const CompactMatchCard = ({ match, onViewDetails, onContact }) => {
  return (
    <MatchCard 
      match={match}
      onViewDetails={onViewDetails}
      onContact={onContact}
      showActions={true}
      compact={true}
    />
  );
};

/**
 * Match Score Badge Component
 */
export const MatchScoreBadge = ({ score, size = 'md' }) => {
  const percentage = Math.round(score * 100);
  
  const getColorClass = (score) => {
    if (score >= 0.8) return 'bg-green-100 text-green-800 border-green-200';
    if (score >= 0.6) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const getSizeClass = (size) => {
    switch (size) {
      case 'sm': return 'text-xs px-2 py-1';
      case 'lg': return 'text-base px-4 py-2';
      default: return 'text-sm px-3 py-1';
    }
  };

  return (
    <span className={`inline-flex items-center rounded-full border font-medium ${getColorClass(score)} ${getSizeClass(size)}`}>
      {percentage}% Match
    </span>
  );
};

/**
 * Match Reasons List Component
 */
export const MatchReasonsList = ({ reasons = [], maxVisible = 3, showAll = false }) => {
  const visibleReasons = showAll ? reasons : reasons.slice(0, maxVisible);
  const hiddenCount = reasons.length - maxVisible;

  return (
    <div className="flex flex-wrap gap-1">
      {visibleReasons.map((reason, index) => (
        <Badge 
          key={index} 
          variant="outline" 
          className="text-xs bg-blue-50 text-blue-700 border-blue-200"
        >
          {reason}
        </Badge>
      ))}
      {!showAll && hiddenCount > 0 && (
        <Badge variant="outline" className="text-xs text-gray-500">
          +{hiddenCount} more
        </Badge>
      )}
    </div>
  );
};

export default MatchCard;
