# Upwork Fetcher CLI

A powerful Python command-line tool that fetches and stores Upwork job postings using the Upwork GraphQL API. This tool helps freelancers and agencies efficiently search, filter, and track job opportunities from Upwork.

## Features

- **Job Fetching**: Search for jobs using multiple search expressions with Lucene syntax support
- **Database Storage**: Automatically stores job data in PostgreSQL database with deduplication
- **Rich CLI Interface**: Beautiful command-line interface with tables and progress indicators
- **OAuth2 Authentication**: Secure authentication with Upwork API using OAuth2 flow
- **Flexible Filtering**: Support for various search criteria and pagination
- **Data Persistence**: Prevents duplicate job entries and maintains historical data

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- Upwork API credentials (Client ID, Client Secret, Redirect URI)

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd upwork-automation-cli

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Using pip

```bash
pip install upwork-fetcher
```

## Configuration

### 1. Upwork API Setup

1. Go to [Upwork Developers](https://developers.upwork.com/)
2. Create a new application
3. Note down your Client ID, Client Secret, and set up a Redirect URI

### 2. Database Setup

Set up a PostgreSQL database and note the connection URL:
```
postgresql://username:password@host:port/database_name
```

## Usage

### Initial Setup

Configure your Upwork API credentials:

```bash
upwork-fetcher setup --client_id "your_client_id" --client_secret "your_client_secret" --redirect_uri "your_redirect_uri"
```

This will:
1. Save your API credentials
2. Open an authorization URL in your browser
3. Prompt you to enter the authorization code
4. Exchange the code for access and refresh tokens

### Fetching Jobs

Search and fetch jobs with various options:

```bash
# Basic job search
upwork-fetcher fetch -s "python" --limit 20

# Multiple search expressions
upwork-fetcher fetch -s "react" -s "node.js" -s "typescript" --limit 50

# With database URL (if not configured)
upwork-fetcher fetch -s "machine learning" --db-url "postgresql://user:pass@localhost:5432/upwork_jobs"

# Verbose output with job details table
upwork-fetcher fetch -s "django" --verbose --limit 10

# With pagination
upwork-fetcher fetch -s "flutter" --offset 20 --limit 30
```

### Command Options

#### `setup` command
- `--client_id`: Your Upwork API client ID
- `--client_secret`: Your Upwork API client secret  
- `--redirect_uri`: Your configured redirect URI

#### `fetch` command
- `-s, --search-expression`: Search expression (can be used multiple times)
- `--limit`: Maximum number of jobs to fetch (default: 50)
- `--offset`: Number of jobs to skip (default: 0)
- `--db-url`: PostgreSQL database URL
- `-v, --verbose`: Show detailed job information in table format

## Project Structure

```
upwork_fetcher/
├── cli.py                 # Main CLI entry point
├── commands.py            # CLI command implementations
├── config.py             # Configuration management
├── schema.py             # Pydantic schemas for data validation
├── models/
│   ├── jobs.py           # Database model for jobs
│   └── dbcontext/
│       └── dbcontext.py  # Database context manager
├── services/
│   └── upwork_service.py # Main service for Upwork API interaction
└── queries/
    └── market_place_job.py # GraphQL queries
```

## Database Schema

The tool creates a `job` table with the following key fields:

- **Basic Info**: `id`, `title`, `description`, `category`
- **Budget**: `amount_raw_value`, `amount_currency`, `hourly_budget_min/max`
- **Requirements**: `skills`, `experience_level`, `duration`
- **Client Info**: `client_total_hires`, `client_total_spent`, `client_location_*`
- **Timestamps**: `created_date_time`, `published_date_time`

## Configuration Files

The tool stores configuration in `~/.upwork_fetcher/config.json`:

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret", 
  "redirect_uri": "your_redirect_uri",
  "access_token": "...",
  "refresh_token": "...",
  "code": "...",
  "db_url": "postgresql://..."
}
```

## Search Expressions

The tool supports Upwork's search syntax including:

- **Keywords**: `"python developer"`
- **Skills**: `"react AND typescript"`
- **Boolean operators**: `"(python OR django) AND NOT wordpress"`
- **Phrases**: `"machine learning engineer"`

## Error Handling

- **Authentication**: Automatically refreshes access tokens when expired
- **Database**: Validates database URL format and connectivity
- **API Errors**: Graceful handling of API rate limits and errors
- **Duplicates**: Prevents storing duplicate job entries

## Development

### Setting up for Development

```bash
# Clone repository
git clone <repository-url>
cd upwork-automation-cli

# Install dependencies with dev tools
poetry install --with dev

# Run tests
poetry run pytest

# Format code
poetry run black .

# Type checking
poetry run mypy .
```

### Building and Publishing

```bash
# Update version
poetry version [patch | minor | major]

# Build package
poetry build

# Publish to PyPI
poetry publish
```

## Deployment Instructions

```bash
# Update version
poetry version [patch | minor | major]

# Create git tag
git tag v$(poetry version -s)

# Commit and push
git add .
git commit -m "Release v$(poetry version -s)"
git push origin main --tags
```

## Dependencies

- **click**: Command-line interface framework
- **requests**: HTTP client for API calls
- **gql**: GraphQL client
- **psycopg2-binary**: PostgreSQL adapter
- **tortoise-orm**: Async ORM for database operations
- **pydantic**: Data validation and settings
- **rich**: Rich text and beautiful formatting
- **python-dotenv**: Environment variable loading

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API credentials
   - Check if access token has expired (tool auto-refreshes)
   - Ensure redirect URI matches your Upwork app configuration

2. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database URL format
   - Ensure database exists and user has proper permissions

3. **No Jobs Found**
   - Try different search expressions
   - Check if search terms are too specific
   - Verify Upwork API is accessible

### Logging

Enable verbose mode to see detailed information:
```bash
upwork-fetcher fetch -s "python" --verbose
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational and legitimate job search purposes only. Please respect Upwork's Terms of Service and API usage guidelines. The authors are not responsible for any misuse of this tool.

## Support

For issues and questions:
- Check the troubleshooting section
- Review existing GitHub issues
- Create a new issue with detailed information

## Version History

- **0.1.15**: Current version with enhanced error handling and type hinting
- **0.1.14**: Improved job schema conversion with error handling  
- Previous versions: Various bug fixes and feature enhancements
