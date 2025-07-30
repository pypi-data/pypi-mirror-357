# Python Substack

A Python wrapper around the Substack API for creating, managing, and publishing posts programmatically.

## Features

- 🚀 Create and publish posts to Substack
- 📝 Support for draft posts
- 📊 Get subscriber count and analytics
- 🖼️ Image upload support
- ⏰ Post scheduling functionality
- 🔐 Authentication handling
- 🛡️ Rate limiting protection

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/TarunVedula/python-substack.git
cd python-substack

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
pip install python-substack
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/TarunVedula/python-substack.git
cd python-substack

# Install in development mode
pip install -e .
```

## Quick Start

### 1. Set up Authentication

Create a `.env` file in your project directory:

```env
EMAIL=your-email@example.com
PASSWORD=your-password
PUBLICATION_URL=https://your-publication.substack.com
```

### 2. Basic Usage

```python
from substack import Api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the API client
api = Api(
    email=os.getenv("EMAIL"),
    password=os.getenv("PASSWORD"),
    publication_url=os.getenv("PUBLICATION_URL")
)

# Get subscriber count
subscriber_count = api.get_publication_subscriber_count()
print(f"Current subscribers: {subscriber_count}")

# Get published posts
posts = api.get_published_posts(limit=5)
for post in posts:
    print(f"Post: {post['title']}")
```

## Examples

### Getting Subscriber Count

```python
from substack import Api

api = Api(
    email="your-email@example.com", 
    password="your-password",
    publication_url="https://your-publication.substack.com"
)

subscriber_count = api.get_publication_subscriber_count()
print(f"You have {subscriber_count} subscribers")
```

### Creating and Publishing a Draft

```python
from substack import Api

api = Api(
    email="your-email@example.com", 
    password="your-password",
    publication_url="https://your-publication.substack.com"
)

# Create a new draft
draft_data = {
    "title": "Hello World",
    "subtitle": "A test post",
    "body": "# Hello World\n\nThis is a test post created with python-substack.",
    "section_id": None
}

draft = api.post_draft(draft_data)
print(f"Draft created: {draft['id']}")

# Publish the draft
published_post = api.publish_draft(draft, send=True)
print(f"Published: {published_post['url']}")
```

### Working with Drafts

```python
# Get all drafts
drafts = api.get_drafts()

# Get a specific draft
draft = api.get_draft(draft_id)

# Update a draft
updated_draft = api.put_draft(draft, title="Updated Title")

# Delete a draft
api.delete_draft(draft_id)
```

### Scheduling Posts

```python
from datetime import datetime

# Schedule a draft for later publication
schedule_time = datetime(2024, 2, 1, 10, 0, 0)  # Feb 1, 2024 at 10 AM
scheduled = api.schedule_draft(draft, schedule_time)

# Unschedule a draft
api.unschedule_draft(draft)
```

## API Reference

### Api Class

#### Methods

- `get_publication_subscriber_count()`: Get current subscriber count
- `get_published_posts(offset=0, limit=25, order_by="post_date", order_direction="desc")`: Get published posts
- `get_drafts(filter=None, offset=None, limit=None)`: Get all drafts
- `get_draft(draft_id)`: Get a specific draft
- `post_draft(body)`: Create a new draft
- `put_draft(draft, **kwargs)`: Update a draft
- `publish_draft(draft, send=True, share_automatically=False)`: Publish a draft
- `schedule_draft(draft, draft_datetime)`: Schedule a draft for later publication
- `unschedule_draft(draft)`: Unschedule a draft
- `delete_draft(draft_id)`: Delete a draft
- `get_user_profile()`: Get user profile information
- `get_user_publications()`: Get all user publications
- `get_user_primary_publication()`: Get the primary publication

#### Draft Data Structure

```python
draft_data = {
    "title": str,           # Required: Post title
    "subtitle": str,        # Optional: Post subtitle
    "body": str,           # Required: Post content (supports Markdown)
    "section_id": int,     # Optional: Section ID
    "tags": list,          # Optional: List of tags
    "published": bool      # Optional: Whether to publish immediately
}
```

## Configuration

### Environment Variables

- `EMAIL`: Your Substack email address
- `PASSWORD`: Your Substack password
- `PUBLICATION_URL`: Your publication URL (e.g., https://your-publication.substack.com)

### Authentication Options

You can authenticate in two ways:

1. **Email/Password**: Provide email and password directly
2. **Cookies**: Save and reuse cookies for persistent sessions

```python
# Using cookies for persistent authentication
api = Api(cookies_path="cookies.json")

# Export cookies for later use
api.export_cookies("cookies.json")
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/TarunVedula/python-substack.git
cd python-substack

# Install dependencies
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest
```

### Running Tests

```bash
python -m pytest
```

### Code Quality

This project uses:
- **Poetry** for dependency management
- **pytest** for testing
- **pre-commit** for code quality hooks
- **GitHub Actions** for CI/CD

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thank you @Paolo Mazza for Project Inspo
- Substack API for providing the underlying service


**Note**: This library is not officially affiliated with Substack. Use at your own risk and in accordance with Substack's terms of service. 
