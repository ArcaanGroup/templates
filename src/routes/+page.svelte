<script lang="ts">
    import { invoke } from "@tauri-apps/api/core";
    import { onMount } from "svelte";
    import { t } from "svelte-i18n";
    import { localeStore } from "$lib/stores";
    // Import typography styles
    import "$lib/styles/typography.css";
    import ThemeToggle from "$lib/components/ThemeToggle.svelte";
    import LanguageToggle from "$lib/components/LanguageToggle.svelte";

    let name = $state("");
    let greetMsg = $state("");
    let currentLocale = $state("fa");
    let isPageLoaded = $state(false); // Track if page has loaded

    // Initialize on component mount
    onMount(() => {
        // Get the current locale
        const unsubscribe = localeStore.subscribe((value) => {
            currentLocale = value;
        });

        isPageLoaded = true;

        // Clean up subscription
        return () => {
            unsubscribe();
        };
    });

    async function greet(event: Event) {
        event.preventDefault();
        // Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
        greetMsg = await invoke("greet", { name, locale: currentLocale });
    }
</script>

<main class="container">
    <div class="controls">
        <ThemeToggle />
        <LanguageToggle />
    </div>

    {#if isPageLoaded}
        <h1>{$t("welcome")}</h1>

        <div class="row">
            <a href="https://vitejs.dev" target="_blank">
                <img src="/vite.svg" class="logo vite" alt="Vite Logo" />
            </a>
            <a href="https://tauri.app" target="_blank">
                <img src="/tauri.svg" class="logo tauri" alt="Tauri Logo" />
            </a>
            <a href="https://kit.svelte.dev" target="_blank">
                <img
                    src="/svelte.svg"
                    class="logo svelte-kit"
                    alt="SvelteKit Logo"
                />
            </a>
        </div>
        <p>{$t("greeting")}</p>

        <form class="greeting-form row" onsubmit={greet}>
            <input
                id="greet-input"
                placeholder={$t("name_placeholder")}
                bind:value={name}
            />
            <button type="submit">{$t("greet_button")}</button>
        </form>
        <p>{greetMsg}</p>
    {:else}
        <!-- Show a loading state while locale is being loaded -->
        <div class="loading">
            <p>Loading...</p>
        </div>
    {/if}
</main>

<style>
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 50vh;
    }

    .controls {
        position: absolute;
        top: 20px;
        right: 20px;
        display: flex;
        gap: 0.5rem;
    }

    .logo.vite:hover {
        filter: drop-shadow(0 0 2em #747bff);
    }

    .logo.svelte-kit:hover {
        filter: drop-shadow(0 0 2em #ff3e00);
    }

    .container {
        margin: 0;
        padding-top: 10vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }

    .logo {
        height: 6em;
        padding: 1.5em;
        will-change: filter;
        transition: 0.75s;
    }

    .logo.tauri:hover {
        filter: drop-shadow(0 0 2em #24c8db);
    }

    .row {
        display: flex;
        justify-content: center;
    }

    .greeting-form {
        gap: 1rem;
    }

    h1 {
        text-align: center;
    }

    input,
    button {
        border-radius: 8px;
        border: 1px solid var(--color-border);
        padding: 0.6em 1.2em;
        font-size: 1em;
        font-weight: 500;
        font-family: inherit;
        color: var(--color-input-text);
        background-color: var(--color-input-bg);
        transition: border-color 0.25s;
        box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
    }

    button {
        cursor: pointer;
    }

    button:hover {
        border-color: var(--color-accent);
    }

    button:active {
        border-color: var(--color-accent);
        background-color: var(--color-button-hover);
    }

    input,
    button {
        outline: none;
    }
</style>
