<?php
/**
 * Plugin Name: iPhoneFeed Robots.txt
 * Description: Custom robots.txt for iphonefeed.news SEO optimization
 * Version: 1.0
 * Author: iPhoneFeed
 */

// Write physical robots.txt to site root
function iphonefeed_write_robots_txt() {
    $root = ABSPATH;
    $robots_content = <<<ROBOTS
# robots.txt for iphonefeed.news
# Apple news aggregator (RU audience)
# Updated: 2026-04-14

# ─── Global rules (all bots) ───────────────────────────────────────────────

User-agent: *

# WordPress system areas
Disallow: /wp-admin/
Allow:    /wp-admin/admin-ajax.php

Disallow: /wp-login.php
Disallow: /xmlrpc.php

# Low-value / duplicate content
Disallow: /?s=
Disallow: /search/
Disallow: /feed/
Disallow: /*/feed/
Disallow: /trackback/
Disallow: /*/trackback/
Disallow: /comments/
Disallow: /*/comments/

# WordPress internals
Disallow: /wp-includes/
Disallow: /wp-content/plugins/
Disallow: /wp-content/cache/
Disallow: /wp-json/
Disallow: /cgi-bin/

# Query-string junk
Disallow: /*?*replytocom=
Disallow: /*?*preview=true
Disallow: /*?*print=

# Allow static assets explicitly
Allow: /wp-content/uploads/
Allow: /wp-content/themes/

# ─── Googlebot ──────────────────────────────────────────────────────────────

User-agent: Googlebot

Disallow: /wp-admin/
Allow:    /wp-admin/admin-ajax.php
Disallow: /wp-login.php
Disallow: /xmlrpc.php
Disallow: /?s=
Disallow: /search/
Disallow: /feed/
Disallow: /*/feed/
Disallow: /trackback/
Disallow: /*/trackback/
Disallow: /comments/
Disallow: /*/comments/
Disallow: /wp-includes/
Disallow: /wp-content/plugins/
Disallow: /wp-content/cache/
Disallow: /wp-json/
Disallow: /*?*replytocom=
Disallow: /*?*preview=true

Allow: /wp-content/uploads/
Allow: /wp-content/themes/

# ─── Googlebot-Image ────────────────────────────────────────────────────────

User-agent: Googlebot-Image

Allow: /wp-content/uploads/
Disallow: /

# ─── Yandex ─────────────────────────────────────────────────────────────────

User-agent: Yandex

Disallow: /wp-admin/
Allow:    /wp-admin/admin-ajax.php
Disallow: /wp-login.php
Disallow: /xmlrpc.php
Disallow: /?s=
Disallow: /search/
Disallow: /feed/
Disallow: /*/feed/
Disallow: /trackback/
Disallow: /*/trackback/
Disallow: /comments/
Disallow: /*/comments/
Disallow: /wp-includes/
Disallow: /wp-content/plugins/
Disallow: /wp-content/cache/
Disallow: /wp-json/
Disallow: /*?*replytocom=
Disallow: /*?*preview=true

Allow: /wp-content/uploads/
Allow: /wp-content/themes/

# ─── Aggressive / bad bots ───────────────────────────────────────────────────

User-agent: AhrefsBot
Disallow: /

User-agent: MJ12bot
Disallow: /

User-agent: DotBot
Disallow: /

User-agent: SemrushBot
Disallow: /

# ─── Sitemap ─────────────────────────────────────────────────────────────────

Sitemap: https://iphonefeed.news/sitemap_index.xml
ROBOTS;

    $file_path = $root . 'robots.txt';
    file_put_contents($file_path, $robots_content);
}

register_activation_hook(__FILE__, 'iphonefeed_write_robots_txt');

// Also run on init in case the file was deleted
add_action('init', function() {
    $root = ABSPATH;
    $file_path = $root . 'robots.txt';
    if (!file_exists($file_path)) {
        iphonefeed_write_robots_txt();
    }
});
