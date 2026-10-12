# OmniProxy Privacy Policy

Effective date and last updated: October 12, 2026

OmniProxy is a Personal AI Gateway for managing local models, connecting external AI services, routing requests, and monitoring calls. This policy covers the OmniProxy desktop application and command-line software, our optional recipe-contribution service, and privacy communications with us. The operator is **A New Zero Innovations Limited (Hong Kong)** ("we", "us", or "our").

## 1. At a glance

- Settings, credentials, local model assets, and call records are maintained on your device. Installing OmniProxy does not give us access to them.
- Local inference processes content on the machine running OmniProxy. External models, search services, and webpage-reading services receive the information needed for the requests you route to them.
- Recipe contributions are optional. Testing, editing, saving, or previewing a recipe does not upload it to our contribution service. A submission is sent only when you choose the sharing action; routine use does not submit it.
- A recipe contribution contains a restricted description of protocol mappings and test-result metadata, not your complete prompts, responses, API credentials, or media attachments.
- We do not sell or rent your personal information, use it for advertising, or use contribution data to train AI models. Contributions are used to review and improve model compatibility rules.

**Recipe-sharing availability:** As of this policy's effective date, the documented OmniProxy contribution configuration has no enabled Firebase deployment. The sharing flow described below is conditional on availability in your version. Uploads are unavailable when the service recipient, region, or retention disclosure is missing. Before enabling this service, we will update this policy with the actual recipient, processing locations, and infrastructure-log retention. Publishing this policy alone does not enable uploads.

## 2. Information handled on your device

OmniProxy handles the information necessary for the features you use, including:

- Application preferences, model and provider configurations, routing and protocol mappings, and connection settings.
- API keys and other authentication credentials you provide. OmniProxy uses the operating system's credential store for protected credentials; on macOS this is Keychain. Credentials are supplied to the configured service when needed to authenticate a request.
- Local model files and locations you authorize OmniProxy to access, together with local model-management and test information.
- Request content and results supplied by you or by applications using your OmniProxy gateway. Depending on the feature and model, this may include text, prompts, conversation context, images, audio, other supported attachments, translations, search queries, and requested webpage addresses.
- Local glossaries, redaction settings, call records, error information, cached results, and usage statistics.

Call records can contain sensitive request or response content. They are separate from the longer-lived usage totals used for statistics. Body-retention settings and storage limits govern local call content; clearing call logs does not necessarily clear aggregate statistics. Settings, credentials, model assets, and other local records have their own lifecycles and are not all removed when call bodies expire.

OmniProxy does not operate a general cloud backup of these local records. Files you export, copy, or store in a synchronized or shared directory are subject to the access and retention practices of that destination. Uninstalling the application is not a guarantee that local files, Keychain entries, exported copies, or remote submissions have been deleted.

## 3. Local processing and external services

### Local models

When a request uses a local model, inference takes place on the machine running OmniProxy rather than an AI service operated by us. Downloading models or checking public model and recipe catalogs can still involve network access. A model host or catalog host can receive the requested resource address and ordinary network information, such as an IP address and access time.

If you access OmniProxy running on another computer, that computer is the processing location. A local model on that computer does not mean that your content remains on your own device.

### Services you configure

When you route a request to an external model, search service, webpage-reading service, or API gateway, OmniProxy sends the required content to the configured destination. For example, an external translation request sends the text and any relevant instructions or glossary context; a search request sends its query; a webpage-reading request sends the requested URL. Supported media requests may send their attachments.

The service can also receive authentication and network metadata. If the destination is itself a gateway or proxy, its downstream providers may receive the request as well. Provider retention, training, account records, and deletion practices are governed by that service's policy and your agreement with it. Choosing a provider through OmniProxy does not make us its operator or give us control over its independent processing.

Real connection checks and model tests can contact external services and incur their normal charges. They do not become recipe contributions merely because a test succeeds. Review the destination and test inputs before running them.

### Redaction

Text redaction is configured separately for each external source and is off by default for new sources. When enabled, it attempts to replace detected sensitive text before sending the request. It can miss information or replace the wrong text. Raw images, audio, and other unparsed binary content are not covered by text redaction. Some request paths allow an explicit bypass where you have enabled that permission.

Redaction is not a guarantee of anonymity or permission to disclose someone else's information. Check the actual outgoing content, use non-sensitive test samples, and choose services you trust. Protecting authentication secrets in ordinary logs is separate from redacting business content.

## 4. Optional recipe contributions to Firebase

A "recipe" describes how OmniProxy adapts request and response fields for a model or protocol. Sharing a recipe helps maintainers investigate compatibility problems; it is not a request to upload your conversation history.

### Firebase functions and when they run

Firebase is used for the recipe-contribution service only. It is not the destination for your ordinary model calls, local call logs, statistics, model assets, settings, or backups. OmniProxy does not use Firebase Analytics, Crashlytics, Remote Config, Firebase Authentication, or a Firebase user-account system.

| Function | Trigger and information handled |
| --- | --- |
| Prepare a preview or display submission records | Runs locally through OmniProxy's own runtime. It reads the local contribution projection, local receipts, and the service configuration. It does not query Firebase or send a contribution. |
| Submit a contribution | Runs after you choose to share. It sends the restricted recipe document, a random submission identifier, and its deletion credential over HTTPS to the contribution service. |
| Delete a submission | Runs when you request deletion. It sends the submission identifier and deletion credential to the service so it can authenticate and remove the record. It does not upload a new recipe or grant permission for future sharing. |
| Prevent abuse | Runs on requests received by the service, including submission and deletion requests. It uses short-lived IP-derived rate-limit buckets and counts, as described below. |
| Expire records or reject a candidate | Runs on the server: scheduled cleanup removes expired records, and authorized maintainers can reject and remove candidates. These actions do not collect a new recipe from your device or require a new sharing decision. |

Downloading official recipes uses the separate signed distribution mechanism; it is not an upload to Firebase. Testing, editing, saving, restarting OmniProxy, or opening this policy does not submit a contribution.

### Your sharing decision

When sharing is available, the application shows a preview of the eligible contribution and a brief explanation of its purpose. Selecting **Agree and share** is both your authorization and the instruction to submit that contribution. The software does not require a second permission dialog after that action. The corresponding CLI submission requires its explicit confirmation option.

General acceptance of this policy is not permission for automatic collection. Declining or closing the preview does not submit it and does not prevent local editing, testing, or saving. Each later contribution or manual retry is a new action you initiate; the current software does not automatically upload subsequent changes or automatically retry a failed submission. Deletion and server cleanup are separate operations, not new contribution uploads.

### What is submitted

The contribution service accepts a limited, validated record containing:

- An approved public provider profile, public model identifier, protocol family, and tested capability, such as chat, vision, or search.
- Restricted field-mapping operations for the previous and corrected recipe, including permitted field paths, named transforms, and bounded public parameter values.
- Hashes identifying the previous and corrected recipe versions, a fixed failure category, the OmniProxy version, and the successful test timestamp.
- A random identifier for that submission and a separate random deletion credential. These belong to one submission, not a persistent user account or device profile.

The contribution format has no fields for provider endpoints, secret headers, provider API keys, passwords, local file paths, private provider names, full prompts, complete request or response bodies, raw error messages, or media attachments. Recipes with unapproved identities or unrestricted values can remain usable locally while being ineligible to share. Review the preview before confirming; do not submit confidential material or information you lack permission to disclose.

The deletion credential is transmitted over HTTPS to authenticate ownership of the submission. The backend stores its hash rather than the credential itself. Your copy is held in your device's credential store for later deletion requests; it is not your AI provider's API key.

### Recipient, access, and purpose

When enabled, the contribution backend uses **Google Firebase / Google Cloud**, specifically Cloud Functions and Firestore, to process and store submissions for us. Authorized maintainers review candidates to improve compatibility rules. The service does not offer a public listing or public download of submitted records.

Firebase is infrastructure we choose to operate this service. It is different from an AI provider you choose independently. We remain responsible for our use of that infrastructure and for privacy requests concerning information under our control. See [Firebase privacy and security information](https://firebase.google.com/support/privacy), the [Google Cloud Privacy Notice](https://cloud.google.com/terms/cloud-privacy-notice), and [Google's Privacy Policy](https://policies.google.com/privacy) for the provider's applicable processing practices.

### Network information and abuse prevention

Google's infrastructure receives network information such as the connecting IP address, request time, URL, and response status. The contribution handler uses an IP-derived keyed hash that changes each minute to limit abuse; it does not use that value as a persistent user or device identifier. Rate-limit records expire after 15 minutes and are removed by scheduled cleanup.

The contribution handler does not write submission bodies, deletion credentials, raw IP addresses, or complete internal errors to its application logs. Infrastructure request logs are separate and may contain network metadata. For this reason, we do not describe submissions as completely anonymous. This feature does not use Firebase Analytics, Crashlytics, advertising identifiers, or a user-tracking SDK.

### Retention and deletion

Each submission receipt is set to expire 90 days after acceptance. Scheduled cleanup runs hourly to remove expired receipts and candidates; the expiry time is not a guarantee that physical deletion completes at that exact instant. A candidate submitted independently by several people may remain while other valid submissions reference it, with its retention renewed by a new submission.

When sharing is available, the sharing preview provides **Shared recipes**, where you can request deletion; the corresponding CLI contribution-deletion operation is also available. There is no separate contribution-management section in Settings. If the preview is unavailable, contact **hello@anz.tv** privately to request deletion or withdraw your sharing consent. Provide the submission identifier if you have it, but do not send your deletion credential or provider API key by email. A successful response confirms removal of your backend receipt. The associated candidate is removed when no other live submission references it. A pending or failed deletion is not confirmation that the server record is gone. An upload with an unknown outcome may still have reached the server; keep its receipt and deletion credential so you can request deletion.

Deleting a local recipe, uninstalling OmniProxy, or losing the deletion credential does not itself delete a remote contribution. If you cannot use the deletion operation, contact us privately. We may need sufficient information to locate the record and verify the request. Never post the deletion credential in a public issue. Infrastructure logs have a separate retention lifecycle; deleting a contribution does not necessarily erase those logs.

### Reviewed rules and published copies

Submissions are unverified candidates, even when a local test passed. Maintainers may independently test the underlying compatibility changes using synthetic inputs and incorporate reviewed, general-purpose rules into official signed recipe distributions. Sharing does not guarantee acceptance or publication.

Withdrawal removes the submission as described above. It cannot recall rules already distributed to other users, their downloaded copies, or equivalent rules supplied independently by others. We do not publish submission identifiers, deletion credentials, or private network logs as part of those rules.

## 5. Diagnostics, documentation, and support

OmniProxy does not include developer-operated advertising tracking or general usage-analytics or crash-reporting uploads. Local call monitoring and statistics are product features, not automatic reports to us. Apple may separately process purchase, store, and diagnostic information under its own policies and your platform settings.

When you open documentation hosted on GitHub or GitHub Pages, GitHub processes website access under the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement).

If you email us or submit feedback, we receive the information you choose to include and use it to answer or investigate your request. Support messages and attachments may contain personal information. Send only what is necessary and redact credentials, private content, and identifying details. GitHub issues are public; use email for private privacy requests. We retain support information for handling the request and any necessary follow-up, security, or legal obligations, rather than using it for advertising.

## 6. Security and responsibility boundaries

We limit the data accepted by the contribution service, require HTTPS for that service, protect deletion credentials, and restrict access to stored candidates. No storage or transmission method is completely secure, and we cannot guarantee that all outages, unauthorized access, or data loss will be prevented.

You are responsible for choosing appropriate external destinations, protecting your device and credentials, reviewing what you share, and having the necessary rights to submit it. Automated filters and local test success do not establish that content is safe or lawful to disclose.

Third-party services may change their availability, pricing, processing practices, or terms. To the extent permitted by applicable law, we do not guarantee their independent conduct or assume liability for losses attributable solely to those services or to unauthorized disclosures you make. **This does not exclude our responsibility for our own processing, security obligations, conduct, or any liability or privacy rights that cannot lawfully be excluded.** In particular, using Firebase does not transfer all responsibility for our contribution service to Google.

## 7. Your choices and privacy rights

You can choose local processing, decide which external services to configure, stop sending requests to a service, change or remove credentials, manage local log retention, clear available local records, and decline recipe sharing. Declining sharing does not prevent ordinary local recipe editing, testing, or saving.

Where applicable, optional contributions are processed on the basis of your consent, and you can withdraw that consent through deletion or by contacting us. Withdrawal does not undo processing that was lawful before withdrawal or recall already distributed general rules. Necessary support and service-security processing may rely on responding to your request, legitimate interests, or legal obligations, as applicable.

Depending on your location, you may have rights to access, correct, delete, or receive a copy of personal information we control, restrict or object to processing, withdraw consent, or complain to a supervisory authority. Contact us to exercise applicable rights. We do not have remote access to your local OmniProxy records; you manage those on the device. Requests about an independently selected provider should also be directed to that provider.

Google, GitHub, external providers, and support systems may process information outside your country, including in places with different data-protection laws. The actual Firebase service and database locations and infrastructure-log retention must be disclosed before recipe uploads are enabled; this policy does not claim that all information stays in Hong Kong or on your device.

We may disclose information we control where legally required or necessary to investigate abuse or protect lawful rights. We do not use this provision to collect your local content automatically.

## 8. Children and policy changes

OmniProxy is not directed to children. If applicable law requires a parent or guardian's permission for the processing described here, obtain that permission before using the relevant service. Contact us if you believe a child has provided personal information to us improperly.

We may update this policy as the product, service availability, or applicable requirements change. We will update the date above and provide appropriate notice of material changes. A policy update does not replace any separate consent required to upload a recipe or authorize new processing.

## 9. Contact

For privacy questions or requests, contact [hello@anz.tv](mailto:hello@anz.tv).

**Operator / Controller:** A New Zero Innovations Limited (Hong Kong).

For public product feedback only, use [OmniProxy Docs Issues](https://github.com/granoflow/omniproxy-docs/issues). Do not post personal information, API keys, or deletion credentials there.
