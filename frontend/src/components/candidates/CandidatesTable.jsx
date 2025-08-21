import React from 'react';
import { ExternalLink, MapPin, User, Clock, Mail, Phone, Briefcase } from 'lucide-react';
import { Card } from '../ui/Card.jsx';
import { Badge } from '../ui/Badge.jsx';
import { Button } from '../ui/Button.jsx';
import { LoadingSpinner } from '../ui/LoadingSpinner.jsx';

const CandidatesTable = ({ candidates, loading, onCandidateClick }) => {
  if (loading) {
    return (
      <Card className="p-8">
        <div className="flex items-center justify-center">
          <LoadingSpinner size="lg" />
          <span className="ml-3 text-gray-600">Loading candidates...</span>
        </div>
      </Card>
    );
  }

  if (!candidates || candidates.length === 0) {
    return (
      <Card className="p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">👥</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No candidates found</h3>
          <p className="text-gray-600">Try adjusting your filters or search criteria.</p>
        </div>
      </Card>
    );
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const getExperienceColor = (experience) => {
    const colors = {
      'entry': 'bg-green-100 text-green-800',
      'mid': 'bg-blue-100 text-blue-800',
      'senior': 'bg-purple-100 text-purple-800',
      'lead': 'bg-orange-100 text-orange-800',
      'executive': 'bg-red-100 text-red-800'
    };
    return colors[experience?.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const formatSkills = (skills) => {
    if (!skills) return 'No skills listed';
    if (Array.isArray(skills)) {
      return skills.slice(0, 3).join(', ') + (skills.length > 3 ? '...' : '');
    }
    if (typeof skills === 'string') {
      const skillArray = skills.split(',').map(s => s.trim());
      return skillArray.slice(0, 3).join(', ') + (skillArray.length > 3 ? '...' : '');
    }
    return 'No skills listed';
  };

  return (
    <div className="space-y-4">
      {/* Desktop Table View */}
      <div className="hidden lg:block">
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Candidate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Contact
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Experience
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Skills
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Added
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {candidates.map((candidate) => (
                  <tr key={candidate._id || candidate.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                            <User className="h-5 w-5 text-gray-600" />
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {candidate.name || candidate.firstName + ' ' + candidate.lastName || 'Unknown Name'}
                          </div>
                          <div className="text-sm text-gray-500">
                            {candidate.title || candidate.currentPosition || 'No title'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        {candidate.email && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Mail className="h-4 w-4 mr-2" />
                            <span>{candidate.email}</span>
                          </div>
                        )}
                        {candidate.phone && (
                          <div className="flex items-center text-sm text-gray-600">
                            <Phone className="h-4 w-4 mr-2" />
                            <span>{candidate.phone}</span>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {candidate.location || 'Not specified'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge className={getExperienceColor(candidate.experience)}>
                        {candidate.experience || 'Not specified'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {formatSkills(candidate.skills)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-600">
                          {formatDate(candidate.created_at || candidate.dateAdded)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onCandidateClick && onCandidateClick(candidate)}
                        >
                          View Profile
                        </Button>
                        {candidate.resume_url && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(candidate.resume_url, '_blank')}
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Mobile Card View */}
      <div className="lg:hidden space-y-4">
        {candidates.map((candidate) => (
          <Card key={candidate._id || candidate.id} className="p-4">
            <div className="space-y-3">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex items-center flex-1">
                  <div className="flex-shrink-0 h-12 w-12">
                    <div className="h-12 w-12 rounded-full bg-gray-300 flex items-center justify-center">
                      <User className="h-6 w-6 text-gray-600" />
                    </div>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {candidate.name || candidate.firstName + ' ' + candidate.lastName || 'Unknown Name'}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {candidate.title || candidate.currentPosition || 'No title'}
                    </p>
                  </div>
                </div>
                <Badge className={getExperienceColor(candidate.experience)}>
                  {candidate.experience || 'Not specified'}
                </Badge>
              </div>

              {/* Contact Details */}
              <div className="space-y-2">
                {candidate.email && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Mail className="h-4 w-4 mr-2" />
                    <span>{candidate.email}</span>
                  </div>
                )}
                
                {candidate.phone && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Phone className="h-4 w-4 mr-2" />
                    <span>{candidate.phone}</span>
                  </div>
                )}
                
                <div className="flex items-center text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mr-2" />
                  <span>{candidate.location || 'Not specified'}</span>
                </div>
                
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 mr-2" />
                  <span>{formatDate(candidate.created_at || candidate.dateAdded)}</span>
                </div>
              </div>

              {/* Skills */}
              <div>
                <div className="flex items-center text-sm text-gray-600 mb-1">
                  <Briefcase className="h-4 w-4 mr-2" />
                  <span className="font-medium">Skills:</span>
                </div>
                <p className="text-sm text-gray-900">
                  {formatSkills(candidate.skills)}
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onCandidateClick && onCandidateClick(candidate)}
                  className="flex-1"
                >
                  View Profile
                </Button>
                {candidate.resume_url && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(candidate.resume_url, '_blank')}
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default CandidatesTable;