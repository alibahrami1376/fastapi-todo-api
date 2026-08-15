LOGIN
  ↓
Access A + Refresh A
  ↓
Session
  ├── access_jti = A
  └── refresh_jti = A


REFRESH
  ↓
Refresh A
  ↓
find Session by refresh_jti
  ↓
Refresh A → revoked
  ↓
Access B + Refresh B
  ↓
همان Session با JTIهای جدید


LOGOUT
  ↓
Access B
  ↓
find Session by access_jti
  ↓
access_revoked_at = now
refresh_revoked_at = now
  ↓
❌ Session 