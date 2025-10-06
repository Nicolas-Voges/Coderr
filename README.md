# Coderr – Marketplace API

Coderr is a Django-based API for a marketplace that allows users to create offers, place orders, and submit reviews. The API supports role-based access control, custom permissions, and structured data modeling.

## Features

- **Role-Based Access Control**: Distinction between business and customer profiles.
- **Offer Management**: Create, update, and delete offers.
- **Order Management**: Place and manage orders.
- **Review System**: Customers can review business users.
- **User Profiles**: Manage user information and settings.
- **Dynamic Filtering**: Filter offers by price, delivery time, and search keywords.
- **Custom Pagination**: API endpoints support configurable pagination.

## Installation

### Requirements

- Python 3.9+
- Django 3.2+
- Django REST Framework
- PostgreSQL (or any other supported database)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/Nicolas-Voges/Coderr.git
   cd Coderr

2. Create a virtual environment:

   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: `env\Scripts\activate`

3. Install dependencies:

   ```bash
   pip install -r requirements.txt

4. Configure the database in settings.py.

5. Apply migrations:

   ```bash
   python manage.py migrate

6. Create a superuser:

   ```bash
   python manage.py createsuperuser

7. Start the development server:

   ```bash
   python manage.py runserver


## API Endpoints
### Offers

    
- GET /offers/: List all offers.

- POST /offers/: Create a new offer.

- GET /offers/{id}/: Retrieve a specific offer.

- PUT /offers/{id}/: Update a specific offer.

- DELETE /offers/{id}/: Delete an offer.


###  Order Management

- GET /orders/: List orders for the authenticated user.

- POST /orders/: Place a new order (customers only).

- PATCH /orders/{id}/: Update order status (business only).

- DELETE /orders/{id}/: Delete an order (admin only).

### Reviews

- GET /reviews/: List reviews for business or reviewer.

- POST /reviews/: Create a review (customers only).

- PATCH /reviews/{id}/: Update a review (review owner only).

- DELETE /reviews/{id}/: Delete a review (review owner only).

### Detail Retrieval

- GET /offerdetails/{id}/: Retrieve a single offer detail.

### Order Counts

- GET /order-count/{business_user_id}/: Count of in-progress orders.

- GET /completed-order-count/{business_user_id}/: Count of completed orders.

### Base Info

- GET /base-info/: Retrieve general statistics about reviews, offers, and business profiles.

## Testing

### Run the test suite using:

    python manage.py test

### Tests include:

- Offers

- Orders
  
- Reviews

- Base Info API
