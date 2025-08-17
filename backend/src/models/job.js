const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
    title: { type: String, required: true },
    company: { type: String, required: true },
    location: String,
    description: String,
    requirements: [String],
    responsibilities: [String],
    skills: [String],
    experience_level: String,
    job_type: String, // full-time, part-time, contract, etc.
    salary_min: Number,
    salary_max: Number,
    salary_currency: String,
    posted_date: Date,
    application_deadline: Date,
    url: { type: String, required: true },
    source: String, // linkedin, indeed, glassdoor, etc.
    status: { type: String, default: 'active' }, // active, expired, filled
    contact_email: String,
    contact_name: String,
    contact_title: String,
    company_size: String,
    industry: String,
    benefits: [String],
    remote_allowed: Boolean,
    urgency_score: Number,
    scraped_at: { type: Date, default: Date.now },
    updated_at: { type: Date, default: Date.now }
}, {
    timestamps: true
});

// Index for efficient searching
jobSchema.index({ title: 'text', company: 'text', description: 'text' });
jobSchema.index({ posted_date: -1 });
jobSchema.index({ source: 1 });
jobSchema.index({ status: 1 });

module.exports = mongoose.model('Job', jobSchema);
