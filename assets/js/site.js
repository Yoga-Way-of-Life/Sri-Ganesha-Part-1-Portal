/* =============================================================================
   Śrī Gaṇeśa — Part 1 Portal
   Global Site Behaviour
   =============================================================================

   Responsibilities
   ----------------
   - Light / dark theme switching
   - Theme persistence
   - Mobile navigation
   - Reading progress indicator
   - Basic keyboard-friendly interaction handling

   Design principle
   ----------------
   Keep this file small and focused.

   Content, presentation and behaviour remain separate:

       Markdown → Content
       Jinja2  → Structure
       CSS     → Presentation
       JS      → Behaviour

   ============================================================================= */

"use strict";


/* =============================================================================
   1. DOM references
   ============================================================================= */

const html = document.documentElement;
const themeToggle = document.getElementById("theme-toggle");
const menuToggle = document.getElementById("menu-toggle");
const siteNavigation = document.getElementById("site-navigation");
const readingProgress = document.getElementById("reading-progress");


/* =============================================================================
   2. Theme management
   ============================================================================= */

const THEME_STORAGE_KEY = "sri-ganesha-theme";


function getPreferredTheme() {
    const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);

    if (storedTheme === "light" || storedTheme === "dark") {
        return storedTheme;
    }

    if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
        return "dark";
    }

    return "light";
}


function updateThemeButton(theme) {
    if (!themeToggle) {
        return;
    }

    const icon = themeToggle.querySelector(".theme-toggle__icon");

    if (theme === "dark") {
        themeToggle.setAttribute(
            "aria-label",
            "Switch to light theme"
        );

        themeToggle.setAttribute(
            "title",
            "Switch to light theme"
        );

        if (icon) {
            icon.textContent = "☀";
        }

        return;
    }

    themeToggle.setAttribute(
        "aria-label",
        "Switch to dark theme"
    );

    themeToggle.setAttribute(
        "title",
        "Switch to dark theme"
    );

    if (icon) {
        icon.textContent = "◐";
    }
}


function applyTheme(theme, persist = false) {
    html.setAttribute("data-theme", theme);
    updateThemeButton(theme);

    if (persist) {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
    }
}


function toggleTheme() {
    const currentTheme = html.getAttribute("data-theme") || "light";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";

    applyTheme(nextTheme, true);
}


function initialiseTheme() {
    const preferredTheme = getPreferredTheme();

    applyTheme(preferredTheme);
}


if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
}


/* =============================================================================
   3. Mobile navigation
   ============================================================================= */

function closeNavigation() {
    if (!siteNavigation || !menuToggle) {
        return;
    }

    siteNavigation.classList.remove("is-open");

    menuToggle.setAttribute(
        "aria-expanded",
        "false"
    );

    menuToggle.setAttribute(
        "aria-label",
        "Open navigation menu"
    );

    const icon = menuToggle.querySelector("span");

    if (icon) {
        icon.textContent = "☰";
    }
}


function openNavigation() {
    if (!siteNavigation || !menuToggle) {
        return;
    }

    siteNavigation.classList.add("is-open");

    menuToggle.setAttribute(
        "aria-expanded",
        "true"
    );

    menuToggle.setAttribute(
        "aria-label",
        "Close navigation menu"
    );

    const icon = menuToggle.querySelector("span");

    if (icon) {
        icon.textContent = "×";
    }
}


function toggleNavigation() {
    if (!siteNavigation || !menuToggle) {
        return;
    }

    const isOpen = siteNavigation.classList.contains("is-open");

    if (isOpen) {
        closeNavigation();
    } else {
        openNavigation();
    }
}


function initialiseNavigation() {
    if (!menuToggle || !siteNavigation) {
        return;
    }

    menuToggle.addEventListener(
        "click",
        toggleNavigation
    );

    const navigationLinks = siteNavigation.querySelectorAll("a");

    navigationLinks.forEach((link) => {
        link.addEventListener(
            "click",
            closeNavigation
        );
    });

    document.addEventListener(
        "keydown",
        (event) => {
            if (event.key === "Escape") {
                closeNavigation();
            }
        }
    );

    document.addEventListener(
        "click",
        (event) => {
            if (!siteNavigation.classList.contains("is-open")) {
                return;
            }

            if (
                !siteNavigation.contains(event.target) &&
                !menuToggle.contains(event.target)
            ) {
                closeNavigation();
            }
        }
    );

    window.addEventListener(
        "resize",
        () => {
            if (window.innerWidth > 767) {
                closeNavigation();
            }
        }
    );
}


/* =============================================================================
   4. Reading progress
   ============================================================================= */

function updateReadingProgress() {
    if (!readingProgress) {
        return;
    }

    const documentHeight =
        document.documentElement.scrollHeight - window.innerHeight;

    if (documentHeight <= 0) {
        readingProgress.style.width = "0%";
        return;
    }

    const scrollPosition = window.scrollY;
    const progress =
        (scrollPosition / documentHeight) * 100;

    const boundedProgress = Math.min(
        Math.max(progress, 0),
        100
    );

    readingProgress.style.width = `${boundedProgress}%`;
}


function initialiseReadingProgress() {
    if (!readingProgress) {
        return;
    }

    updateReadingProgress();

    window.addEventListener(
        "scroll",
        updateReadingProgress,
        { passive: true }
    );

    window.addEventListener(
        "resize",
        updateReadingProgress
    );
}


/* =============================================================================
   5. System theme changes
   ============================================================================= */

function initialiseSystemThemeListener() {
    const mediaQuery = window.matchMedia(
        "(prefers-color-scheme: dark)"
    );

    mediaQuery.addEventListener(
        "change",
        (event) => {
            const storedTheme =
                localStorage.getItem(THEME_STORAGE_KEY);

            if (storedTheme) {
                return;
            }

            applyTheme(
                event.matches ? "dark" : "light"
            );
        }
    );
}


/* =============================================================================
   6. Initialisation
   ============================================================================= */

function initialiseSite() {
    initialiseTheme();
    initialiseNavigation();
    initialiseReadingProgress();
    initialiseSystemThemeListener();
}


if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initialiseSite
    );
} else {
    initialiseSite();
}