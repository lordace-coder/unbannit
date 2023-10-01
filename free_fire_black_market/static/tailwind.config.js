{
  import("tailwindcss").Config;
}
module.exports = {
  mode: "jit",
  prefix: "tw-",
  content: [
    "./src/**/*.css",
    "../core/templates/**/*.html",
    "../static/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
