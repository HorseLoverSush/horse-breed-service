Project Name: HorseLover Platform

Description:
HorseLover is a multi-microservice platform for horse enthusiasts. It provides information about horse breeds, stable management, horse accessories, and user management. The platform will have separate frontend apps for different microservices and centralized configuration for managing environments and secrets.

Architecture Overview:
- Multi-repo approach
- Microservices:
  - horse-breed
  - horse-stable
  - horse-accessories
  - user-service (user management)
- Frontend Apps:
  - horse-breeds (frontend)
  - horse-stable (frontend)
- Platform configuration:
  - config
  - vault (for secrets)

Databases:
1. horse_breeds_db
   - Tables: countries, breeds
2. horse_stable_db
   - Tables: horses, horse_health
3. horse_accessories_db
   - Tables: categories, accessories, reviews
4. user_db
   - Tables: users, user_preferences

Sample Data: Provided for all tables across all microservices to start testing APIs.

Key Notes:
- Microservices use FastAPI (Python) for backend.
- PostgreSQL for databases; each microservice has its own DB.
- Users are managed by the user-service; other services reference users via API (owner_id).
- Countries data is static and stored in horse_breeds_db.
- Frontend apps will interact with respective microservices APIs.
- Docker containers are used for local setup.
- GitHub organization will host all repositories as private initially.
- Repositories structured as:
  - microservices/
      horse-breed
      horse-stable
      horse-accessories
      user-service
  - platform/
      config
      vault
  - frontend-app/
      horse-stable
      horse-breeds
- Future considerations: CI/CD workflows, branch strategies (main, develop, feature branches), protected branches, secrets management.

APIs expected:
- horse-breed service: CRUD for breeds and countries.
- horse-stable service: CRUD for horses and horse_health; reference breed_id and owner_id.
- horse-accessories service: CRUD for categories, accessories, reviews.
- user-service: CRUD for users and preferences, authentication, roles.

Frontend apps:
- Consume respective microservice APIs.
- Display data, manage forms, etc.

Docker:
- Each microservice and DB is containerized.
- Local setup uses exposed ports, volumes for persistent data.

Goal:
Provide GitHub Copilot with this context to help generate FastAPI code for all microservices, including models, CRUD endpoints, database interactions, and initial sample data handling.

