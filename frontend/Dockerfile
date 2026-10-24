# 1. Base Image
FROM node:20-alpine AS base
WORKDIR /app
RUN apk add --no-cache libc6-compat

# 2. Dependencies Stage
FROM base AS deps
COPY package.json package-lock.json ./
RUN npm ci

# 3. Builder Stage
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Argument to pass API URL during build time if needed
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# 4. Production Runner Stage (Minimal Alpine image)
FROM base AS runner
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy static and public assets
COPY --from=builder /app/public ./public

# Copy standalone build
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
