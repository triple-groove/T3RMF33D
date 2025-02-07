# T3RMF33D

A social feed that centers around simplicity and terminal like look.

## Features

### Core Functionality
- Create text posts with media attachments (images and videos)
- Automatic YouTube video embedding in posts
- Threaded comments/replies on posts
- User profile pages with post history
- Edit and delete your own content

### User Interface
- Classic terminal aesthetic with green text on black background
- Retro "Press Start 2P" pixel font
- Responsive design that maintains the old-school feel
- Clean, intuitive navigation

### Security & User Management
- Secure user authentication system
- Password hashing for enhanced security
- Invitation-only registration system
- Admin privileges for content moderation

### Media Support
- Image uploads (PNG, JPG, JPEG, GIF)
- Video uploads (MP4, WebM)
- Automatic YouTube link embedding
- Secure media file handling

### Admin Features
- Generate invitation tokens for new users
- Delete any post or comment
- User management capabilities
- Admin dashboard for system overview

## Technical Requirements

- Python 3.x
- Flask web framework
- SQLite database
- Modern web browser
- Internet connection (for font loading and YouTube embeds)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/t3rmf33d.git
   cd t3rmf33d
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Start the application:
   ```bash
   python app.py
   ```

## First-Time Setup

1. The first user to register automatically becomes an admin
2. Subsequent users need an invitation token to register
3. Admin users can generate invitation tokens from the admin dashboard
4. Share tokens securely with new users

## Usage

1. Visit `http://localhost:5000` in your web browser
2. Register an account (or log in if you have one)
3. Create posts, upload media, or comment on existing posts
4. Use the navigation menu to explore different sections
5. Admins can access the dashboard through the admin panel

## Security Notes

- Change the `SECRET_KEY` in `app.py` before deploying
- Keep invitation tokens secure and private
- Regular backups of the SQLite database are recommended
- Configure proper file upload limits for your environment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers directly.