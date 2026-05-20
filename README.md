# Restaurant OMS

Restaurant OMS is a Django-based restaurant operations application with customer ordering flows, account management, payments, delivery tracking, and reporting.

## Local stack

- Python 3.14 with Pipenv
- PostgreSQL as the only database backend
- Node.js/npm for Tailwind asset builds
- Optional Redis/Celery services for async workloads

## Local setup

1. Install Python dependencies:

   ```bash
   pipenv install --dev
   ```

2. Install frontend build dependencies:

   ```bash
   npm --prefix apps/theme/static_src install
   ```

   To rebuild the Tailwind/DaisyUI stylesheet on demand:

   ```bash
   npm run build-css-prod
   ```

3. Ensure `.env` exists. The project auto-loads it from `config/settings.py`.

4. Ensure PostgreSQL is running locally with this connection:

   ```env
   DB_CONNECTION={"dbname":"postgres","username":"postgres","password":"postgres","host":"localhost","port":5432}
   ```

5. Apply migrations:

   ```bash
   pipenv run python manage.py migrate
   ```

6. Verify Django configuration:

   ```bash
   pipenv run python manage.py check
   ```

7. Start the development server:

   ```bash
   pipenv run python manage.py runserver
   ```

8. Open the app at `http://127.0.0.1:8000/`.

## Demo accounts

- Customer: `customer@example.com` / `password123`
- Admin: `admin@example.com` / `password123`

## Notes for local development

- Stripe is treated as disabled unless the active public and secret keys are real.
- Khalti is disabled in the checked-in local `.env`.
- In the current local environment, checkout is Cash on Delivery only.
- Social login buttons stay hidden until valid OAuth credentials are configured.

## Additional documentation

- [Workflow runbook](docs/workflows.md)
- [User manual](docs/manual/user-manual.md)
- [Bug log](docs/bugs-fixed.md)# django_template

To install dependencies:

```bash
bun install
```

To run:

```bash
bun run index.ts
```

This project was created using `bun init` in bun v1.3.5. [Bun](https://bun.com) is a fast all-in-one JavaScript runtime.
