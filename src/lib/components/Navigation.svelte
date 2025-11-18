<script lang="ts">
    import { t } from "svelte-i18n";
    import ThemeToggle from "./ThemeToggle.svelte";
    import LanguageToggle from "./LanguageToggle.svelte";
</script>

<nav class="main-nav">
    <div class="nav-content">
        <div class="logo-section">
            <h1>Sepehr</h1>
            <span class="subtitle">Ground Control Platform</span>
        </div>

        <div class="nav-items">
            <a href="/dashboard" class="nav-link">{$t("menu.dashboard")}</a>
            <a href="/mission-planning" class="nav-link"
                >{$t("menu.mission_planning")}</a
            >
            <a href="/map-caching" class="nav-link">{$t("menu.map_caching")}</a>
            <a href="/data-management" class="nav-link"
                >{$t("menu.data_management")}</a
            >
            <a href="/control-parameters" class="nav-link"
                >{$t("menu.control_parameters")}</a
            >
            <a href="/company-profile" class="nav-link"
                >{$t("menu.company_profile")}</a
            >
        </div>

        <div class="controls">
            <ThemeToggle />
            <LanguageToggle />
        </div>
    </div>
</nav>

<style>
    .main-nav {
        background-color: var(--color-nav-bg);
        color: var(--color-nav-text);
        padding: 0.5rem 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .nav-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
    }

    .logo-section h1 {
        margin: 0;
        font-size: 1.5rem;
        color: var(--color-nav-text);
    }

    .subtitle {
        color: var(--color-nav-text);
        font-size: 0.8rem;
        opacity: 0.8;
    }

    .nav-items {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
    }

    .nav-link {
        color: var(--color-nav-text);
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        transition: background-color 0.3s;
    }

    .nav-link:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }

    .controls {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    @media (max-width: 768px) {
        .nav-content {
            flex-direction: column;
            gap: 1rem;
        }

        .nav-items {
            width: 100%;
            justify-content: center;
        }
    }
</style>
