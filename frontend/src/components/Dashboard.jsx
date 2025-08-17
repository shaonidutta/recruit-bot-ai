import React, { useState, useEffect } from 'react';
import './Dashboard.css';

const Dashboard = () => {
    const [agentStatus, setAgentStatus] = useState(null);
    const [queueStats, setQueueStats] = useState(null);
    const [jobs, setJobs] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchParams, setSearchParams] = useState({
        keywords: 'Software Engineer',
        location: 'United States',
        num_pages: 1
    });

    // Fetch agent status and queue stats
    const fetchStatus = async () => {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            if (data.success) {
                setAgentStatus(data.status);
                setQueueStats(data.status.queue);
            }
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    };

    // Start job discovery
    const startDiscovery = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/discover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchParams)
            });
            const data = await response.json();
            if (data.success) {
                setJobs(data.jobs || []);
                setQueueStats(data.queueStats);
            }
        } catch (error) {
            console.error('Error starting discovery:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Start Google Jobs search
    const startGoogleJobs = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/google-jobs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: searchParams.keywords,
                    location: searchParams.location,
                    num_pages: searchParams.num_pages
                })
            });
            const data = await response.json();
            if (data.success) {
                setJobs(data.jobs || []);
                setQueueStats(data.queueStats);
            }
        } catch (error) {
            console.error('Error starting Google Jobs search:', error);
        } finally {
            setIsLoading(false);
        }
    };

    // Clear queue
    const clearQueue = async () => {
        try {
            await fetch('/api/queue/clear', { method: 'POST' });
            fetchStatus();
        } catch (error) {
            console.error('Error clearing queue:', error);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000); // Update every 5 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <h1>AI Recruitment Agent - Command Center</h1>
                <div className="status-indicator">
                    <span className={`status-dot ${agentStatus ? 'online' : 'offline'}`}></span>
                    <span>System {agentStatus ? 'Online' : 'Offline'}</span>
                </div>
            </header>

            <div className="dashboard-grid">
                {/* Control Panel */}
                <div className="panel control-panel">
                    <h2>Job Discovery Control</h2>
                    <div className="search-form">
                        <div className="form-group">
                            <label>Keywords:</label>
                            <input
                                type="text"
                                value={searchParams.keywords}
                                onChange={(e) => setSearchParams({...searchParams, keywords: e.target.value})}
                                placeholder="e.g., Software Engineer, Data Scientist"
                            />
                        </div>
                        <div className="form-group">
                            <label>Location:</label>
                            <input
                                type="text"
                                value={searchParams.location}
                                onChange={(e) => setSearchParams({...searchParams, location: e.target.value})}
                                placeholder="e.g., New York, Remote"
                            />
                        </div>
                        <div className="form-group">
                            <label>Pages:</label>
                            <input
                                type="number"
                                value={searchParams.num_pages}
                                onChange={(e) => setSearchParams({...searchParams, num_pages: parseInt(e.target.value)})}
                                min="1"
                                max="5"
                            />
                        </div>
                        <div className="button-group">
                            <button 
                                onClick={startDiscovery} 
                                disabled={isLoading}
                                className="btn btn-primary"
                            >
                                {isLoading ? 'Discovering...' : 'Start Full Discovery'}
                            </button>
                            <button 
                                onClick={startGoogleJobs} 
                                disabled={isLoading}
                                className="btn btn-secondary"
                            >
                                Google Jobs Only
                            </button>
                        </div>
                    </div>
                </div>

                {/* Agent Status */}
                <div className="panel status-panel">
                    <h2>Agent Status</h2>
                    {agentStatus ? (
                        <div className="status-grid">
                            <div className="status-item">
                                <span className="label">Graph Workflow:</span>
                                <span className={`value ${agentStatus.graph?.status}`}>
                                    {agentStatus.graph?.status || 'Unknown'}
                                </span>
                            </div>
                            <div className="status-item">
                                <span className="label">Google Jobs:</span>
                                <span className={`value ${agentStatus.googleJobs?.status}`}>
                                    {agentStatus.googleJobs?.status || 'Unknown'}
                                </span>
                            </div>
                            <div className="status-item">
                                <span className="label">API Key:</span>
                                <span className={`value ${agentStatus.googleJobs?.hasApiKey ? 'configured' : 'missing'}`}>
                                    {agentStatus.googleJobs?.hasApiKey ? '✓ Configured' : '✗ Missing'}
                                </span>
                            </div>
                        </div>
                    ) : (
                        <div className="loading">Loading status...</div>
                    )}
                </div>

                {/* Queue Statistics */}
                <div className="panel queue-panel">
                    <h2>Processing Queue</h2>
                    {queueStats ? (
                        <div className="queue-stats">
                            <div className="stat-item">
                                <span className="stat-number">{queueStats.totalInQueue}</span>
                                <span className="stat-label">Total in Queue</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-number">{queueStats.pending}</span>
                                <span className="stat-label">Pending</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-number">{queueStats.processing}</span>
                                <span className="stat-label">Processing</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-number">{queueStats.currentProcessing}</span>
                                <span className="stat-label">Active Workers</span>
                            </div>
                            <div className="queue-controls">
                                <button onClick={clearQueue} className="btn btn-danger">
                                    Clear Queue
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="loading">Loading queue stats...</div>
                    )}
                </div>

                {/* Recent Jobs */}
                <div className="panel jobs-panel">
                    <h2>Recent Jobs ({jobs.length})</h2>
                    <div className="jobs-list">
                        {jobs.length > 0 ? (
                            jobs.slice(0, 10).map((job, index) => (
                                <div key={index} className="job-item">
                                    <div className="job-title">{job.title}</div>
                                    <div className="job-company">{job.company}</div>
                                    <div className="job-location">{job.location}</div>
                                    <div className="job-source">{job.source}</div>
                                </div>
                            ))
                        ) : (
                            <div className="no-jobs">No jobs discovered yet. Start a search to see results.</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;