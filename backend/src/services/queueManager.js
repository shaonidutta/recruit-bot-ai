const EventEmitter = require('events');
const Job = require('../models/job');
const Company = require('../models/company');
const { connectDB } = require('../utils/dbHelper');

class JobQueue extends EventEmitter {
    constructor() {
        super();
        this.queue = [];
        this.processing = false;
        this.maxConcurrent = 5;
        this.currentProcessing = 0;
        this.retryAttempts = 3;
        this.retryDelay = 5000; // 5 seconds
    }

    /**
     * Add jobs to the processing queue
     * @param {Array} jobs - Array of job objects to process
     * @param {String} source - Source of the jobs (linkedin, indeed, etc.)
     */
    async addJobs(jobs, source = 'unknown') {
        console.log(`[QueueManager] Adding ${jobs.length} jobs from ${source} to queue`);
        
        const jobsWithMetadata = jobs.map(job => ({
            ...job,
            source,
            addedAt: new Date(),
            attempts: 0,
            status: 'pending'
        }));

        this.queue.push(...jobsWithMetadata);
        this.emit('jobsAdded', { count: jobs.length, source });
        
        // Start processing if not already running
        if (!this.processing) {
            this.startProcessing();
        }

        return {
            success: true,
            queueSize: this.queue.length,
            message: `Added ${jobs.length} jobs to queue`
        };
    }

    /**
     * Start processing jobs in the queue
     */
    async startProcessing() {
        if (this.processing) {
            console.log('[QueueManager] Processing already in progress');
            return;
        }

        this.processing = true;
        console.log('[QueueManager] Starting job processing');
        this.emit('processingStarted');

        try {
            await connectDB();
            
            while (this.queue.length > 0 && this.currentProcessing < this.maxConcurrent) {
                const job = this.queue.shift();
                this.processJob(job);
            }
        } catch (error) {
            console.error('[QueueManager] Error starting processing:', error);
            this.emit('processingError', error);
        }
    }

    /**
     * Process a single job
     * @param {Object} jobData - Job data to process
     */
    async processJob(jobData) {
        this.currentProcessing++;
        jobData.status = 'processing';
        
        console.log(`[QueueManager] Processing job: ${jobData.title} at ${jobData.company}`);
        
        try {
            // Check if job already exists
            const existingJob = await Job.findOne({ 
                url: jobData.url,
                source: jobData.source 
            });

            if (existingJob) {
                console.log(`[QueueManager] Job already exists: ${jobData.title}`);
                jobData.status = 'duplicate';
                this.emit('jobProcessed', { job: jobData, result: 'duplicate' });
            } else {
                // Save new job
                const newJob = new Job({
                    ...jobData,
                    scraped_at: new Date()
                });
                
                await newJob.save();
                console.log(`[QueueManager] Saved job: ${jobData.title}`);
                
                // Process company information
                await this.processCompany(jobData.company, newJob._id);
                
                jobData.status = 'completed';
                this.emit('jobProcessed', { job: jobData, result: 'saved', jobId: newJob._id });
            }
        } catch (error) {
            console.error(`[QueueManager] Error processing job ${jobData.title}:`, error);
            
            // Retry logic
            if (jobData.attempts < this.retryAttempts) {
                jobData.attempts++;
                jobData.status = 'retry';
                
                console.log(`[QueueManager] Retrying job ${jobData.title} (attempt ${jobData.attempts})`);
                
                // Add back to queue with delay
                setTimeout(() => {
                    this.queue.unshift(jobData);
                }, this.retryDelay);
            } else {
                jobData.status = 'failed';
                this.emit('jobFailed', { job: jobData, error });
            }
        } finally {
            this.currentProcessing--;
            
            // Continue processing if there are more jobs
            if (this.queue.length > 0 && this.currentProcessing < this.maxConcurrent) {
                const nextJob = this.queue.shift();
                this.processJob(nextJob);
            }
            
            // Check if processing is complete
            if (this.currentProcessing === 0 && this.queue.length === 0) {
                this.processing = false;
                console.log('[QueueManager] Processing completed');
                this.emit('processingCompleted');
            }
        }
    }

    /**
     * Process company information
     * @param {String} companyName - Name of the company
     * @param {String} jobId - ID of the job
     */
    async processCompany(companyName, jobId) {
        try {
            let company = await Company.findOne({ name: companyName });
            
            if (!company) {
                company = new Company({
                    name: companyName,
                    job_postings: [jobId],
                    enrichment_status: 'pending'
                });
                await company.save();
                console.log(`[QueueManager] Created new company: ${companyName}`);
            } else {
                // Add job to existing company
                if (!company.job_postings.includes(jobId)) {
                    company.job_postings.push(jobId);
                    await company.save();
                }
            }
            
            this.emit('companyProcessed', { company: companyName, jobId });
        } catch (error) {
            console.error(`[QueueManager] Error processing company ${companyName}:`, error);
        }
    }

    /**
     * Get queue statistics
     */
    getStats() {
        const pendingJobs = this.queue.filter(job => job.status === 'pending').length;
        const processingJobs = this.queue.filter(job => job.status === 'processing').length;
        const retryJobs = this.queue.filter(job => job.status === 'retry').length;
        
        return {
            totalInQueue: this.queue.length,
            pending: pendingJobs,
            processing: processingJobs,
            retry: retryJobs,
            currentProcessing: this.currentProcessing,
            isProcessing: this.processing
        };
    }

    /**
     * Clear the queue
     */
    clearQueue() {
        this.queue = [];
        console.log('[QueueManager] Queue cleared');
        this.emit('queueCleared');
    }

    /**
     * Pause processing
     */
    pauseProcessing() {
        this.processing = false;
        console.log('[QueueManager] Processing paused');
        this.emit('processingPaused');
    }
}

// Create singleton instance
const jobQueue = new JobQueue();

// Event listeners for monitoring
jobQueue.on('jobsAdded', (data) => {
    console.log(`[QueueManager] Event: ${data.count} jobs added from ${data.source}`);
});

jobQueue.on('jobProcessed', (data) => {
    console.log(`[QueueManager] Event: Job processed - ${data.result}`);
});

jobQueue.on('jobFailed', (data) => {
    console.error(`[QueueManager] Event: Job failed - ${data.job.title}`);
});

jobQueue.on('processingCompleted', () => {
    console.log('[QueueManager] Event: All jobs processed');
});

module.exports = {
    jobQueue,
    JobQueue
};