import React, { useState, useEffect, useCallback } from "react";
import DashboardLayout from "../../components/layout/DashboardLayout.jsx";
import { Card } from "../../components/ui/Card.jsx";
import { Button } from "../../components/ui/Button.jsx";
import { Input } from "../../components/ui/Input.jsx";
import { Badge } from "../../components/ui/Badge.jsx";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner.jsx";
import { Pagination } from "../../components/ui/Pagination.jsx";
import { MatchCard } from "../../components/ui/MatchCard.jsx";
import {
  RefreshCw,
  Download,
  Filter,
  Search,
  SlidersHorizontal,
} from "lucide-react";
import { matchService } from "../../api/services/matchService.js";

const MatchesPage = () => {
  const [matches, setMatches] = useState([]);
  const [filteredMatches, setFilteredMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Filter states
  const [searchTerm, setSearchTerm] = useState("");
  const [minScore, setMinScore] = useState("");
  const [sortBy, setSortBy] = useState("date"); // 'date', 'score', 'candidate', 'job'
  const [sortOrder, setSortOrder] = useState("desc"); // 'asc', 'desc'
  const [showFilters, setShowFilters] = useState(false);

  // Fetch matches from API
  const fetchMatches = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await matchService.getMatches({ limit: 1000 });

      if (response.success && response.data && response.data.matches) {
        setMatches(response.data.matches);
        setFilteredMatches(response.data.matches);
      } else {
        setMatches([]);
        setFilteredMatches([]);
      }
    } catch (err) {
      console.error("Error fetching matches:", err);
      setError("Failed to load matches. Please try again.");
      setMatches([]);
      setFilteredMatches([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchMatches();
  }, [fetchMatches]);

  // Apply filters and sorting
  useEffect(() => {
    let filtered = [...matches];

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        (match) =>
          (match.candidate_name &&
            match.candidate_name.toLowerCase().includes(term)) ||
          (match.job_title && match.job_title.toLowerCase().includes(term)) ||
          (match.company_name &&
            match.company_name.toLowerCase().includes(term)) ||
          (match.candidate_email &&
            match.candidate_email.toLowerCase().includes(term)) ||
          (match.match_reasons &&
            match.match_reasons.some((reason) =>
              reason.toLowerCase().includes(term)
            ))
      );
    }

    // Score filter
    if (minScore) {
      const scoreThreshold = parseFloat(minScore) / 100;
      filtered = filtered.filter(
        (match) => match.match_score >= scoreThreshold
      );
    }

    // Sorting
    filtered.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "score":
          comparison = (b.match_score || 0) - (a.match_score || 0);
          break;
        case "candidate":
          comparison = (a.candidate_name || "").localeCompare(
            b.candidate_name || ""
          );
          break;
        case "job":
          comparison = (a.job_title || "").localeCompare(b.job_title || "");
          break;
        case "date":
        default:
          const dateA = new Date(a.created_at || 0);
          const dateB = new Date(b.created_at || 0);
          comparison = dateB - dateA;
          break;
      }

      return sortOrder === "asc" ? -comparison : comparison;
    });

    setFilteredMatches(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [matches, searchTerm, minScore, sortBy, sortOrder]);

  // Handle refresh
  const handleRefresh = () => {
    fetchMatches();
  };

  // Handle export (placeholder)
  const handleExport = () => {
    console.log("Export matches:", filteredMatches);
    // TODO: Implement CSV/Excel export functionality
    alert("Export functionality coming soon!");
  };

  // Handle match click
  const handleMatchClick = (match) => {
    console.log("Match clicked:", match);
    // TODO: Open match details modal or navigate to detail page
  };

  // Handle contact
  const handleContact = (match) => {
    console.log("Contact candidate:", match);
    // TODO: Implement contact functionality
    alert(`Contact ${match.candidate_name} at ${match.candidate_email}`);
  };

  // Calculate pagination
  const totalItems = filteredMatches.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentMatches = filteredMatches.slice(startIndex, endIndex);

  // Get score statistics
  const getScoreStats = () => {
    if (filteredMatches.length === 0)
      return { avg: 0, high: 0, medium: 0, low: 0 };

    const avg =
      filteredMatches.reduce((sum, m) => sum + (m.match_score || 0), 0) /
      filteredMatches.length;
    const high = filteredMatches.filter((m) => m.match_score >= 0.8).length;
    const medium = filteredMatches.filter(
      (m) => m.match_score >= 0.6 && m.match_score < 0.8
    ).length;
    const low = filteredMatches.filter((m) => m.match_score < 0.6).length;

    return { avg: Math.round(avg * 100), high, medium, low };
  };

  const stats = getScoreStats();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">All Matches</h1>
            <p className="text-gray-600 mt-1">
              View and manage all job-candidate matches with advanced filtering
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center space-x-2"
            >
              <RefreshCw
                className={`h-4 w-4 ${loading ? "animate-spin" : ""}`}
              />
              <span>Refresh</span>
            </Button>

            <Button
              variant="outline"
              onClick={handleExport}
              disabled={filteredMatches.length === 0}
              className="flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Matches</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredMatches.length}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🎯</span>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High Quality</p>
                <p className="text-2xl font-bold text-green-600">
                  {stats.high}
                </p>
                <p className="text-xs text-gray-500">≥80% match</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">✨</span>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Medium Quality</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {stats.medium}
                </p>
                <p className="text-xs text-gray-500">60-79% match</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">⭐</span>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Average Score</p>
                <p className="text-2xl font-bold text-blue-600">{stats.avg}%</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📊</span>
              </div>
            </div>
          </Card>
        </div>

        {/* Error Message */}
        {error && (
          <Card className="p-4 bg-red-50 border-red-200">
            <div className="flex items-center">
              <div className="text-red-600">
                <svg
                  className="h-5 w-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
              <div className="ml-auto">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setError(null)}
                  className="text-red-600 hover:text-red-800"
                >
                  ×
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Filters and Search */}
        <Card className="p-4">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by candidate name, job title, company, or match reasons..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2"
              >
                <SlidersHorizontal className="h-4 w-4" />
                <span>Filters</span>
                {(minScore || sortBy !== "date") && (
                  <Badge variant="default" className="ml-1">
                    Active
                  </Badge>
                )}
              </Button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Score
                  </label>
                  <Input
                    type="number"
                    placeholder="e.g., 70"
                    value={minScore}
                    onChange={(e) => setMinScore(e.target.value)}
                    min="0"
                    max="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sort By
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="date">Date (Newest First)</option>
                    <option value="score">Match Score</option>
                    <option value="candidate">Candidate Name</option>
                    <option value="job">Job Title</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sort Order
                  </label>
                  <select
                    value={sortOrder}
                    onChange={(e) => setSortOrder(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="desc">Descending</option>
                    <option value="asc">Ascending</option>
                  </select>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Matches List */}
        <Card className="p-6">
          {loading && matches.length === 0 ? (
            <div className="flex justify-center items-center py-12">
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="text-slate-500 mt-2">Loading matches...</p>
              </div>
            </div>
          ) : filteredMatches.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <p className="text-slate-600 font-medium mb-2">
                No matches found
              </p>
              <p className="text-slate-500 text-sm mb-4">
                {searchTerm || minScore
                  ? "Try adjusting your filters or search terms"
                  : "Run the workflow to discover new job-candidate matches"}
              </p>
              {(searchTerm || minScore) && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setSearchTerm("");
                    setMinScore("");
                  }}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          ) : (
            <>
              <div className="space-y-4">
                {currentMatches.map((match, index) => (
                  <MatchCard
                    key={match.id || index}
                    match={match}
                    onViewDetails={handleMatchClick}
                    onContact={handleContact}
                    showActions={true}
                    compact={false}
                  />
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-6 flex justify-center">
                  <Pagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                    totalItems={totalItems}
                    itemsPerPage={itemsPerPage}
                  />
                </div>
              )}
            </>
          )}
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default MatchesPage;
