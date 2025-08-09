"""
URL configuration for waterme project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.utils.safestring import mark_safe

def api_documentation(request):
    html = """
    <html>
    <head>
        <title>WaterMe API Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #333; }
            h2 { color: #555; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 5px; }
            code { font-family: Consolas, monospace; }
        </style>
    </head>
    <body>
        <h1>WaterMe API Documentation</h1>
        <p>Welcome to the WaterMe API documentation. This API provides endpoints for user registration, authentication, and profile management.</p>

        <h2>Base URL</h2>
        <p><code>https://waterme-be.onrender.com/api/</code> (or <code>http://localhost:8000/api/</code> for local development)</p>

        <h2>Endpoints</h2>

        <h3>1. Register User</h3>
        <p><strong>POST /auth/register/</strong></p>
        <p>Creates a new user account.</p>
        <p><strong>Request Body</strong> (application/json):</p>
        <pre><code>
{
    "username": "string",
    "email": "string",
    "password": "string",
    "user_type": "string",
    "phone_number": "string (optional)",
    "address": "string (optional)",
    "latitude": number (optional),
    "longitude": number (optional)
}
        </code></pre>
        <p><strong>Response</strong> (201 Created):</p>
        <pre><code>
{
    "id": integer,
    "username": "string",
    "email": "string",
    "user_type": "string",
    "phone_number": "string",
    "address": "string",
    "latitude": number,
    "longitude": number
}
        </code></pre>
        <p><strong>Error Response</strong> (400 Bad Request):</p>
        <pre><code>
{
    "field_name": ["error message"]
}
        </code></pre>

        <h3>2. Login</h3>
        <p><strong>POST /auth/login/</strong></p>
        <p>Authenticates a user and returns JWT tokens.</p>
        <p><strong>Request Body</strong> (application/json):</p>
        <pre><code>
{
    "username": "string",
    "password": "string"
}
        </code></pre>
        <p><strong>Response</strong> (200 OK):</p>
        <pre><code>
{
    "refresh": "string",
    "access": "string",
    "user": {
        "id": integer,
        "username": "string",
        "email": "string",
        "user_type": "string",
        "phone_number": "string",
        "address": "string",
        "latitude": number,
        "longitude": number
    }
}
        </code></pre>
        <p><strong>Error Response</strong> (401 Unauthorized):</p>
        <pre><code>
{
    "error": "Invalid credentials"
}
        </code></pre>

        <h3>3. Profile</h3>
        <p><strong>GET /auth/profile/</strong></p>
        <p>Retrieves the authenticated user's profile.</p>
        <p><strong>Headers</strong>:</p>
        <pre><code>
Authorization: Bearer &lt;access_token&gt;
        </code></pre>
        <p><strong>Response</strong> (200 OK):</p>
        <pre><code>
{
    "id": integer,
    "username": "string",
    "email": "string",
    "user_type": "string",
    "phone_number": "string",
    "address": "string",
    "latitude": number,
    "longitude": number
}
        </code></pre>

        <p><strong>PUT /auth/profile/</strong></p>
        <p>Updates the authenticated user's profile (partial updates allowed).</p>
        <p><strong>Headers</strong>:</p>
        <pre><code>
Authorization: Bearer &lt;access_token&gt;
Content-Type: application/json
        </code></pre>
        <p><strong>Request Body</strong> (application/json):</p>
        <pre><code>
{
    "phone_number": "string (optional)",
    "address": "string (optional)",
    "latitude": number (optional),
    "longitude": number (optional)
}
        </code></pre>
        <p><strong>Response</strong> (200 OK):</p>
        <pre><code>
{
    "id": integer,
    "username": "string",
    "email": "string",
    "user_type": "string",
    "phone_number": "string",
    "address": "string",
    "latitude": number,
    "longitude": number
}
        </code></pre>
        <p><strong>Error Response</strong> (400 Bad Request):</p>
        <pre><code>
{
    "field_name": ["error message"]
}
        </code></pre>

        <h2>Authentication</h2>
        <p>The API uses JWT (JSON Web Tokens) for authentication. Obtain an access token via the <code>/auth/login/</code> endpoint and include it in the <code>Authorization</code> header for protected endpoints (e.g., <code>/auth/profile/</code>).</p>
        <p>Example:</p>
        <pre><code>
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
        </code></pre>

        <h2>Testing the API</h2>
        <p>Use tools like Postman or curl to test the API. Example curl commands:</p>
        <pre><code>
# Register
curl -X POST https://waterme-be.onrender.com/api/auth/register/ \
-H "Content-Type: application/json" \
-d '{"username":"testuser","email":"testuser@example.com","password":"securepassword123","user_type":"customer","phone_number":"1234567890","address":"123 Test St","latitude":6.5244,"longitude":3.3792}'

# Login
curl -X POST https://waterme-be.onrender.com/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{"username":"testuser","password":"securepassword123"}'

# Get Profile
curl -X GET https://waterme-be.onrender.com/api/auth/profile/ \
-H "Authorization: Bearer &lt;access_token&gt;"
        </code></pre>
    </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path('', api_documentation, name='api_documentation'),  # Root URL for documentation
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
]