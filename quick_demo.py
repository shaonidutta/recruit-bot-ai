"""
Quick Demo Script for Interview
Shows the workflow in action with real-time progress
"""

import asyncio
import sys
import os
from datetime import datetime

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from dotenv import load_dotenv
load_dotenv('services/.env')

print("\n" + "=" * 80)
print("🚀 AI RECRUITMENT AGENT - LIVE DEMO")
print("=" * 80)
print(f"⏰ Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

async def run_demo():
    """Run a complete workflow demo"""
    
    print("\n📋 DEMO: Complete Recruitment Workflow")
    print("-" * 80)
    
    # Import the orchestrator
    from app.services.unified_orchestrator import run_unified_workflow
    
    # Run workflow with demo keywords
    keywords = "Python Developer"
    print(f"\n🔍 Searching for: '{keywords}'")
    print("-" * 80)
    
    print("\n⏳ Starting workflow... (this will take ~30-45 seconds)")
    print("\n📊 Progress:")
    
    start_time = datetime.now()
    
    try:
        # Run the unified workflow
        result = await run_unified_workflow(keywords=keywords)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
        # Display results
        print(f"\n⏱️  Total Duration: {duration:.2f} seconds")
        print("\n📊 Results Summary:")
        print("-" * 80)
        
        # Scraping results
        stats = result.get('stats', {})
        print(f"\n🔍 Job Discovery:")
        print(f"   • LinkedIn Jobs: {stats.get('linkedin_jobs', 0)}")
        print(f"   • Indeed Jobs: {stats.get('indeed_jobs', 0)}")
        print(f"   • Google Jobs: {stats.get('google_jobs', 0)}")
        print(f"   • Total Discovered: {stats.get('total_jobs_discovered', 0)}")
        
        # Processing results
        raw_jobs = len(result.get('raw_jobs', []))
        parsed_jobs = len(result.get('parsed_jobs', []))
        deduplicated_jobs = len(result.get('deduplicated_jobs', []))
        enriched_jobs = len(result.get('enriched_jobs', []))
        quality_checked_jobs = len(result.get('quality_checked_jobs', []))
        matched_jobs = len(result.get('matched_jobs', []))
        stored_jobs = len(result.get('stored_jobs', []))
        
        print(f"\n⚙️  Processing Pipeline:")
        print(f"   • Raw Jobs: {raw_jobs}")
        print(f"   • Parsed Jobs: {parsed_jobs}")
        print(f"   • Deduplicated: {deduplicated_jobs}")
        print(f"   • Enriched: {enriched_jobs}")
        print(f"   • Quality Checked: {quality_checked_jobs}")
        print(f"   • Matched: {matched_jobs}")
        print(f"   • Stored: {stored_jobs}")
        
        # Enrichment stats
        enrichment_stats = result.get('enrichment_stats', {})
        if enrichment_stats:
            print(f"\n🏢 Company Enrichment:")
            print(f"   • Companies Created: {enrichment_stats.get('companies_created', 0)}")
            print(f"   • Contacts Created: {enrichment_stats.get('contacts_created', 0)}")
            print(f"   • Apollo Enriched: {enrichment_stats.get('apollo_enriched', 0)}")
        
        # Outreach results
        outreach_results = result.get('outreach_results', {})
        if outreach_results:
            print(f"\n📧 Email Outreach:")
            print(f"   • Emails Sent: {outreach_results.get('emails_sent', 0)}")
            print(f"   • LLM Generated: {outreach_results.get('llm_generated', 0)}")
            print(f"   • Total Tokens: {outreach_results.get('total_tokens_used', 0)}")
        
        # Show sample jobs
        if stored_jobs > 0:
            print(f"\n📝 Sample Jobs (first 3):")
            print("-" * 80)
            sample_jobs = result.get('stored_jobs', [])[:3]
            for i, job in enumerate(sample_jobs, 1):
                print(f"\n{i}. {job.get('title', 'N/A')}")
                print(f"   Company: {job.get('company', 'N/A')}")
                print(f"   Location: {job.get('location', 'N/A')}")
                print(f"   Source: {job.get('source', 'N/A')}")
                if job.get('enrichment_success'):
                    print(f"   ✅ Enriched with company data")
                if job.get('matches'):
                    print(f"   🎯 {len(job.get('matches', []))} candidate matches")
        
        # Errors
        errors = result.get('errors', [])
        if errors:
            print(f"\n⚠️  Errors Encountered: {len(errors)}")
            for error in errors[:3]:
                print(f"   • {error}")
        
        print("\n" + "=" * 80)
        print("✅ Demo completed successfully!")
        print("=" * 80)
        
        # Performance metrics
        print(f"\n📈 Performance Metrics:")
        print(f"   • Jobs per second: {stored_jobs / duration:.2f}")
        print(f"   • Average time per job: {duration / max(stored_jobs, 1):.2f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run the demo
if __name__ == "__main__":
    print("\n🎬 Starting demo workflow...")
    print("💡 Tip: Watch the console for real-time progress updates")
    
    success = asyncio.run(run_demo())
    
    if success:
        print("\n✅ Demo completed successfully!")
        print("\n💡 Next Steps:")
        print("   1. Check MongoDB for stored jobs")
        print("   2. View API docs at http://localhost:8000/docs")
        print("   3. Check email for outreach messages")
    else:
        print("\n❌ Demo encountered errors - check logs above")
    
    print("\n" + "=" * 80)
    print(f"⏰ Demo Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

