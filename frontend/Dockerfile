# ── ETAPA 1: Build ─────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

# Las variables de entorno de Vite se embeben en el build
# Por eso las pasamos como ARG en tiempo de build, no como ENV en runtime
ARG VITE_API_URL
ARG VITE_STRIPE_PUBLIC_KEY
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# ── ETAPA 2: Producción con Nginx ──────────────────────────
FROM nginx:alpine AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]