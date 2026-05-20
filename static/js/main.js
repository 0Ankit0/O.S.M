const OMS_THEME_KEY = "oms-theme";
const OMS_DEFAULT_THEME = document.documentElement.dataset.defaultTheme || "corporate";

function applyOmsTheme(themeName, persist = true) {
	const theme = themeName || OMS_DEFAULT_THEME;
	document.documentElement.setAttribute("data-theme", theme);

	if (persist) {
		try {
			localStorage.setItem(OMS_THEME_KEY, theme);
		} catch (error) {
			console.warn("Unable to persist theme selection.", error);
		}
	}

	syncOmsThemeControls(theme);
}

function readOmsTheme() {
	try {
		return localStorage.getItem(OMS_THEME_KEY) || document.documentElement.getAttribute("data-theme") || OMS_DEFAULT_THEME;
	} catch (error) {
		return document.documentElement.getAttribute("data-theme") || OMS_DEFAULT_THEME;
	}
}

function syncOmsThemeControls(activeTheme) {
	document.querySelectorAll("[data-theme-selector]").forEach((selector) => {
		selector.value = activeTheme;
	});

	document.querySelectorAll("[data-theme-choice]").forEach((button) => {
		const isActive = button.dataset.themeChoice === activeTheme;
		button.setAttribute("aria-pressed", isActive ? "true" : "false");
		button.classList.toggle("border-primary", isActive);
		button.classList.toggle("bg-primary/10", isActive);
	});
}

document.addEventListener("DOMContentLoaded", () => {
	const activeTheme = readOmsTheme();
	applyOmsTheme(activeTheme, false);

	document.querySelectorAll("[data-theme-choice]").forEach((button) => {
		button.addEventListener("click", () => {
			applyOmsTheme(button.dataset.themeChoice);
		});
	});

	document.querySelectorAll("[data-theme-selector]").forEach((selector) => {
		selector.addEventListener("change", (event) => {
			applyOmsTheme(event.target.value);
		});
	});
});

window.applyOmsTheme = applyOmsTheme;
