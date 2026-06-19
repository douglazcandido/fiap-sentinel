# =========================================================
# STAGE 1 - build da aplicacao React/Vite
# =========================================================
FROM node:20-slim AS build

WORKDIR /app

# copia apenas os manifestos primeiro para aproveitar cache de layers do Docker
COPY package.json package-lock.json* pnpm-lock.yaml* ./

# instala dependencias (detecta automaticamente npm ou pnpm pelo lockfile presente)
RUN if [ -f pnpm-lock.yaml ]; then \
        npm install -g pnpm && pnpm install --frozen-lockfile; \
    else \
        npm ci; \
    fi

# copia o restante do codigo fonte
COPY . .

# argumento de build para a URL da API (pode ser sobrescrito no build)
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# gera o build de producao (arquivos estaticos em /app/dist)
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm run build; \
    else \
        npm run build; \
    fi

# =========================================================
# STAGE 2 - servidor estatico Nginx, enxuto, so com o build final
# =========================================================
FROM nginx:1.27-alpine AS production

# remove a configuracao default do nginx
RUN rm /etc/nginx/conf.d/default.conf

# copia configuracao customizada (necessaria para SPA com React Router)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# copia somente os arquivos estaticos gerados no stage de build
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
