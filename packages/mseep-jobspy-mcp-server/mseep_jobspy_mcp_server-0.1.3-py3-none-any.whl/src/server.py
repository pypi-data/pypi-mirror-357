from fastmcp import FastMCP
from jobspy.linkedin import LinkedIn
from jobspy.model import ScraperInput, Site, DescriptionFormat
from jobspy.util import get_enum_from_value
import logging

# Initialize MCP server
mcp = FastMCP("linkedin-jobspy")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_job(job):
    """
    Convert a JobPost object to a serializable dictionary.
    """
    job_dict = {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "job_url": job.job_url,
        "job_url_direct": job.job_url_direct,
    }
    
    # Handle optional fields that might be None
    if job.location:
        job_dict["location"] = job.location.display_location()
    
    if job.date_posted:
        job_dict["date_posted"] = job.date_posted.isoformat()
    
    if job.description:
        job_dict["description"] = job.description
    
    if job.company_url:
        job_dict["company_url"] = job.company_url
    
    if job.job_type:
        job_dict["job_type"] = ", ".join(jt.value[0] for jt in job.job_type)
    
    if job.compensation:
        job_dict["compensation"] = {
            "min_amount": job.compensation.min_amount,
            "max_amount": job.compensation.max_amount,
            "currency": job.compensation.currency,
        }
    
    if job.emails:
        job_dict["emails"] = job.emails
    
    job_dict["is_remote"] = job.is_remote
    
    if job.job_level:
        job_dict["job_level"] = job.job_level
    
    if job.company_industry:
        job_dict["company_industry"] = job.company_industry
    
    if job.company_logo:
        job_dict["company_logo"] = job.company_logo
    
    if job.job_function:
        job_dict["job_function"] = job.job_function
    
    return job_dict

@mcp.tool()
def search_jobs(
    search_term: str,
    location: str = None,
    distance: int = 50,
    is_remote: bool = False,
    job_type: str = None,
    results_wanted: int = 15,
    fetch_description: bool = False,
    description_format: str = "markdown",
    google_search_term: str = None,
    hours_old: int = None,
    country_indeed: str = None,
    proxies: str = None,
    ca_cert: str = None,
):
    """
    Search for jobs on LinkedIn with the given criteria.
    """
    try:
        # Handle proxies
        proxy_list = None
        if proxies:
            proxy_list = [p.strip() for p in proxies.split(",")]
        
        # Initialize LinkedIn scraper
        linkedin = LinkedIn(proxies=proxy_list, ca_cert=ca_cert)
        
        # Convert job_type to enum if provided
        job_type_enum = get_enum_from_value(job_type) if job_type else None
        
        # Create scraper input
        scraper_input = ScraperInput(
            site_type=[Site.LINKEDIN],
            search_term=search_term,
            location=location,
            distance=distance,
            is_remote=is_remote,
            job_type=job_type_enum,
            results_wanted=results_wanted,
            linkedin_fetch_description=fetch_description,
            description_format=DescriptionFormat.MARKDOWN if description_format.lower() == "markdown" else DescriptionFormat.HTML,
            google_search_term=google_search_term,
            hours_old=hours_old,
            country_indeed=country_indeed
        )
        
        # Scrape jobs
        job_response = linkedin.scrape(scraper_input)
        
        # Convert job posts to a serializable format
        job_list = [serialize_job(job) for job in job_response.jobs]
        
        return job_list
    except Exception as e:
        logger.error(f"Error in search_jobs: {str(e)}")
        return {"error": str(e)}

@mcp.tool()
def get_job_details(job_id: str, description_format: str = "markdown", proxies: str = None, ca_cert: str = None):
    """
    Get detailed information about a specific LinkedIn job.
    """
    try:
        # Handle proxies
        proxy_list = None
        if proxies:
            proxy_list = [p.strip() for p in proxies.split(",")]
            
        # Initialize LinkedIn scraper
        linkedin = LinkedIn(proxies=proxy_list, ca_cert=ca_cert)
        
        # Initialize scraper_input for description format
        linkedin.scraper_input = ScraperInput(
            site_type=[Site.LINKEDIN],
            description_format=DescriptionFormat.MARKDOWN if description_format.lower() == "markdown" else DescriptionFormat.HTML
        )
        
        # Get job details
        details = linkedin._get_job_details(job_id)
        
        return details
    except Exception as e:
        logger.error(f"Error in get_job_details: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import argparse
    import sys
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='Run LinkedIn MCP Server')
    parser.add_argument('--transport', default='stdio', help='Transport to use (stdio, sse, etc.)')
    parser.add_argument('--port', type=int, default=8080, help='Port to use for network transports')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the server with the specified transport and port
    logger.info(f"Starting server with transport={args.transport}, port={args.port}")
    
    # Only pass port parameter when not using stdio
    if args.transport == 'stdio':
        mcp.run(transport=args.transport)
    else:
        mcp.run(transport=args.transport, port=args.port)
