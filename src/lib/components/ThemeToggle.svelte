<script lang="ts">
    import { themeStore } from "$lib/stores";
    import { browser } from "$app/environment";

    let currentTheme = $state("light");
    let isInitialized = $state(false);

    // Subscribe to theme changes
    $effect(() => {
        const unsubscribe = themeStore.subscribe((value) => {
            currentTheme = value;
            if (browser) {
                // Update the document's class to reflect the theme
                document.documentElement.classList.remove("light", "dark");
                document.documentElement.classList.add(value);
                // Also update the data-theme attribute for CSS
                document.documentElement.setAttribute("data-theme", value);
                // Update localStorage with the theme preference
                localStorage.setItem("theme", value);
            }
            isInitialized = true;
        });

        return () => {
            unsubscribe();
        };
    });

    function toggleTheme() {
        themeStore.toggle();
    }
</script>

<button
    class="theme-toggle"
    aria-label="Toggle dark mode"
    title="Toggle dark mode"
    onclick={toggleTheme}
    data-current-theme={currentTheme}
>
    {#if currentTheme === "light"}
        <!-- Sun icon for light theme -->
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="theme-icon sun-icon"
        >
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
    {:else}
        <!-- Moon icon for dark theme -->
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="theme-icon moon-icon"
        >
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
    {/if}
</button>

<style>
    .theme-toggle {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0.5rem;
        border-radius: 50%;
        border: 1px solid transparent;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 40px;
        height: 40px;
    }

    .theme-toggle:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }

    .theme-icon {
        width: 100%;
        height: 100%;
    }

    /* Light theme styles */
    :global(html[data-theme="light"]) .theme-toggle {
        background-color: #f0f0f0;
        color: #333;
        border: 1px solid #ddd;
    }

    :global(html[data-theme="light"]) .theme-toggle:hover {
        background-color: #e0e0e0;
    }

    /* Dark theme styles */
    :global(html[data-theme="dark"]) .theme-toggle {
        background-color: #444;
        color: #fff;
        border: 1px solid #666;
    }

    :global(html[data-theme="dark"]) .theme-toggle:hover {
        background-color: #555;
    }
</style>
