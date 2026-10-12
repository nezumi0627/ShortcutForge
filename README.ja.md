# ShortcutForge

**型付きJSONからAppleショートカットを作成するPython CLIと、Codex・Claude Code向けSkillです。** AIハーネスが自然言語を解釈し、ShortcutForgeは入力検証とBinary PLIST生成を決定的に行います。Python 3.11以上、Windows・macOS・Linuxに対応します。

[English README](README.md) · [ドキュメント一覧](docs/README.md) · [貢献ガイド](docs/contributing.md) · [MIT License](LICENSE)

> **互換性:** Binary PLISTを生成できても、Appleショートカットへの読み込みや実行が保証されるわけではありません。GitHubホストmacOSでの署名は、RunnerがiCloudにサインインしていないため現在利用できません。詳細は[既知の制限](#既知の制限)を確認してください。

## できること

- JSONプランから`.shortcut`ファイルを生成
- 既知アクション、パラメータ、plist互換値、出力参照を検証
- 既存のワークフローplistを実行せずに解析
- iOS 17・18・26・27を指定してアクションカタログを検索
- Codex・Claude Codeから使える、モデルAPIに依存しないSkillを提供

GUI、Webアプリ、常駐サーバー、LLM API、Python標準ライブラリ以外の実行依存関係はありません。

## クイックスタート

Python 3.11以上が必要です。

```sh
python -m pip install .
shortcutforge build examples/hello.json -o Hello.shortcut
shortcutforge validate Hello.shortcut
shortcutforge inspect Hello.shortcut
```

`shortcutforge`コマンドがPATHにない場合は、`python -m shortcutforge`を使えます。

## JSONを手で作成する

プランは通常のJSONです。テキストエディターで作成でき、AIハーネスから生成することもできます。

```json
{
  "version": 1,
  "name": "現在時刻を通知",
  "actions": [
    {"id": "current_date", "as": "now"},
    {"id": "notify", "params": {"text": {"ref": "now"}}}
  ]
}
```

```sh
shortcutforge build plan.json -o NotifyCurrentTime.shortcut
shortcutforge validate NotifyCurrentTime.shortcut
shortcutforge inspect NotifyCurrentTime.shortcut
```

アクションID、Appleパラメーターキー、rawアクションID、出力参照の仕様は[JSONプラン形式](docs/json-plan-format.md)を参照してください。Rawアクションの識別子とパラメーターは、互換性のあるショートカットまたは信頼できる情報源から取得してください。構造検証だけでは実行互換性を確認できません。

## iOSバージョン別カタログ

利用対象のiOSバージョンを必ず指定します。カタログは観測済み情報と不明な互換性を区別します。バージョン指定は動作保証ではありません。

```sh
shortcutforge actions list --os 27 --query notification
shortcutforge actions list --os 26 --lang ja --format markdown --output ios26-actions.ja.md
shortcutforge actions list --os 18 --format json
```

[日本語カタログガイド](docs/action-catalog.ja.md)、[英語カタログガイド](docs/action-catalog.en.md)、[収録範囲と出典](docs/action-catalog-sources.md)を参照してください。カタログの訂正・追加を歓迎します。[貢献ガイド](docs/contributing.md)に従ってPRをお送りください。

## AIハーネス用Skill

`skills/shortcutforge/SKILL.md`はCodexとClaude Codeに対応しています。Pythonパッケージをインストール後、`skills/shortcutforge`を各ハーネスのSkillディレクトリへコピーまたはリンクしてください。自然言語の解釈とJSON作成はAI側が行い、ShortcutForgeはモデルAPIを呼び出しません。具体的な配置先と安全な手順はSkillファイルを確認してください。

## コマンド

| コマンド | 用途 |
| --- | --- |
| `shortcutforge build PLAN -o FILE` | JSONを検証してBinary PLISTを生成 |
| `shortcutforge validate FILE` | plist構造を検証（Appleアクションの意味検証はしません） |
| `shortcutforge inspect FILE` | 実行せずにワークフロー名とアクションIDを表示 |
| `shortcutforge actions list --os VERSION` | バージョン別のアクション候補を検索 |
| `shortcutforge sign FILE` | GitHub Actions署名ワークフローを実行。現状は[署名制限](docs/signing-validation.md)あり |

各コマンドのオプションは`shortcutforge COMMAND --help`で確認できます。

## 既知の制限

- ビルド時の便利なスキーマは`current_date`、`text`、`notify`、`speak`、`open_url`のみです。Raw Appleアクションには基本的な構造検証だけを行います。
- 変数・出力参照は現在の直線的なアクション形式で利用できます。条件分岐・繰り返しのコンパイルとカレンダーアクションは未実装です。
- 2,501件の識別子カタログはAppleの完全なスキーマではありません。iOS 27はSimulatorでの観測情報があり、iOS 17・18・26は互換性が不明、または部分的な変更報告に基づきます。
- 実機iPhoneへの読み込み・実行テストは未実施です。iOS 27への読み込みも未検証です。
- GitHubホストmacOSでの署名は、AppleからiCloudサインインを要求されて失敗しました。現状この経路では署名済み成果物を生成できません。[署名検証記録](docs/signing-validation.md)を参照してください。

## 開発

```sh
python -m unittest discover -s tests -v
```

変更前に[アーキテクチャ](docs/architecture.md)、[セキュリティ](docs/security.md)、[貢献ガイド](docs/contributing.md)、[AGENTS.md](AGENTS.md)を確認してください。このPublicリポジトリはGitHubテンプレートとしても利用できます。複製前に[テンプレート利用上の注意](docs/template-and-release.md)を確認してください。
