# Etap 1: Budowanie aplikacji
FROM node:20-alpine as build

WORKDIR /app

# Kopiowanie plików zależności
COPY package.json package-lock.json ./

# Instalacja zależności
RUN npm install

# Kopiowanie reszty kodu źródłowego
COPY . .

# Budowanie wersji produkcyjnej (tworzy katalog dist)
RUN npm run build

# Etap 2: Serwowanie aplikacji przez Nginx
FROM nginx:alpine

# Kopiowanie zbudowanych plików z etapu 1 do katalogu Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Opcjonalnie: Jeśli używasz React Router (tutaj masz SPA stanowe, ale warto dodać na przyszłość)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
