# Application Flows

---

## 1. Register

```
Client
  │
  ├─ POST /api/v1/auth/register
  │   body: { email, password, confirm_password }
  │
  ▼
RegisterRequestSchema (Pydantic)
  ├─ email: valid EmailStr
  ├─ password: 8-72 chars, uppercase + lowercase + digit + special char
  └─ confirm_password == password  →  mismatch → 400

  ▼
AuthService.register()
  ├─ user_repo.get_by_email()  →  exists → 400 "email already exists"
  └─ user_repo.create_user()
       ├─ username: random generated
       └─ password: bcrypt hashed

  ▼
201 { user_id, email, detail }
```

---

## 2. Login + Fingerprint Binding

```
Client
  │
  ├─ POST /api/v1/auth/login
  │   body:    { email, password }
  │   headers: User-Agent, X-Forwarded-For / client IP
  │
  ▼
Route
  ├─ fingerprint = SHA256( client_ip + ":" + User-Agent )
  └─ AuthService.login(request, fingerprint_hash=fingerprint)

  ▼
AuthService.login()
  ├─ user_repo.get_by_email()  →  not found → 400
  ├─ user.verify_password()    →  wrong     → 400
  ├─ generate_access_token(user_id)
  │     payload: { type:"access", sub, jti, iat, exp }
  ├─ generate_refresh_token(user_id, fingerprint_hash)
  │     payload: { type:"refresh", sub, jti, iat, exp, fph: fingerprint }
  └─ session_repo.create()
       stores: access_jti, refresh_jti, expires_at (both)

  ▼
200 { access_token, refresh_token, token_type:"bearer" }
```

---

## 3. Authenticated Request (Access Token Validation)

```
Client
  │
  ├─ Any protected endpoint
  │   headers: Authorization: Bearer <access_token>
  │
  ▼
get_current_user (dependency)
  ├─ credentials is None          → 401
  ├─ decode_access_token(token)
  │     └─ wrong type / no sub / no jti / expired / bad sig → 401
  ├─ session_repo.get_by_access_token_jti(jti)
  │     └─ not found or access_revoked_at != NULL            → 401
  └─ user_repo.get_by_id(user_id)
        └─ not found or not is_active                        → 401

  ▼
current_user injected into route handler
```

---

## 4. Refresh Token Rotation + Fingerprint Validation

```
Client
  │
  ├─ POST /api/v1/auth/refresh
  │   headers: Authorization: Bearer <refresh_token>
  │            User-Agent, IP  (must match login)
  │
  ▼
Route
  ├─ credentials is None  → 401
  ├─ fingerprint = SHA256( client_ip + ":" + User-Agent )
  └─ AuthService.refresh_access_token(token, fingerprint_hash=fingerprint)

  ▼
AuthService.refresh_access_token()
  ├─ decode_refresh_token(token, fingerprint_hash)
  │     ├─ wrong type / expired / bad sig           → 401
  │     ├─ token.fph present AND fph != fingerprint → 401  ← fingerprint check
  │     └─ returns payload
  ├─ session_repo.get_by_refresh_token_jti(jti)
  │     └─ not found or refresh_revoked_at != NULL  → 401
  ├─ user_repo.get_by_id()
  │     └─ not found                                → 401
  ├─ session_repo.revoke_refresh_token()
  │     refresh_revoked_at = now
  ├─ generate_access_token(user_id)       ← new Access B
  ├─ generate_refresh_token(user_id, fph) ← new Refresh B  (carries fingerprint)
  └─ session_repo.create()  →  new session row (Access B jti, Refresh B jti)

  ▼
200 { access_token, refresh_token, token_type:"bearer" }

Note: old Refresh A is revoked; replaying it → 401
```

---

## 5. Logout

```
Client
  │
  ├─ POST /api/v1/auth/logout
  │   headers: Authorization: Bearer <access_token>
  │
  ▼
AuthService.logout()
  ├─ decode_access_token(token)                     → 401 on failure
  ├─ session_repo.get_by_access_token_jti(jti)
  │     └─ not found or already revoked             → 401
  ├─ session_repo.revoke_access_token()
  │     access_revoked_at = now
  └─ session_repo.revoke_refresh_token()
        refresh_revoked_at = now

  ▼
200 { detail: "You have been logged out successfully." }

Note: both tokens are dead; any further request with either → 401
```

---

## 6. Create Task

```
Client
  │
  ├─ POST /api/v1/todos
  │   headers: Authorization: Bearer <access_token>
  │   body: { title, description?, priority?, due_date? }
  │
  ▼
get_current_user  →  (see flow 3)

  ▼
TaskCreateSchema (Pydantic)
  ├─ title: 3-100 chars  (required)
  ├─ description: max 1000 chars (optional)
  ├─ priority: low | medium | high  (default: low)
  └─ due_date: date, must be today or future  (optional)

  ▼
TaskService.create_task(user_id, task)
  └─ task_repo.create_task()

  ▼
201 TaskResponseSchema
```

---

## 7. List Tasks (Search / Filter / Sort / Paginate)

```
Client
  │
  ├─ GET /api/v1/todos
  │   query params (all optional):
  │     q          – search in title + description (ILIKE)
  │     is_completed – true | false
  │     priority   – low | medium | high
  │     due_from   – date
  │     due_to     – date  (must be >= due_from)
  │     sort_by    – created_at | updated_at | due_date | priority | title
  │     order      – asc | desc  (default: desc)
  │     page       – >= 1  (default: 1)
  │     page_size  – 1-50  (default: 10)
  │
  ▼
TaskQuerySchema validation
  └─ due_to < due_from  → 422

  ▼
TaskService.get_tasks(user_id, params)
  └─ task_repo.get_tasks()
       ├─ _base_query()        filter: deleted_at IS NULL
       ├─ _apply_owner_filter  filter: owner_id == user_id
       ├─ _apply_search        ILIKE title OR description
       ├─ _apply_filters       is_completed, priority, due_from, due_to
       ├─ count()              total before pagination
       ├─ _apply_sorting       column.asc() / .desc()
       └─ _apply_pagination    OFFSET + LIMIT

  ▼
200 { results, page, page_size, total, pages }
```

---

## 8. Get / Update / Delete Single Task (404 vs 403)

```
Client
  │
  ├─ GET | PATCH | PUT | DELETE  /api/v1/todos/{id}
  │   headers: Authorization: Bearer <access_token>
  │
  ▼
TaskService.*_task(user_id, task_id)
  ├─ task_repo.get_by_id(task_id)
  │     └─ deleted_at IS NULL filter applied
  │     └─ None  →  TodoNotFoundException    → 404
  ├─ task.owner_id != user_id
  │     →  PermissionDeniedException         → 403
  └─ proceed with operation

PATCH  →  partial update (only fields present in body)
PUT    →  full replace (all fields required, including is_completed)
DELETE →  soft-delete (deleted_at = now, record stays in DB)
           GET after delete → 404
```

---

## 9. Exception Handling (Global)

```
Exception type                  Handler                  HTTP status
─────────────────────────────────────────────────────────────────────
BaseAppException                app_exception_handler
  ├─ TodoNotFoundException                                404
  ├─ PermissionDeniedException                           403
  ├─ AuthenticationException                             401
  └─ InvalidSortFieldException                           400

HTTPException                   http_exception_handler   as-is

RequestValidationError          validation_exception_handler
  ├─ sort_by field error                                 400
  └─ other validation errors                             422

Exception (catch-all)           unhandled_exception_handler  500

All error responses follow the shape:
  { "success": false, "error": { "code": "...", "message": "..." } }
```

---

## 10. Soft Delete

```
DELETE /api/v1/todos/{id}
  └─ task.deleted_at = datetime.now(utc)
       db.commit()

All read queries filter:  WHERE deleted_at IS NULL
→ soft-deleted tasks are invisible to the owner
→ task ID is still in DB (audit trail)
```

---

## 11. Session Lifecycle (summary)

```
Login
  └─ new session row
       access_jti  = A,  access_revoked_at  = NULL
       refresh_jti = A,  refresh_revoked_at = NULL

Refresh
  └─ refresh_revoked_at = now  (old row)
  └─ new session row
       access_jti  = B,  access_revoked_at  = NULL
       refresh_jti = B,  refresh_revoked_at = NULL

Logout
  └─ current session row
       access_revoked_at  = now
       refresh_revoked_at = now
```
