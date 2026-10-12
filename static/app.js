// Browser checks (the server repeats the same rules in app.py).

// Show a list of messages in the red box next to the form
function showErrors(form, errors) {
  const box = (form.closest(".scope") || form).querySelector(".errors");
  box.innerHTML = errors.map(e => "<li>" + e + "</li>").join("");
  box.hidden = errors.length === 0;
}

function checkRegister(f) {
  const errors = [];
  if (f.name.value.trim() === "") errors.push("Name is required");
  if (f.email.value.trim() === "") errors.push("Email is required");
  if (f.password.value === "") errors.push("Password is required");
  if (f.confirm_password.value === "") errors.push("Confirm password is required");
  if (f.password.value && f.confirm_password.value && f.password.value !== f.confirm_password.value)
    errors.push("Passwords do not match");
  return errors;
}

function checkLogin(f) {
  const errors = [];
  if (f.email.value.trim() === "") errors.push("Email is required");
  if (f.password.value === "") errors.push("Password is required");
  return errors;
}

function checkTodo(f) {
  const title = f.title.value;
  if (title.trim() === "") return ["Title is required"];
  if (title.length > 200) return ["Title is too long (200 characters at most)"];
  return [];
}

const checks = { register: checkRegister, login: checkLogin, todo: checkTodo };

// Every form with data-form="..." is checked before it is sent
document.querySelectorAll("form[data-form]").forEach(form => {
  form.addEventListener("submit", event => {
    const errors = checks[form.dataset.form](form);
    if (errors.length > 0) {
      event.preventDefault();   // nothing is sent
      showErrors(form, errors);
    }
  });
});

// "Are you sure?" before deleting
document.querySelectorAll("form[data-confirm]").forEach(form => {
  form.addEventListener("submit", event => {
    if (!confirm(form.dataset.confirm)) event.preventDefault();
  });
});

// Light / dark mode button. The choice is remembered in the browser (localStorage).
const themeButton = document.getElementById("theme-toggle");

function currentTheme() {
  // the chosen theme, or the system setting if nothing was chosen yet
  return document.documentElement.dataset.theme ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
}

function updateThemeButton() {
  themeButton.textContent = currentTheme() === "dark" ? "☀️" : "🌙";   // shows what you switch to
}

themeButton.addEventListener("click", () => {
  const next = currentTheme() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("theme", next); } catch (e) {}
  updateThemeButton();
});

updateThemeButton();
