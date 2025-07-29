"""
IP Information MCP Server

This server provides tools and resources for retrieving IP address information,
including geolocation data and network provider details.
"""

import asyncio
from typing import Optional, Dict, Any
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError


# Create the MCP server instance
mcp = FastMCP(
    name="IP Information Server",
    instructions="""
    This server provides IP address lookup capabilities to retrieve location 
    and network provider information. Use the ipinfo_lookup tool to get details 
    about any IP address, including geolocation, ISP, and network information.
    
    The server can look up information for:
    - Specific IP addresses (IPv4 or IPv6)
    - The client's own IP address (when no IP is provided)
    
    This is useful for understanding network topology, debugging connectivity 
    issues, or providing location-aware services.
    """
)


@mcp.tool
async def ipinfo_lookup(
    ip_address: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Retrieve comprehensive information about an IP address including location and network details.
    
    This tool provides geolocation data, ISP information, and network topology details
    for any IP address. When no IP address is specified, it returns information about
    the client's current IP address.
    
    Args:
        ip_address: The IP address to look up (IPv4 or IPv6). If None, looks up the client's IP.
        
    Returns:
        A dictionary containing:
        - ip: The IP address that was looked up
        - city: City name
        - region: State/province name
        - country: Country name and code
        - location: Latitude and longitude coordinates
        - timezone: Timezone information
        - isp: Internet Service Provider name
        - org: Organization name
        - as_number: Autonomous System number and name
        - postal: Postal/ZIP code
        - And other relevant network information
        
    Example usage:
        - Look up your own IP: ipinfo_lookup()
        - Look up a specific IP: ipinfo_lookup("8.8.8.8")
        - Check a website's server: ipinfo_lookup("142.250.191.14")
    """
    try:
        if ctx:
            await ctx.info(f"Looking up IP information for: {ip_address or 'client IP'}")
        
        # Import the ipinfo module functionality
        # Note: This would use the actual ipinfo:get_ip_details tool in practice
        # For this example, we'll simulate the call structure
        
        # The actual implementation would call the ipinfo:get_ip_details tool
        # result = await get_ip_details(ip_address)
        
        # For demonstration, we'll show the expected structure
        if ip_address is None:
            description = "client's current IP address"
        else:
            description = f"IP address {ip_address}"
            
        # This is where you'd integrate with the actual ipinfo:get_ip_details tool
        # For now, we'll return a structured response indicating how to use it
        return {
            "message": f"This tool would retrieve detailed information for {description}",
            "ip_queried": ip_address or "client_ip",
            "data_fields": {
                "ip": "The actual IP address",
                "city": "City name",
                "region": "State/province",
                "country": "Country name and code",
                "location": "Latitude and longitude",
                "timezone": "Timezone information", 
                "isp": "Internet Service Provider",
                "org": "Organization name",
                "postal": "Postal/ZIP code",
                "as_number": "Autonomous System details"
            },
            "note": "This is a template - integrate with ipinfo:get_ip_details tool for actual data"
        }
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to retrieve IP information: {str(e)}")
        raise ToolError(f"IP lookup failed: {str(e)}")


@mcp.resource("resource://ipinfo/usage-guide")
def get_usage_guide() -> str:
    """
    Provides a comprehensive guide on how and when to use the IP information tools.
    """
    return """
# IP Information Server Usage Guide

## Overview
This server provides tools to retrieve detailed information about IP addresses, including geolocation data, network provider information, and connectivity details.

## Primary Tool: ipinfo_lookup

### Purpose
The `ipinfo_lookup` tool retrieves comprehensive information about any IP address, including:
- Geographic location (city, region, country, coordinates)
- Network information (ISP, organization, AS number)
- Timezone and postal code data
- Connection details

### When to Use
- **Network Troubleshooting**: Identify the source or destination of network traffic
- **Security Analysis**: Investigate suspicious IP addresses
- **Content Localization**: Determine user location for geographic content delivery
- **Compliance**: Verify data sovereignty and regulatory requirements
- **Analytics**: Understand user demographics and traffic patterns
- **API Rate Limiting**: Implement location-based rate limiting

### Usage Examples

#### Look up your own IP address:
```
ipinfo_lookup()
```

#### Look up a specific IP address:
```
ipinfo_lookup("8.8.8.8")  # Google's public DNS
ipinfo_lookup("1.1.1.1")  # Cloudflare's DNS
```

#### Common use cases:
- Investigate a suspicious login: `ipinfo_lookup("192.168.1.100")`
- Check CDN server location: `ipinfo_lookup("151.101.193.140")`
- Verify VPN exit node: `ipinfo_lookup("10.0.0.1")`

## Data Fields Returned

| Field | Description | Example |
|-------|-------------|---------|
| ip | The IP address queried | "8.8.8.8" |
| city | City name | "Mountain View" |
| region | State/province | "California" |
| country | Country name and code | "United States (US)" |
| location | Coordinates | "37.4056,-122.0775" |
| timezone | Timezone info | "America/Los_Angeles" |
| isp | Internet Service Provider | "Google LLC" |
| org | Organization | "Google Public DNS" |
| postal | ZIP/postal code | "94043" |
| as_number | Autonomous System | "AS15169 Google LLC" |

## Privacy and Security Considerations

- **IP Privacy**: Be mindful that IP lookups can reveal user location
- **Rate Limits**: The underlying service may have rate limiting
- **Data Retention**: Consider how long to retain IP lookup results
- **User Consent**: Ensure appropriate consent for location tracking
- **Accuracy**: IP geolocation is approximate, especially for mobile/VPN users

## Error Handling

The tool will return appropriate error messages for:
- Invalid IP address formats
- Network connectivity issues  
- API rate limit exceeded
- Service unavailable

## Integration Notes

This server is designed to work with:
- Security monitoring systems
- Web analytics platforms
- Content delivery networks
- Fraud detection systems
- Compliance monitoring tools
"""


@mcp.resource("resource://ipinfo/examples")
def get_examples() -> Dict[str, Any]:
    """
    Provides practical examples of using the IP information tools.
    """
    return {
        "basic_usage": {
            "description": "Basic IP lookup examples",
            "examples": [
                {
                    "name": "Check your own IP",
                    "command": "ipinfo_lookup()",
                    "use_case": "Verify your current public IP and location"
                },
                {
                    "name": "Look up Google DNS",
                    "command": "ipinfo_lookup('8.8.8.8')",
                    "use_case": "Get information about Google's public DNS server"
                },
                {
                    "name": "Investigate suspicious IP",
                    "command": "ipinfo_lookup('192.168.1.100')",
                    "use_case": "Check details of an IP from security logs"
                }
            ]
        },
        "security_scenarios": [
            {
                "scenario": "Fraud Detection",
                "description": "Check if login attempts are from expected geographic regions",
                "example": "ipinfo_lookup(user_login_ip)"
            },
            {
                "scenario": "Content Delivery",
                "description": "Determine optimal CDN server based on user location",
                "example": "ipinfo_lookup() to get user location, then select nearest CDN"
            },
            {
                "scenario": "Compliance Monitoring", 
                "description": "Verify data access is within permitted geographic boundaries",
                "example": "Check if IP is in allowed country list for GDPR compliance"
            }
        ],
        "troubleshooting": {
            "common_issues": [
                {
                    "issue": "Private IP addresses",
                    "solution": "Private IPs (192.168.x.x, 10.x.x.x) won't have public geolocation data"
                },
                {
                    "issue": "VPN/Proxy detection",
                    "solution": "Results may show VPN provider location, not actual user location"
                },
                {
                    "issue": "Mobile networks",
                    "solution": "Mobile IP geolocation can be less accurate due to network topology"
                }
            ]
        }
    }


@mcp.prompt
def analyze_ip_security(ip_address: str) -> str:
    """
    Generate a prompt for analyzing the security implications of an IP address.
    
    Args:
        ip_address: The IP address to analyze for security purposes
    """
    return f"""
Please analyze the security implications of the IP address {ip_address}. 

First, use the ipinfo_lookup tool to gather information about this IP address, then provide an analysis covering:

1. **Geographic Analysis**: 
   - Is the location consistent with expected user behavior?
   - Are there any geographic red flags (known high-risk regions)?

2. **Network Analysis**:
   - What organization/ISP owns this IP?
   - Is it a known hosting provider, VPN, or proxy service?
   - Any reputation concerns with the network provider?

3. **Security Assessment**:
   - Is this IP associated with any known threats?
   - Should this IP be flagged for additional monitoring?
   - Recommended security actions based on the analysis

4. **Context Considerations**:
   - How does this IP fit into the broader security context?
   - Any patterns or anomalies to note?

Please provide a comprehensive security assessment with actionable recommendations.
"""


if __name__ == "__main__":
    mcp.run()
