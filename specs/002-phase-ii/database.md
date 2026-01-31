# Database Schema & Prisma Configuration

## 1. Database Specifications
- **Provider:** Neon (Serverless PostgreSQL)
- **Schema Management:** Prisma (TypeScript version in Frontend acts as Primary).

## 2. The Schema (`schema.prisma`)
The following schema defines the core Identity models (Better-Auth standard) and the Business Logic models (Todo App).

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

// --- Better Auth Core Models ---

model User {
  id            String    @id @default(cuid())
  name          String
  email         String    @unique
  emailVerified Boolean   @default(false)
  image         String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  sessions      Session[]
  accounts      Account[]
  
  // Relation to Business Logic
  tasks         Task[]

  @@map("user") // Lowercase map is safer for Postgres convention consistency
}

model Session {
  id        String   @id @default(cuid())
  userId    String
  token     String   @unique
  expiresAt DateTime
  ipAddress String?
  userAgent String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("session")
}

model Account {
  id                    String    @id @default(cuid())
  userId                String
  accountId             String
  providerId            String
  accessToken           String?
  refreshToken          String?
  accessTokenExpiresAt  DateTime?
  refreshTokenExpiresAt DateTime?
  password              String?   // For email/password auth
  createdAt             DateTime  @default(now())
  updatedAt             DateTime  @updatedAt
  user                  User      @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("account")
}

model Verification {
  id         String   @id @default(cuid())
  identifier String
  value      String
  expiresAt  DateTime
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  @@map("verification")
}

// --- Todo Application Business Models ---

enum TaskStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
}

enum Priority {
  HIGH
  MEDIUM
  LOW
}

model Task {
  id          String   @id @default(cuid())
  title       String
  description String?
  status      TaskStatus @default(PENDING)
  priority    Priority   @default(MEDIUM)
  
  // Organization
  tags        String[]
  dueDate     DateTime?

  // Ownership (CRITICAL: Every task MUST belong to a user)
  userId      String
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@index([userId]) // Performance optimization for "Get My Tasks"
  @@map("task")
}
```

## 3. CLI Commands Reference
- **Push Schema changes to Neon:**
  `npx prisma db push`
- **Generate Client (Frontend):**
  `npx prisma generate`
- **Studio (Visual Editor):**
  `npx prisma studio`

## 4. Resources
- [Prisma Schemas Reference](https://www.prisma.io/docs/concepts/components/prisma-schema)
- [Better-Auth Prisma Adapter](https://www.better-auth.com/docs/adapters/prisma)
- [Neon Database Connection](https://neon.tech/docs/connect/connect-from-any-app)
