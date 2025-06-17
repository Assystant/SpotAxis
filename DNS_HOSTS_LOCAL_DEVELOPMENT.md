# DNS and Hosts File Configuration for SpotAxis Local Development

## Introduction to DNS

DNS (Domain Name System) is a hierarchical naming system that translates human-readable domain names (e.g., `spotaxis.com`) into IP addresses that computers can understand. In SpotAxis, DNS resolution is crucial for the multi-tenant subdomain architecture.

## SpotAxis Subdomain Architecture

SpotAxis uses a multi-tenant architecture where each company gets its own subdomain:
- **Main Site**: `spotaxis.com` (job board and main application)
- **Company Subdomains**: `{company}.spotaxis.com` (individual company career sites)
- **Demo Environment**: `demo.spotaxis.com` (development/testing environment)

### Subdomain Middleware

The application uses `TRM.middleware.SubdomainMiddleware` to:
- Detect subdomains from incoming requests
- Route requests to appropriate URL configurations
- Handle company-specific subdomain routing

## Hosts File Overriding for Local Development

### Hosts File Locations

- **Windows**: `C:\Windows\System32\drivers\etc\hosts`
- **macOS/Linux**: `/etc/hosts`

### SpotAxis-Specific Hosts Entries

Add these entries to your hosts file for local development:

```
127.0.0.1    localhost
127.0.0.1    spotaxis.local
127.0.0.1    demo.spotaxis.local
127.0.0.1    company1.spotaxis.local
127.0.0.1    company2.spotaxis.local
127.0.0.1    api.spotaxis.local
```

### Environment Configuration

SpotAxis supports multiple environments:
- **local_development**: Development on your local machine
- **server_development**: Development and testing on server
- **productive**: Production environment

The environment is set in `TRM/environment.py` and affects:
- `HOSTED_URL` configuration
- `ROOT_DOMAIN` settings
- Database and email configurations

### Flushing DNS Cache

After modifying the hosts file, flush your system's DNS cache:

- **Windows**: `ipconfig /flushdns`
- **macOS**: `sudo killall -HUP mDNSResponder`
- **Linux**: `sudo systemctl restart nscd` (if nscd is installed)

## Local Development Setup

### Running SpotAxis Locally

1. **Start Django Development Server**:
   ```bash
   python manage.py runserver
   ```

2. **Access Different Subdomains**:
   - Main site: `http://spotaxis.local:8000`
   - Demo environment: `http://demo.spotaxis.local:8000`
   - Company subdomain: `http://company1.spotaxis.local:8000`

### URL Configuration

- **Main URLs**: `TRM/urls.py` (for main site)
- **Subdomain URLs**: `TRM/subdomain_urls.py` (for company subdomains)
- **Support URLs**: `TRM/support_urls.py` (for support subdomain)
- **Blog URLs**: `TRM/blog_urls.py` (for blog subdomain)

### Testing Subdomain Functionality

1. Add company subdomain entries to hosts file
2. Create test companies in Django admin
3. Access company-specific career sites
4. Test multi-tenant isolation

## VS Code Integration

- Use **Live Server** extension for frontend development
- Configure **Remote SSH** extension for server development
- Set up local proxy configurations for subdomain routing

## Security Considerations

- Hosts file changes only affect your local machine
- Use `.local` TLD for local development to avoid conflicts
- Remember to remove test entries when not needed
- Subdomain middleware ensures proper tenant isolation
- Session cookies are domain-specific for security 
