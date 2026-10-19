# Privacy and browser storage

This documentation uses no analytics, remote fonts, video embeds, or external
comment services. Fonts use the browser's local font stack. Search, styles, scripts,
favicon and Mermaid 11.12.0 diagrams are served with the documentation itself.
The pinned Mermaid distribution includes its MIT license in the site assets.

## Consent controls

The native Zensical consent panel provides **Accept**, **Reject**, and **Manage
settings**. The optional GitHub repository-statistics category starts unchecked.
Accept saves the selected categories; it does not automatically enable an unchecked
category. Reject disables optional categories. The footer's **Change cookie
settings** link reopens the panel and restores the saved choice. Rejecting after
accepting prevents subsequent optional GitHub requests on reload.

When enabled, repository statistics may contact `api.github.com`. A repository link
is also available independently; clicking an external link navigates to that site
and is an explicit user action. Hosting requests to GitHub Pages are necessary to
serve this documentation. The hosting provider's own logging is outside this site's
consent integration.

Consent choices use scoped browser localStorage (`__consent`). The theme may store
search, palette or repository-cache state locally. Local storage is inspected by
the browser verification script as well as cookies; this is not a cookie-only audit.

See [documentation development](Documentation-Development.md) for repeatable browser
checks and evidence. A consent panel and these checks are not proof of GDPR compliance.
Any future analytics, embeds or other optional services require a new privacy review
and consent-aware integration.
