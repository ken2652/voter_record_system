# Voter Record Management System

A comprehensive web application for managing voter records, built with Flask and MySQL. The system provides an efficient way to store, manage, and retrieve voter information with features like search, filtering, and data export capabilities.

## Features

- **User-friendly Interface**: Clean and responsive design using Bootstrap 5
- **Voter Management**: Add, edit, view, and delete voter records
- **Advanced Search**: Search by name, barangay, sitio, or precinct number
- **Data Export**: Export search results to Excel format
- **Photo Management**: Upload and manage voter photos
- **Dynamic Filtering**: Barangay-Sitio relationship management
- **Data Visualization**: Charts and statistics on the dashboard
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voter-record-system.git
cd voter-record-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a MySQL database:
```sql
CREATE DATABASE voter_records;
```

5. Configure the database connection:
   - Create a `.env` file in the project root
   - Add the following configuration (modify as needed):
```
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=voter_records
SECRET_KEY=your-secret-key-here
```

6. Initialize the database:
```bash
mysql -u your_username -p voter_records < db/schema.sql
```

## Running the Application

1. Start the Flask development server:
```bash
python run.py
```

2. Access the application:
   - Open a web browser and navigate to `http://localhost:5000`
   - Log in with the default admin credentials (if configured)

## Project Structure

```
voter_record_system/
│── app.py                   # Main Flask application
│── config.py               # Configuration settings
│── requirements.txt        # Python dependencies
│── run.py                 # Application entry point
│
├── static/                # Static files
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
├── templates/             # HTML templates
│   ├── layout.html
│   ├── index.html
│   ├── add_record.html
│   ├── edit_record.html
│   ├── view_record.html
│   ├── search.html
│   └── search_results.html
│
└── db/                   # Database files
    ├── connection.py
    └── schema.sql
```

## Usage

1. **Adding a Voter**
   - Click "Add Voter" in the navigation menu
   - Fill in the required information
   - Upload a photo (optional)
   - Click "Save Record"

2. **Searching Records**
   - Use the search page to find voters
   - Filter by name, barangay, sitio, or status
   - Export results to Excel

3. **Managing Records**
   - View complete voter details
   - Edit information as needed
   - Delete records (requires confirmation)

4. **Exporting Data**
   - Search for desired records
   - Click "Export to Excel"
   - Save the generated file

## Security Features

- Password hashing for user authentication
- CSRF protection for forms
- Input validation and sanitization
- Secure file upload handling
- Role-based access control

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please create an issue in the GitHub repository or contact the development team.

## Acknowledgments

- Flask framework
- Bootstrap for UI components
- Chart.js for data visualization
- MySQL for database management 