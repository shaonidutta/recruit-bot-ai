const axios = require('axios');
const { jobQueue } = require('../queueManager');

class GoogleJobsAgent {
    constructor() {
        this.name = 'GoogleJobsAgent';
        this.baseUrl = 'https://serpapi.com/search';
        this.apiKey = process.env.SERPAPI_KEY || '';
        this.rateLimitDelay = 1000; // 1 second between requests
        this.maxRetries = 3;
    }

    /**
     * Search for jobs using Google Jobs API via SerpAPI
     * @param {Object} params - Search parameters
     * @param {string} params.query - Job search query
     * @param {string} params.location - Location for job search
     * @param {number} params.num_pages - Number of pages to scrape (default: 1)
     * @returns {Promise<Object>} Search results
     */
    async searchJobs(params) {
        const { query, location, num_pages = 1 } = params;
        
        console.log(`[GoogleJobsAgent] Starting job search for: ${query} in ${location}`);
        
        if (!this.apiKey) {
            throw new Error('SERPAPI_KEY environment variable is required');
        }

        const allJobs = [];
        let totalProcessed = 0;

        try {
            for (let page = 0; page < num_pages; page++) {
                console.log(`[GoogleJobsAgent] Fetching page ${page + 1}/${num_pages}`);
                
                const searchParams = {
                    engine: 'google_jobs',
                    q: query,
                    location: location,
                    api_key: this.apiKey,
                    start: page * 10, // Google Jobs typically shows 10 results per page
                    num: 10
                };

                const jobs = await this.fetchJobsPage(searchParams);
                
                if (jobs && jobs.length > 0) {
                    const processedJobs = jobs.map(job => this.parseJobData(job));
                    allJobs.push(...processedJobs);
                    totalProcessed += processedJobs.length;
                    
                    console.log(`[GoogleJobsAgent] Page ${page + 1}: Found ${processedJobs.length} jobs`);
                } else {
                    console.log(`[GoogleJobsAgent] No more jobs found on page ${page + 1}`);
                    break;
                }

                // Rate limiting
                if (page < num_pages - 1) {
                    await this.delay(this.rateLimitDelay);
                }
            }

            // Add jobs to processing queue
            if (allJobs.length > 0) {
                await jobQueue.addJobs(allJobs, 'google_jobs');
            }

            console.log(`[GoogleJobsAgent] Completed search. Total jobs found: ${totalProcessed}`);
            
            return {
                success: true,
                totalJobs: totalProcessed,
                jobs: allJobs,
                source: 'google_jobs',
                searchParams: { query, location, num_pages }
            };

        } catch (error) {
            console.error('[GoogleJobsAgent] Search failed:', error.message);
            return {
                success: false,
                error: error.message,
                totalJobs: totalProcessed,
                jobs: allJobs
            };
        }
    }

    /**
     * Fetch jobs from a single page
     * @param {Object} searchParams - SerpAPI search parameters
     * @returns {Promise<Array>} Array of job objects
     */
    async fetchJobsPage(searchParams) {
        let retries = 0;
        
        while (retries < this.maxRetries) {
            try {
                const response = await axios.get(this.baseUrl, {
                    params: searchParams,
                    timeout: 30000
                });

                if (response.data && response.data.jobs_results) {
                    return response.data.jobs_results;
                } else {
                    console.warn('[GoogleJobsAgent] No jobs_results in API response');
                    return [];
                }

            } catch (error) {
                retries++;
                console.error(`[GoogleJobsAgent] API request failed (attempt ${retries}):`, error.message);
                
                if (retries < this.maxRetries) {
                    await this.delay(this.rateLimitDelay * retries); // Exponential backoff
                } else {
                    throw new Error(`Failed to fetch jobs after ${this.maxRetries} attempts: ${error.message}`);
                }
            }
        }
    }

    /**
     * Parse job data from Google Jobs API response
     * @param {Object} jobData - Raw job data from API
     * @returns {Object} Parsed job object
     */
    parseJobData(jobData) {
        try {
            // Extract salary information
            const salaryInfo = this.parseSalary(jobData.detected_extensions);
            
            // Extract job type and schedule
            const jobType = this.extractJobType(jobData.detected_extensions);
            const schedule = this.extractSchedule(jobData.detected_extensions);
            
            return {
                title: jobData.title || 'Unknown Title',
                company: jobData.company_name || 'Unknown Company',
                location: jobData.location || 'Unknown Location',
                description: jobData.description || '',
                url: jobData.share_link || jobData.related_links?.[0]?.link || '',
                
                // Salary information
                salary_min: salaryInfo.min,
                salary_max: salaryInfo.max,
                salary_currency: salaryInfo.currency,
                salary_period: salaryInfo.period,
                
                // Job details
                job_type: jobType,
                schedule_type: schedule,
                remote_allowed: this.isRemoteJob(jobData.location, jobData.description),
                
                // Additional metadata
                posted_date: this.parsePostedDate(jobData.detected_extensions),
                source: 'google_jobs',
                external_id: jobData.job_id || null,
                
                // Company information
                company_logo: jobData.thumbnail || null,
                
                // Requirements and skills (basic extraction)
                requirements: this.extractRequirements(jobData.description),
                skills: this.extractSkills(jobData.description),
                
                // Urgency scoring
                urgency_score: this.calculateUrgencyScore(jobData),
                
                scraped_at: new Date()
            };
        } catch (error) {
            console.error('[GoogleJobsAgent] Error parsing job data:', error);
            return {
                title: jobData.title || 'Parse Error',
                company: jobData.company_name || 'Unknown',
                location: jobData.location || 'Unknown',
                description: jobData.description || '',
                url: jobData.share_link || '',
                source: 'google_jobs',
                scraped_at: new Date()
            };
        }
    }

    /**
     * Parse salary information from detected extensions
     */
    parseSalary(extensions) {
        if (!extensions) return { min: null, max: null, currency: 'USD', period: 'year' };
        
        const salaryRegex = /\$([\d,]+)(?:\s*-\s*\$([\d,]+))?\s*(per\s+hour|per\s+year|hourly|annually)?/i;
        const salaryText = extensions.join(' ');
        const match = salaryText.match(salaryRegex);
        
        if (match) {
            const min = parseInt(match[1].replace(/,/g, ''));
            const max = match[2] ? parseInt(match[2].replace(/,/g, '')) : null;
            const period = match[3] ? (match[3].includes('hour') ? 'hour' : 'year') : 'year';
            
            return { min, max, currency: 'USD', period };
        }
        
        return { min: null, max: null, currency: 'USD', period: 'year' };
    }

    /**
     * Extract job type from extensions
     */
    extractJobType(extensions) {
        if (!extensions) return 'full-time';
        
        const text = extensions.join(' ').toLowerCase();
        
        if (text.includes('part-time') || text.includes('part time')) return 'part-time';
        if (text.includes('contract') || text.includes('contractor')) return 'contract';
        if (text.includes('freelance') || text.includes('freelancer')) return 'freelance';
        if (text.includes('internship') || text.includes('intern')) return 'internship';
        if (text.includes('temporary') || text.includes('temp')) return 'temporary';
        
        return 'full-time';
    }

    /**
     * Extract schedule type from extensions
     */
    extractSchedule(extensions) {
        if (!extensions) return 'standard';
        
        const text = extensions.join(' ').toLowerCase();
        
        if (text.includes('flexible') || text.includes('flex')) return 'flexible';
        if (text.includes('night') || text.includes('evening')) return 'night';
        if (text.includes('weekend')) return 'weekend';
        if (text.includes('shift')) return 'shift';
        
        return 'standard';
    }

    /**
     * Check if job allows remote work
     */
    isRemoteJob(location, description) {
        const text = `${location} ${description}`.toLowerCase();
        const remoteKeywords = ['remote', 'work from home', 'wfh', 'telecommute', 'distributed'];
        
        return remoteKeywords.some(keyword => text.includes(keyword));
    }

    /**
     * Parse posted date from extensions
     */
    parsePostedDate(extensions) {
        if (!extensions) return null;
        
        const text = extensions.join(' ');
        const dateRegex = /(\d+)\s+(day|week|month)s?\s+ago/i;
        const match = text.match(dateRegex);
        
        if (match) {
            const amount = parseInt(match[1]);
            const unit = match[2].toLowerCase();
            const date = new Date();
            
            switch (unit) {
                case 'day':
                    date.setDate(date.getDate() - amount);
                    break;
                case 'week':
                    date.setDate(date.getDate() - (amount * 7));
                    break;
                case 'month':
                    date.setMonth(date.getMonth() - amount);
                    break;
            }
            
            return date;
        }
        
        return null;
    }

    /**
     * Extract basic requirements from job description
     */
    extractRequirements(description) {
        if (!description) return [];
        
        const requirements = [];
        const text = description.toLowerCase();
        
        // Look for education requirements
        if (text.includes('bachelor') || text.includes('degree')) {
            requirements.push('Bachelor\'s degree required');
        }
        if (text.includes('master')) {
            requirements.push('Master\'s degree preferred');
        }
        
        // Look for experience requirements
        const expMatch = text.match(/(\d+)\+?\s*years?\s*(of\s+)?experience/i);
        if (expMatch) {
            requirements.push(`${expMatch[1]}+ years of experience`);
        }
        
        return requirements;
    }

    /**
     * Extract skills from job description
     */
    extractSkills(description) {
        if (!description) return [];
        
        const commonSkills = [
            'javascript', 'python', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'html', 'css', 'typescript', 'angular',
            'vue.js', 'mongodb', 'postgresql', 'redis', 'elasticsearch', 'jenkins',
            'terraform', 'ansible', 'linux', 'windows', 'macos', 'azure', 'gcp'
        ];
        
        const text = description.toLowerCase();
        return commonSkills.filter(skill => text.includes(skill));
    }

    /**
     * Calculate urgency score based on job data
     */
    calculateUrgencyScore(jobData) {
        let score = 50; // Base score
        
        // Check for urgency keywords
        const urgentKeywords = ['urgent', 'immediate', 'asap', 'quickly', 'fast-paced'];
        const text = `${jobData.title} ${jobData.description}`.toLowerCase();
        
        urgentKeywords.forEach(keyword => {
            if (text.includes(keyword)) score += 10;
        });
        
        // Recent posting increases urgency
        const postedDate = this.parsePostedDate(jobData.detected_extensions);
        if (postedDate) {
            const daysAgo = (new Date() - postedDate) / (1000 * 60 * 60 * 24);
            if (daysAgo <= 1) score += 20;
            else if (daysAgo <= 3) score += 10;
            else if (daysAgo <= 7) score += 5;
        }
        
        return Math.min(100, Math.max(0, score));
    }

    /**
     * Utility function for delays
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Get agent status and configuration
     */
    getStatus() {
        const isValidApiKey = this.apiKey && 
                             this.apiKey !== '' && 
                             !this.apiKey.includes('your_') && 
                             !this.apiKey.includes('demo_') && 
                             !this.apiKey.includes('placeholder') &&
                             this.apiKey.length > 10;
        
        return {
            name: this.name,
            status: 'ready',
            hasApiKey: isValidApiKey,
            rateLimitDelay: this.rateLimitDelay,
            maxRetries: this.maxRetries
        };
    }
}

module.exports = GoogleJobsAgent;