# Inventory Management System

A Python-based command-line inventory management system that helps businesses track products, manage inventory levels, handle sales, and generate reports.

## Features

- Product Management: Add, update, and remove products
- Inventory Tracking: Monitor stock levels and set reorder points
- Sales Management: Record sales and track revenue
- Reporting: Generate inventory and sales reports
- Data Persistence: SQLite database for reliable data storage

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the main application:
```bash
python main.py
```

## Project Structure

- `main.py`: Application entry point
- `database.py`: Database connection and operations
- `models/`: Data models and business logic
  - `product.py`: Product management
  - `inventory.py`: Inventory tracking
  - `sales.py`: Sales management
- `utils/`: Utility functions and helpers
- `reports/`: Report generation modules

## License

MIT License 