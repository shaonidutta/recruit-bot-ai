const mongoose = require('mongoose');

const candidateSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    phone: String,
    linkedin_url: String,
    github_url: String,
    portfolio_url: String,
    resume_url: String,
    
    // Professional Information
    current_title: String,
    current_company: String,
    years_experience: Number,
    seniority_level: String, // junior, mid, senior, lead, principal, executive
    
    // Skills and Expertise
    technical_skills: [{
        name: String,
        proficiency: String, // beginner, intermediate, advanced, expert
        years_experience: Number
    }],
    soft_skills: [String],
    certifications: [{
        name: String,
        issuer: String,
        date_obtained: Date,
        expiry_date: Date
    }],
    
    // Education
    education: [{
        degree: String,
        field_of_study: String,
        institution: String,
        graduation_year: Number,
        gpa: Number
    }],
    
    // Work Experience
    work_experience: [{
        title: String,
        company: String,
        start_date: Date,
        end_date: Date,
        description: String,
        achievements: [String],
        technologies_used: [String]
    }],
    
    // Preferences
    preferred_locations: [String],
    remote_preference: String, // remote-only, hybrid, onsite, flexible
    salary_expectation_min: Number,
    salary_expectation_max: Number,
    salary_currency: String,
    preferred_job_types: [String], // full-time, part-time, contract, freelance
    preferred_company_sizes: [String], // startup, small, medium, large, enterprise
    preferred_industries: [String],
    availability: String, // immediate, 2-weeks, 1-month, 3-months
    
    // Job Matching
    job_matches: [{
        job_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Job' },
        match_score: Number,
        match_reasons: [String],
        status: String, // interested, applied, interviewing, rejected, hired
        applied_date: Date,
        notes: String
    }],
    
    // Outreach Tracking
    outreach_campaigns: [{
        campaign_id: String,
        job_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Job' },
        status: String, // sent, opened, replied, interested, not-interested
        sent_date: Date,
        opened_date: Date,
        replied_date: Date,
        response_sentiment: String // positive, neutral, negative
    }],
    
    // Profile Status
    status: { type: String, default: 'active' }, // active, inactive, hired, not-looking
    profile_completeness: Number, // 0-100 percentage
    last_activity: Date,
    created_at: { type: Date, default: Date.now },
    updated_at: { type: Date, default: Date.now }
}, {
    timestamps: true
});

// Indexes for efficient searching and matching
candidateSchema.index({ email: 1 });
candidateSchema.index({ 'technical_skills.name': 1 });
candidateSchema.index({ seniority_level: 1 });
candidateSchema.index({ years_experience: 1 });
candidateSchema.index({ preferred_locations: 1 });
candidateSchema.index({ status: 1 });
candidateSchema.index({ 'job_matches.match_score': -1 });

// Text search index
candidateSchema.index({ 
    name: 'text', 
    current_title: 'text', 
    'technical_skills.name': 'text',
    'work_experience.title': 'text',
    'work_experience.company': 'text'
});

module.exports = mongoose.model('Candidate', candidateSchema);