/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		'./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}',
		'./node_modules/flowbite/**/*.js'
	],
	theme: {
		extend: {
			colors: {
				"bg-primary": "#EEE8F4",
				primary: "#DD5959",
				secondary: "#5D4779",
				"text-light": "#666666",
				"text-heading": "#282828",
			}
		},
	},
	plugins: [
		require('flowbite/plugin')
	],
}
