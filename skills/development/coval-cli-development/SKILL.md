---
name: coval-cli-development
description: Development guide for the Coval CLI (Rust). Use when adding resources, fixing bugs, or making changes to the coval-cli repo.
argument-hint: "[task description]"
---

# Coval CLI Development

Task: `$ARGUMENTS`

## Repository

- **Repo**: `github.com/coval-ai/cli`
- **Language**: Rust 2021 edition
- **Binary**: `coval`
- **Current version**: Check `Cargo.toml`

## Code Style Rules (CRITICAL)

- NO comments except `///` on public items
- NO `unwrap()` or `expect()` outside tests — use `?` for error propagation
- NO unnecessary async
- All API fields that can be null MUST be `Option<T>` with `#[serde(default)]`
- Run `cargo fmt && cargo clippy -- -D warnings` before every commit
- Conventional Commits v1 style, no Claude attribution
- Keep code minimal — no bloat, no over-engineering

## Architecture

```
src/
├── main.rs                 # Entry point (13 lines)
├── cli.rs                  # Clap command definitions + routing
├── config.rs               # ~/.config/coval/config.toml
├── output.rs               # Table/JSON formatting (Tabular trait)
├── client/
│   ├── mod.rs              # CovalClient + all resource clients
│   ├── error.rs            # ApiError enum
│   └── models/             # Request/response types (1 file per resource)
│       ├── mod.rs           # Re-exports all models
│       ├── common.rs        # ListParams, ErrorResponse
│       ├── agent.rs
│       ├── run.rs
│       ├── simulation.rs
│       ├── test_set.rs
│       ├── test_case.rs
│       ├── persona.rs
│       ├── metric.rs
│       └── mutation.rs
└── commands/               # Command implementations (1 file per resource)
    ├── mod.rs
    ├── auth.rs
    ├── config.rs
    ├── agents.rs
    ├── runs.rs
    ├── simulations.rs
    ├── test_sets.rs
    ├── test_cases.rs
    ├── personas.rs
    ├── metrics.rs
    └── mutations.rs

tests/
└── cli_tests.rs            # Integration tests with wiremock
```

## Resources Implemented (9)

| Resource | Endpoints | Notes |
|----------|-----------|-------|
| agents | list, get, create, update, delete | |
| runs | list, get, launch, watch, delete | `watch` has live progress bar |
| simulations | list, get, delete, audio | `audio -o file.wav` downloads |
| test-sets | list, get, create, update, delete | |
| test-cases | list, get, create, update, delete | `--stdin` for bulk JSONL |
| personas | list, get, create, update, delete | |
| metrics | list, get, create, update, delete | |
| mutations | list, get, create, update, delete | Nested under agents |
| config | path, get, set | Local config management |

## How to Add a New Resource

When the OpenAPI spec adds a new resource (e.g., `widgets`), follow these 7 steps:

### 1. Create Model (`src/client/models/widget.rs`)

```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use crate::output::Tabular;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Widget {
    pub id: String,
    pub display_name: String,
    pub create_time: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub optional_field: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct CreateWidgetRequest {
    pub display_name: String,
}

#[derive(Debug, Default, Serialize)]
pub struct UpdateWidgetRequest {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub display_name: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct ListWidgetsResponse {
    pub widgets: Vec<Widget>,
    pub next_page_token: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct GetWidgetResponse {
    pub widget: Widget,
}

#[derive(Debug, Deserialize)]
pub struct CreateWidgetResponse {
    pub widget: Widget,
}

#[derive(Debug, Deserialize)]
pub struct UpdateWidgetResponse {
    pub widget: Widget,
}

impl Tabular for Widget {
    fn headers() -> Vec<&'static str> {
        vec!["ID", "NAME", "CREATED"]
    }
    fn row(&self) -> Vec<String> {
        vec![
            self.id.clone(),
            self.display_name.clone(),
            self.create_time.format("%Y-%m-%d %H:%M").to_string(),
        ]
    }
}
```

### 2. Register Model (`src/client/models/mod.rs`)

```rust
mod widget;
pub use widget::*;
```

### 3. Add Client (`src/client/mod.rs`)

Add struct:
```rust
pub struct WidgetsClient<'a>(&'a CovalClient);
```

Add accessor in `impl CovalClient`:
```rust
pub fn widgets(&self) -> WidgetsClient<'_> {
    WidgetsClient(self)
}
```

Add impl:
```rust
impl WidgetsClient<'_> {
    pub async fn list(&self, params: models::ListParams) -> Result<models::ListWidgetsResponse, ApiError> {
        let mut url = self.0.url("/v1/widgets");
        params.apply_to(&mut url);
        self.0.get(url).await
    }

    pub async fn get(&self, id: &str) -> Result<models::Widget, ApiError> {
        let url = self.0.url(&format!("/v1/widgets/{id}"));
        let resp: models::GetWidgetResponse = self.0.get(url).await?;
        Ok(resp.widget)
    }

    pub async fn create(&self, req: models::CreateWidgetRequest) -> Result<models::Widget, ApiError> {
        let url = self.0.url("/v1/widgets");
        let resp: models::CreateWidgetResponse = self.0.post(url, &req).await?;
        Ok(resp.widget)
    }

    pub async fn update(&self, id: &str, req: models::UpdateWidgetRequest) -> Result<models::Widget, ApiError> {
        let url = self.0.url(&format!("/v1/widgets/{id}"));
        let resp: models::UpdateWidgetResponse = self.0.patch(url, &req).await?;
        Ok(resp.widget)
    }

    pub async fn delete(&self, id: &str) -> Result<(), ApiError> {
        let url = self.0.url(&format!("/v1/widgets/{id}"));
        self.0.delete(url).await
    }
}
```

### 4. Create Command (`src/commands/widgets.rs`)

```rust
use anyhow::Result;
use clap::{Args, Subcommand};

use crate::client::models::{CreateWidgetRequest, ListParams, UpdateWidgetRequest};
use crate::client::CovalClient;
use crate::output::{print_list, print_one, print_success, OutputFormat};

#[derive(Subcommand)]
pub enum WidgetCommands {
    List(ListArgs),
    Get(GetArgs),
    Create(CreateArgs),
    Update(UpdateArgs),
    Delete(DeleteArgs),
}

#[derive(Args)]
pub struct ListArgs {
    #[arg(long)]
    filter: Option<String>,
    #[arg(long, default_value = "50")]
    page_size: u32,
    #[arg(long)]
    order_by: Option<String>,
}

#[derive(Args)]
pub struct GetArgs {
    widget_id: String,
}

#[derive(Args)]
pub struct CreateArgs {
    #[arg(long)]
    name: String,
}

#[derive(Args)]
pub struct UpdateArgs {
    widget_id: String,
    #[arg(long)]
    name: Option<String>,
}

#[derive(Args)]
pub struct DeleteArgs {
    widget_id: String,
}

pub async fn execute(cmd: WidgetCommands, client: &CovalClient, format: OutputFormat) -> Result<()> {
    match cmd {
        WidgetCommands::List(args) => {
            let params = ListParams {
                filter: args.filter,
                page_size: Some(args.page_size),
                order_by: args.order_by,
                ..Default::default()
            };
            let response = client.widgets().list(params).await?;
            print_list(&response.widgets, format);
        }
        WidgetCommands::Get(args) => {
            let widget = client.widgets().get(&args.widget_id).await?;
            print_one(&widget, format);
        }
        WidgetCommands::Create(args) => {
            let req = CreateWidgetRequest {
                display_name: args.name,
            };
            let widget = client.widgets().create(req).await?;
            print_one(&widget, format);
        }
        WidgetCommands::Update(args) => {
            let req = UpdateWidgetRequest {
                display_name: args.name,
            };
            let widget = client.widgets().update(&args.widget_id, req).await?;
            print_one(&widget, format);
        }
        WidgetCommands::Delete(args) => {
            client.widgets().delete(&args.widget_id).await?;
            print_success("Widget deleted.");
        }
    }
    Ok(())
}
```

### 5. Register Command (`src/commands/mod.rs`)

```rust
pub mod widgets;
```

### 6. Wire Up CLI (`src/cli.rs`)

Add to `Commands` enum:
```rust
Widgets {
    #[command(subcommand)]
    command: commands::widgets::WidgetCommands,
},
```

Add to `run()` match:
```rust
Commands::Widgets { command } => {
    commands::widgets::execute(command, &client, cli.format).await
}
```

### 7. Add Test (`tests/cli_tests.rs`)

```rust
#[tokio::test]
async fn test_widgets_list() {
    let mock_server = MockServer::start().await;

    Mock::given(method("GET"))
        .and(path("/v1/widgets"))
        .and(header("X-API-Key", "test_key"))
        .respond_with(ResponseTemplate::new(200).set_body_json(json!({
            "widgets": [{"id": "w123", "display_name": "Test", "create_time": "2025-01-15T10:30:00Z"}]
        })))
        .mount(&mock_server)
        .await;

    coval()
        .arg("--api-key").arg("test_key")
        .arg("--api-url").arg(mock_server.uri())
        .arg("widgets").arg("list")
        .assert()
        .success()
        .stdout(predicate::str::contains("w123"));
}
```

## Key Dependencies

| Crate | Purpose |
|-------|---------|
| clap | CLI argument parsing (derive mode) |
| reqwest | HTTP client (rustls-tls) |
| serde / serde_json | JSON serialization |
| tokio | Async runtime |
| anyhow / thiserror | Error handling |
| tabled | Table output |
| indicatif | Progress bars |
| chrono | DateTime handling |
| dirs | Home directory lookup |
| toml | Config file parsing |

## HTTP Client

- All requests include `User-Agent: coval-cli/{version}`
- All requests include `X-API-Key` header
- Base URL defaults to `https://api.coval.dev`
- 30 second timeout
- Error responses are parsed into typed `ApiError` variants

## Build & Release Process

```bash
# Dev
cargo build
cargo run -- agents list
cargo test

# Lint (must pass before commit)
cargo fmt
cargo clippy -- -D warnings

# Release
# 1. Bump version in Cargo.toml
# 2. Commit: "chore: bump version to X.Y.Z"
# 3. Merge to main
# 4. Tag: git tag vX.Y.Z && git push --tags
# 5. GitHub Actions builds binaries + creates release
# 6. Get SHA256s: gh release download vX.Y.Z --pattern "SHA256SUMS" --output -
# 7. Update coval-ai/homebrew-tap/Formula/coval.rb with new version + hashes
# 8. Push to homebrew-tap
# 9. Verify: brew upgrade coval && coval --version
```

## CI/CD

- `.github/workflows/ci.yml` — fmt, clippy, test on every push/PR
- `.github/workflows/release.yml` — builds binaries for macOS (x64+arm64), Linux (x64+arm64), Windows (x64) on tag push
- Homebrew tap: `coval-ai/homebrew-tap`

## OpenAPI Specs

All API definitions are in the backend repository:
```
/Users/lorenphillips/Development/backend-antigravity/docs/api/openapi/
```

Always check the OpenAPI spec before adding or modifying resources. If a field can be null in practice, it must be `Option<T>` regardless of what the spec says.

## Development Preferences

- Zero bloat — no unnecessary code, abstractions, or features
- No migration logic — tell users to re-login
- No comments in code — code should be self-documenting
- Silent operation — no unnecessary stderr output
- Config at `~/.config/coval/config.toml` (not platform-specific dirs)
- Conventional Commits v1 for all commit messages
- PRs required for main branch
- Test API key for manual testing: set `COVAL_API_KEY` env var
