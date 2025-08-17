const mongoose = require('mongoose');

const companySchema = new mongoose.Schema({
    name: { type: String, required: true },
    domain: String,
    website: String,
    description: String,
    industry: String,
    size: String, // startup, small, medium, large, enterprise
    founded_year: Number,
    headquarters: String,
    funding_stage: String, // seed, series-a, series-b, etc.
    funding_amount: Number,
    employee_count: Number,
    tech_stack: [String],
    culture_keywords: [String],
    benefits: [String],
    remote_policy: String, // remote, hybrid, onsite
    growth_stage: String, // early, growth, mature
    linkedin_url: String,
    glassdoor_rating: Number,
    contacts: [{
        name: String,
        title: String,
        email: String,
        linkedin_url: String,
        phone: String,
        department: String,
        seniority: String // junior, mid, senior, executive
    }],
    job_postings: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Job' }],
    enrichment_status: { type: String, default: 'pending' }, // pending, enriched, failed
    last_enriched: Date,
    created_at: { type: Date, default: Date.now },
    updated_at: { type: Date, default: Date.now }
}, {
    timestamps: true
});

// Indexes for efficient searching
companySchema.index({ name: 'text', description: 'text' });
companySchema.index({ domain: 1 });
companySchema.index({ industry: 1 });
companySchema.index({ size: 1 });
companySchema.index({ 'contacts.email': 1 });

module.exports = mongoose.model('Company', companySchema);