import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "horse-breed-microservice"


def test_get_all_horse_breeds():
    """Test getting all horse breeds"""
    response = client.get("/api/v1/horse-breeds/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # Sample data has 3 breeds
    
    # Check structure of first breed
    breed = data[0]
    required_fields = ["id", "name", "origin", "height_min", "height_max", 
                      "weight_min", "weight_max", "temperament", "colors"]
    for field in required_fields:
        assert field in breed


def test_get_horse_breed_by_id():
    """Test getting a horse breed by ID"""
    response = client.get("/api/v1/horse-breeds/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data


def test_get_horse_breed_not_found():
    """Test getting a non-existent horse breed"""
    response = client.get("/api/v1/horse-breeds/999")
    assert response.status_code == 404


def test_search_horse_breeds():
    """Test searching horse breeds by name"""
    response = client.get("/api/v1/horse-breeds/search?name=Arabian")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any("Arabian" in breed["name"] for breed in data)


def test_create_horse_breed():
    """Test creating a new horse breed"""
    new_breed = {
        "name": "Mustang",
        "origin": "United States",
        "height_min": 14.0,
        "height_max": 15.0,
        "weight_min": 700,
        "weight_max": 900,
        "temperament": "spirited",
        "colors": ["bay", "black", "chestnut"],
        "description": "Wild horses of the American West"
    }
    
    response = client.post("/api/v1/horse-breeds/", json=new_breed)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mustang"
    assert data["id"] is not None


def test_update_horse_breed():
    """Test updating an existing horse breed"""
    update_data = {
        "description": "Updated description for Arabian horses"
    }
    
    response = client.put("/api/v1/horse-breeds/1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description for Arabian horses"


def test_update_horse_breed_not_found():
    """Test updating a non-existent horse breed"""
    update_data = {"description": "Test"}
    response = client.put("/api/v1/horse-breeds/999", json=update_data)
    assert response.status_code == 404


def test_delete_horse_breed():
    """Test deleting a horse breed"""
    # First create a breed to delete
    new_breed = {
        "name": "Test Breed",
        "origin": "Test",
        "height_min": 14.0,
        "height_max": 15.0,
        "weight_min": 800,
        "weight_max": 1000,
        "temperament": "calm",
        "colors": ["brown"]
    }
    
    create_response = client.post("/api/v1/horse-breeds/", json=new_breed)
    breed_id = create_response.json()["id"]
    
    # Now delete it
    delete_response = client.delete(f"/api/v1/horse-breeds/{breed_id}")
    assert delete_response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/horse-breeds/{breed_id}")
    assert get_response.status_code == 404


def test_delete_horse_breed_not_found():
    """Test deleting a non-existent horse breed"""
    response = client.delete("/api/v1/horse-breeds/999")
    assert response.status_code == 404