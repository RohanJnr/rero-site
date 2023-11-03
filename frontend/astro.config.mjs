import { defineConfig } from 'astro/config';
import node from "@astrojs/node";
import tailwind from "@astrojs/tailwind";
import solidJs from "@astrojs/solid-js";

import vercel from "@astrojs/vercel/serverless";

// https://astro.build/config
export default defineConfig({
  output: "server",
  adapter: vercel(),
  integrations: [tailwind(), solidJs()]
});