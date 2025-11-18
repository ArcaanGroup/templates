<script lang="ts">
    import { localeStore } from "$lib/stores";
    import { browser } from "$app/environment";
    import { locale } from "svelte-i18n";

    let currentLocale = $state("en");

    // Subscribe to locale changes
    $effect(() => {
        const unsubscribe = localeStore.subscribe((value) => {
            currentLocale = value;
            if (browser) {
                // Update the document's lang attribute
                document.documentElement.lang = value;
                document.documentElement.dir = value === "fa" ? "rtl" : "ltr";
            }
        });

        return () => {
            unsubscribe();
        };
    });

    function changeLocale(newLocale: string) {
        localeStore.set(newLocale);
        localStorage.setItem("locale", newLocale);

        // Update svelte-i18n locale to trigger reactivity
        locale.set(newLocale);
    }

    // Toggle between English and Persian
    function toggleLocale() {
        const newLocale = currentLocale === "en" ? "fa" : "en";
        changeLocale(newLocale);
    }
</script>

<button class="lang-btn" aria-label="Switch language" onclick={toggleLocale}>
    {currentLocale === "en" ? "FA" : "EN"}
</button>

<style>
    .lang-btn {
        height: 40px;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .lang-btn:hover {
        background-color: rgba(255, 255, 255, 0.2);
    }

    /* Light theme styles */
    :global(html[data-theme="light"]) .lang-btn {
        background-color: #f0f0f0;
        color: #333;
        border: 1px solid #ddd;
    }

    :global(html[data-theme="light"]) .lang-btn:hover {
        background-color: #e0e0e0;
    }

    /* Dark theme styles */
    :global(html[data-theme="dark"]) .lang-btn {
        background-color: #444;
        color: #fff;
        border: 1px solid #666;
    }

    :global(html[data-theme="dark"]) .lang-btn:hover {
        background-color: #555;
    }
</style>
