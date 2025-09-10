/**
 * Workflow Progress Timing Configuration
 * More realistic timing for AI recruitment workflow
 */

export const WORKFLOW_STEPS = [
  { progress: 0, message: "🚀 Initializing AI recruitment agents...", duration: 3000 },
  { progress: 10, message: "🔍 Scanning LinkedIn job postings...", duration: 8000 },
  { progress: 25, message: "🎯 Scraping Indeed opportunities...", duration: 7000 },
  { progress: 40, message: "🌐 Discovering Google job listings...", duration: 6000 },
  { progress: 55, message: "📊 Processing and deduplicating jobs...", duration: 5000 },
  { progress: 70, message: "🤖 Running AI matching algorithms...", duration: 8000 },
  { progress: 85, message: "✉️ Generating personalized outreach emails...", duration: 6000 },
  { progress: 95, message: "📧 Sending emails to hiring managers...", duration: 4000 },
  { progress: 100, message: "✅ Workflow completed successfully!", duration: 2000 }
];

/**
 * Calculate total workflow duration
 */
export const getTotalDuration = () => {
  return WORKFLOW_STEPS.reduce((total, step) => total + step.duration, 0);
};

/**
 * Get formatted duration string
 */
export const getFormattedDuration = () => {
  const totalMs = getTotalDuration();
  const totalSeconds = Math.round(totalMs / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }
  return `${seconds}s`;
};

/**
 * Progress step configuration for different workflow types
 */
export const WORKFLOW_CONFIGS = {
  standard: WORKFLOW_STEPS,
  
  quick: [
    { progress: 0, message: "🚀 Quick scan initialization...", duration: 1000 },
    { progress: 25, message: "🔍 Fast job discovery...", duration: 2000 },
    { progress: 50, message: "📊 Rapid processing...", duration: 1500 },
    { progress: 75, message: "🤖 Quick matching...", duration: 2000 },
    { progress: 100, message: "✅ Quick workflow completed!", duration: 500 }
  ],
  
  comprehensive: [
    { progress: 0, message: "🚀 Comprehensive scan initialization...", duration: 5000 },
    { progress: 8, message: "🔍 Deep LinkedIn analysis...", duration: 12000 },
    { progress: 18, message: "🎯 Extensive Indeed scraping...", duration: 10000 },
    { progress: 28, message: "🌐 Thorough Google job discovery...", duration: 9000 },
    { progress: 40, message: "📊 Advanced deduplication...", duration: 7000 },
    { progress: 52, message: "🧠 Deep AI analysis...", duration: 10000 },
    { progress: 65, message: "🤖 Comprehensive matching...", duration: 12000 },
    { progress: 78, message: "✉️ Personalized email generation...", duration: 8000 },
    { progress: 90, message: "📧 Batch email delivery...", duration: 6000 },
    { progress: 100, message: "✅ Comprehensive workflow completed!", duration: 3000 }
  ]
};

export default {
  WORKFLOW_STEPS,
  WORKFLOW_CONFIGS,
  getTotalDuration,
  getFormattedDuration
};
