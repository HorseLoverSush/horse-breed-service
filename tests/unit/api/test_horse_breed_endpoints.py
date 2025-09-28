"""
Unit tests for horse breed API endpoints.

Tests CRUD operations, validation, error handling,
and response formatting for horse breed endpoints.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.models.horse_breed import HorseBreed
from app.schemas.horse_breed import HorseBreedCreate, HorseBreedUpdate
from app.core.exceptions import (
    NotFoundError,
    ValidationError,
    DatabaseError
)


class TestHorseBreedEndpoints:
    """Test horse breed CRUD endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_breed_data(self):
        """Sample horse breed data for testing."""
        return {
            "name": "Thoroughbred",
            "origin": "England",
            "characteristics": {
                "size": "large",
                "temperament": "spirited",
                "uses": ["racing", "sport"]
            },
            "description": "A breed developed for racing and sport"
        }
    
    @pytest.fixture
    def sample_breed_model(self):
        """Sample horse breed model for testing."""
        return HorseBreed(
            id=1,
            name="Thoroughbred",
            origin="England",
            characteristics={
                "size": "large",
                "temperament": "spirited",
                "uses": ["racing", "sport"]
            },
            description="A breed developed for racing and sport"
        )


class TestGetBreeds:
    """Test GET /api/v1/breeds endpoint."""
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breeds')
    def test_get_breeds_success(self, mock_get_breeds, sample_breed_model):
        """Test successful retrieval of all breeds."""
        # Mock service response
        mock_get_breeds.return_value = [sample_breed_model]
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds")
        
        assert response.status_code == 200
        breeds = response.json()
        assert len(breeds) == 1
        assert breeds[0]["name"] == "Thoroughbred"
        assert breeds[0]["origin"] == "England"
        assert "id" in breeds[0]
        
        mock_get_breeds.assert_called_once_with(skip=0, limit=100)
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breeds')
    def test_get_breeds_with_pagination(self, mock_get_breeds):
        """Test breed retrieval with pagination parameters."""
        mock_get_breeds.return_value = []
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds?skip=10&limit=20")
        
        assert response.status_code == 200
        mock_get_breeds.assert_called_once_with(skip=10, limit=20)
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breeds')
    def test_get_breeds_empty_result(self, mock_get_breeds):
        """Test breed retrieval when no breeds exist."""
        mock_get_breeds.return_value = []
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds")
        
        assert response.status_code == 200
        breeds = response.json()
        assert breeds == []
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breeds')
    def test_get_breeds_database_error(self, mock_get_breeds):
        """Test breed retrieval with database error."""
        mock_get_breeds.side_effect = DatabaseError("Database connection failed")
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds")
        
        assert response.status_code == 500
        error_data = response.json()
        assert "detail" in error_data
        assert "correlation_id" in error_data
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breeds')
    def test_get_breeds_invalid_pagination(self, mock_get_breeds):
        """Test breed retrieval with invalid pagination parameters."""
        client = TestClient(app)
        
        # Test negative skip
        response = client.get("/api/v1/breeds?skip=-1")
        assert response.status_code == 422
        
        # Test zero limit
        response = client.get("/api/v1/breeds?limit=0")
        assert response.status_code == 422
        
        # Test excessive limit
        response = client.get("/api/v1/breeds?limit=1001")
        assert response.status_code == 422


class TestGetBreedById:
    """Test GET /api/v1/breeds/{breed_id} endpoint."""
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breed')
    def test_get_breed_success(self, mock_get_breed, sample_breed_model):
        """Test successful retrieval of breed by ID."""
        mock_get_breed.return_value = sample_breed_model
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds/1")
        
        assert response.status_code == 200
        breed = response.json()
        assert breed["id"] == 1
        assert breed["name"] == "Thoroughbred"
        assert breed["origin"] == "England"
        
        mock_get_breed.assert_called_once_with(1)
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breed')
    def test_get_breed_not_found(self, mock_get_breed):
        """Test retrieval of non-existent breed."""
        mock_get_breed.side_effect = HorseBreedNotFoundError("Breed not found")
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds/999")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "correlation_id" in error_data
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breed')
    def test_get_breed_invalid_id(self, mock_get_breed):
        """Test retrieval with invalid breed ID."""
        client = TestClient(app)
        
        # Test non-integer ID
        response = client.get("/api/v1/breeds/invalid")
        assert response.status_code == 422
        
        # Test negative ID
        response = client.get("/api/v1/breeds/-1")
        assert response.status_code == 422
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breed')
    def test_get_breed_database_error(self, mock_get_breed):
        """Test breed retrieval with database error."""
        mock_get_breed.side_effect = DatabaseError("Database query failed")
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds/1")
        
        assert response.status_code == 500
        error_data = response.json()
        assert "detail" in error_data


class TestCreateBreed:
    """Test POST /api/v1/breeds endpoint."""
    
    @patch('app.services.horse_breed_service.HorseBreedService.create_breed')
    def test_create_breed_success(self, mock_create_breed, sample_breed_data, sample_breed_model):
        """Test successful breed creation."""
        mock_create_breed.return_value = sample_breed_model
        
        client = TestClient(app)
        response = client.post("/api/v1/breeds", json=sample_breed_data)
        
        assert response.status_code == 201
        created_breed = response.json()
        assert created_breed["name"] == "Thoroughbred"
        assert created_breed["origin"] == "England"
        assert "id" in created_breed
        
        mock_create_breed.assert_called_once()
        call_args = mock_create_breed.call_args[0][0]
        assert call_args.name == "Thoroughbred"
        assert call_args.origin == "England"
    
    def test_create_breed_validation_errors(self):
        """Test breed creation with validation errors."""
        client = TestClient(app)
        
        # Test missing required fields
        response = client.post("/api/v1/breeds", json={})
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        
        # Test empty name
        invalid_data = {
            "name": "",
            "origin": "England",
            "characteristics": {},
            "description": "Test"
        }
        response = client.post("/api/v1/breeds", json=invalid_data)
        assert response.status_code == 422
        
        # Test name too long
        invalid_data = {
            "name": "x" * 201,  # Assuming max length is 200
            "origin": "England",
            "characteristics": {},
            "description": "Test"
        }
        response = client.post("/api/v1/breeds", json=invalid_data)
        assert response.status_code == 422
    
    @patch('app.services.horse_breed_service.HorseBreedService.create_breed')
    def test_create_breed_duplicate_name(self, mock_create_breed, sample_breed_data):
        """Test breed creation with duplicate name."""
        mock_create_breed.side_effect = ValidationError("Breed name already exists")
        
        client = TestClient(app)
        response = client.post("/api/v1/breeds", json=sample_breed_data)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data
    
    @patch('app.services.horse_breed_service.HorseBreedService.create_breed')
    def test_create_breed_database_error(self, mock_create_breed, sample_breed_data):
        """Test breed creation with database error."""
        mock_create_breed.side_effect = DatabaseError("Database insert failed")
        
        client = TestClient(app)
        response = client.post("/api/v1/breeds", json=sample_breed_data)
        
        assert response.status_code == 500
        error_data = response.json()
        assert "detail" in error_data
    
    def test_create_breed_invalid_json(self):
        """Test breed creation with invalid JSON."""
        client = TestClient(app)
        
        # Send invalid JSON
        response = client.post(
            "/api/v1/breeds",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_create_breed_complex_characteristics(self):
        """Test breed creation with complex characteristics."""
        complex_data = {
            "name": "Complex Breed",
            "origin": "Test Country",
            "characteristics": {
                "size": "medium",
                "height": {"min": 14, "max": 16, "unit": "hands"},
                "colors": ["bay", "chestnut", "black"],
                "temperament": {
                    "energy_level": "high",
                    "trainability": "excellent",
                    "social": True
                },
                "uses": ["dressage", "jumping", "trail riding"],
                "health": {
                    "common_issues": ["none"],
                    "lifespan": {"min": 25, "max": 30}
                }
            },
            "description": "A breed with complex characteristics"
        }
        
        with patch('app.services.horse_breed_service.HorseBreedService.create_breed') as mock_create:
            mock_breed = HorseBreed(id=1, **complex_data)
            mock_create.return_value = mock_breed
            
            client = TestClient(app)
            response = client.post("/api/v1/breeds", json=complex_data)
            
            assert response.status_code == 201
            created_breed = response.json()
            assert created_breed["characteristics"]["height"]["min"] == 14
            assert "dressage" in created_breed["characteristics"]["uses"]


class TestUpdateBreed:
    """Test PATCH /api/v1/breeds/{breed_id} endpoint."""
    
    @patch('app.services.horse_breed_service.HorseBreedService.update_breed')
    def test_update_breed_success(self, mock_update_breed, sample_breed_model):
        """Test successful breed update."""
        updated_breed = sample_breed_model
        updated_breed.description = "Updated description"
        mock_update_breed.return_value = updated_breed
        
        update_data = {"description": "Updated description"}
        
        client = TestClient(app)
        response = client.patch("/api/v1/breeds/1", json=update_data)
        
        assert response.status_code == 200
        updated = response.json()
        assert updated["description"] == "Updated description"
        
        mock_update_breed.assert_called_once()
        call_args = mock_update_breed.call_args
        assert call_args[0] == 1  # breed_id
        assert call_args[1].description == "Updated description"
    
    @patch('app.services.horse_breed_service.HorseBreedService.update_breed')
    def test_update_breed_not_found(self, mock_update_breed):
        """Test update of non-existent breed."""
        mock_update_breed.side_effect = NotFoundError("HorseBreed", "999")
        
        update_data = {"description": "Updated description"}
        
        client = TestClient(app)
        response = client.patch("/api/v1/breeds/999", json=update_data)
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
    
    def test_update_breed_partial_update(self):
        """Test partial breed update."""
        with patch('app.services.horse_breed_service.HorseBreedService.update_breed') as mock_update:
            # Mock the updated breed
            updated_breed = HorseBreed(
                id=1,
                name="Thoroughbred",
                origin="England",
                characteristics={"size": "large", "new_trait": "added"},
                description="Partially updated description"
            )
            mock_update.return_value = updated_breed
            
            # Only update characteristics
            update_data = {
                "characteristics": {"size": "large", "new_trait": "added"}
            }
            
            client = TestClient(app)
            response = client.patch("/api/v1/breeds/1", json=update_data)
            
            assert response.status_code == 200
            updated = response.json()
            assert updated["characteristics"]["new_trait"] == "added"
            assert updated["name"] == "Thoroughbred"  # Should remain unchanged
    
    def test_update_breed_validation_errors(self):
        """Test breed update with validation errors."""
        client = TestClient(app)
        
        # Test empty name
        update_data = {"name": ""}
        response = client.patch("/api/v1/breeds/1", json=update_data)
        assert response.status_code == 422
        
        # Test name too long
        update_data = {"name": "x" * 201}
        response = client.patch("/api/v1/breeds/1", json=update_data)
        assert response.status_code == 422
    
    @patch('app.services.horse_breed_service.HorseBreedService.update_breed')
    def test_update_breed_duplicate_name(self, mock_update_breed):
        """Test breed update with duplicate name."""
        mock_update_breed.side_effect = ValidationError("Breed name already exists")
        
        update_data = {"name": "Existing Breed Name"}
        
        client = TestClient(app)
        response = client.patch("/api/v1/breeds/1", json=update_data)
        
        assert response.status_code == 400
        error_data = response.json()
        assert "detail" in error_data


class TestDeleteBreed:
    """Test DELETE /api/v1/breeds/{breed_id} endpoint."""
    
    @patch('app.services.horse_breed_service.HorseBreedService.delete_breed')
    def test_delete_breed_success(self, mock_delete_breed):
        """Test successful breed deletion."""
        mock_delete_breed.return_value = True
        
        client = TestClient(app)
        response = client.delete("/api/v1/breeds/1")
        
        assert response.status_code == 204
        assert response.content == b""
        
        mock_delete_breed.assert_called_once_with(1)
    
    @patch('app.services.horse_breed_service.HorseBreedService.delete_breed')
    def test_delete_breed_not_found(self, mock_delete_breed):
        """Test deletion of non-existent breed."""
        mock_delete_breed.side_effect = NotFoundError("HorseBreed", "999")
        
        client = TestClient(app)
        response = client.delete("/api/v1/breeds/999")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
    
    @patch('app.services.horse_breed_service.HorseBreedService.delete_breed')
    def test_delete_breed_database_error(self, mock_delete_breed):
        """Test breed deletion with database error."""
        mock_delete_breed.side_effect = DatabaseError("Database delete failed")
        
        client = TestClient(app)
        response = client.delete("/api/v1/breeds/1")
        
        assert response.status_code == 500
        error_data = response.json()
        assert "detail" in error_data


class TestResponseFormat:
    """Test response format and headers."""
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breeds')
    def test_response_headers(self, mock_get_breeds, sample_breed_model):
        """Test response headers are correctly set."""
        mock_get_breeds.return_value = [sample_breed_model]
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        # Check for correlation ID if implemented
        if "X-Correlation-ID" in response.headers:
            assert len(response.headers["X-Correlation-ID"]) > 0
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breed')
    def test_error_response_format(self, mock_get_breed):
        """Test error response format consistency."""
        mock_get_breed.side_effect = NotFoundError("HorseBreed", "999")
        
        client = TestClient(app)
        response = client.get("/api/v1/breeds/999")
        
        assert response.status_code == 404
        error_data = response.json()
        
        # Standard error response format
        required_fields = ["detail", "correlation_id"]
        for field in required_fields:
            assert field in error_data
        
        assert isinstance(error_data["detail"], str)
        assert len(error_data["correlation_id"]) > 0
    
    def test_json_serialization(self):
        """Test JSON serialization of complex data types."""
        complex_data = {
            "name": "Test Breed",
            "origin": "Test Country",
            "characteristics": {
                "height": {"min": 14.2, "max": 16.1},
                "weight": {"min": 450, "max": 550},
                "colors": ["bay", "chestnut"],
                "is_endangered": False,
                "registration_date": "2024-01-01"
            },
            "description": "Test breed with complex data"
        }
        
        with patch('app.services.horse_breed_service.HorseBreedService.create_breed') as mock_create:
            mock_breed = HorseBreed(id=1, **complex_data)
            mock_create.return_value = mock_breed
            
            client = TestClient(app)
            response = client.post("/api/v1/breeds", json=complex_data)
            
            assert response.status_code == 201
            
            # Verify JSON can be parsed
            breed_data = response.json()
            assert isinstance(breed_data, dict)
            assert breed_data["characteristics"]["height"]["min"] == 14.2
            assert breed_data["characteristics"]["is_endangered"] is False


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async behavior of endpoints."""
    
    async def test_concurrent_breed_operations(self):
        """Test concurrent breed operations."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            with patch('app.services.horse_breed_service.HorseBreedService.get_breed') as mock_get:
                # Mock different breeds for concurrent requests
                mock_get.side_effect = [
                    HorseBreed(id=1, name="Breed1", origin="Country1", characteristics={}, description="Desc1"),
                    HorseBreed(id=2, name="Breed2", origin="Country2", characteristics={}, description="Desc2"),
                    HorseBreed(id=3, name="Breed3", origin="Country3", characteristics={}, description="Desc3")
                ]
                
                # Make concurrent requests
                tasks = [
                    client.get("/api/v1/breeds/1"),
                    client.get("/api/v1/breeds/2"),
                    client.get("/api/v1/breeds/3")
                ]
                
                responses = await asyncio.gather(*tasks)
                
                # All requests should succeed
                for response in responses:
                    assert response.status_code == 200
                
                # Check that different breeds were returned
                breed_names = [response.json()["name"] for response in responses]
                assert len(set(breed_names)) == 3  # All unique names


@pytest.mark.performance
class TestEndpointPerformance:
    """Performance tests for endpoints."""
    
    @patch('app.services.horse_breed_service.HorseBreedService.get_breeds')
    def test_get_breeds_performance(self, mock_get_breeds, performance_timer):
        """Test performance of get breeds endpoint."""
        # Mock large number of breeds
        breeds = [
            HorseBreed(id=i, name=f"Breed{i}", origin="Country", characteristics={}, description="Desc")
            for i in range(1000)
        ]
        mock_get_breeds.return_value = breeds
        
        client = TestClient(app)
        timer = performance_timer
        
        timer.start()
        response = client.get("/api/v1/breeds")
        elapsed = timer.stop()
        
        assert response.status_code == 200
        assert len(response.json()) == 1000
        
        # Should complete within reasonable time
        assert elapsed < 2.0  # Less than 2 seconds
    
    @patch('app.services.horse_breed_service.HorseBreedService.create_breed')
    def test_create_breed_performance(self, mock_create_breed, sample_breed_data, performance_timer):
        """Test performance of create breed endpoint."""
        mock_breed = HorseBreed(id=1, **sample_breed_data)
        mock_create_breed.return_value = mock_breed
        
        client = TestClient(app)
        timer = performance_timer
        
        timer.start()
        response = client.post("/api/v1/breeds", json=sample_breed_data)
        elapsed = timer.stop()
        
        assert response.status_code == 201
        
        # Should complete quickly
        assert elapsed < 1.0  # Less than 1 second