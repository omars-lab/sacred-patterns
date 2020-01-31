# TODO: Tinker with Multiphase build process ...
# one container to install make, eslint, ts, webpack, ... to build the site ...
# the other with essentials to only run site ...

FROM node:10 AS builder
WORKDIR /code
COPY package.json ./
RUN npm install -D
COPY . .
RUN npm run build
# Get rid of the dev node modules and install the prod ones since these should get copied into the prod container ...
RUN rm -rf node_modules/ && npm install --only=prod

FROM node:10
WORKDIR /site/
COPY --from=builder /code/site/ ./site/
COPY --from=builder /code/app/ ./app/
COPY --from=builder /code/node_modules/ ./app/node_modules/
ENTRYPOINT ["node", "app/runner.js"]
