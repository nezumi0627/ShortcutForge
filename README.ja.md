# ShortcutForge

**型付きJSONまたは[Cherri](https://github.com/electrikmilk/cherri)ソースからAppleショートカットを作成します。** ShortcutForgeはPython製CLIと、Codex・Claude Codeで使えるSkillです。AIハーネスが自然言語を解釈して設計する使い方と、人がJSONやCherriを直接書く使い方の両方に対応します。ビルド時にLLM APIは使いません。

[English](README.md) · [ドキュメント一覧](docs/README.md) · [貢献ガイド](docs/contributing.md) · [MIT License](LICENSE)

> **署名と読み込み:** `build`が生成する`.shortcut`は未署名です。iPhone/iPadのショートカットAppへファイルとして読み込む前に署名してください。Windowsで使える署名方式はShortcutyのみで、ショートカット全体をShortcutyのサービスへ送信します。対応する非Windows環境ではHubSignまたはApple純正macOS署名を選べます。GitHub Actionsでは署名しません。外部署名サービスに送る前に[署名とプライバシー](docs/signing-validation.md)を確認してください。

## できること

- バージョン付きJSONプランを内蔵Pythonコンパイラで生成
- `.cherri`を別途インストールしたCherriコンパイラへ渡して生成（Cherri側の署名は無効）
- ワークフローplistの基本構造を検証し、既存ファイルを実行せずに解析
- iOS 17・18・26・27別のアクション調査カタログを検索し、英語・日本語Markdownを出力
- AIハーネスから使えるSkillを提供。自然言語理解はハーネス側で行い、ShortcutForgeはモデルAPIを呼び出さない

JSONコンパイラには、個別に整備したスキーマに加え、公開定義から取り込んだ標準パラメーター形式のスキーマがあります。大規模なアクションカタログは調査用インデックスです。バージョン上で識別子が観測されていても、すべての端末で読み込み・実行できる保証にはなりません。

## インストール

Python 3.11以上が必要です。

```sh
python -m pip install .
```

`shortcutforge`コマンドがPATHにない場合は`python -m shortcutforge`を使ってください。

Cherriビルドは任意機能です。利用する場合はCherri本体を別途インストールし、実行ファイルをPATHに追加します。手順とWindowsの制約は[Cherri連携ガイド](docs/cherri-integration.md)を参照してください。

## JSONから作成する

`plan.json`を作成します。

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

ビルド・確認後、インポート前に署名します。

```sh
shortcutforge build plan.json -o NotifyCurrentTime.shortcut
shortcutforge validate NotifyCurrentTime.shortcut
shortcutforge inspect NotifyCurrentTime.shortcut
shortcutforge sign NotifyCurrentTime.shortcut
```

テキスト入力・通知・読み上げ、URLとWebリクエスト、クリップボード、位置情報と端末情報、カレンダーとリマインダー、写真保存、バッテリー残量、待機に加え、公開定義に基づく200件超のアクションを利用できます。[一覧・出典・制約](docs/named-actions.md)を参照してください。バージョン別の観測と定義元の情報は、端末での読み込み・実行を保証しません。正確なAppleアクション識別子とパラメーター辞書を指定するraw形式も使えますが、ShortcutForgeが行うのは基本的な構造検査だけです。[JSONプラン形式](docs/json-plan-format.md)も参照してください。

## Cherriソースから作成する

Cherriは制御フローや関数を含むコード中心のワークフローに向いた別言語・コンパイラです。Cherriをインストールしてから実行します。

```sh
shortcutforge build examples/cherri-control-flow.cherri -o CherriExample.shortcut
shortcutforge validate CherriExample.shortcut
shortcutforge inspect CherriExample.shortcut
```

ShortcutForgeはCherriを`--skip-sign`付きで呼び出し、未署名plistを検証して指定先へ保存します。署名は別の明示的な操作です。付属例ではIfとRepeatを使っています。Windowsで上流ソースからビルドしたCherriによるスモークテストは成功しましたが、上流の案内ではWindowsの安定対応に制約があります。詳細は[Cherri連携ガイド](docs/cherri-integration.md)を参照してください。

## 対象iOSのアクションを調べる

アクション選択前に、対象端末にインストールされたiOSバージョンを指定してください。カタログは識別子や根拠の検索を助けますが、網羅的ではなく、読み込みや実行を保証しません。

```sh
shortcutforge actions list --os 27 --query notification
shortcutforge actions list --os 26 --lang ja --format markdown --output ios26-actions.ja.md
shortcutforge actions list --os 18 --format json
```

[日本語カタログガイド](docs/action-catalog.ja.md)、[英語カタログガイド](docs/action-catalog.en.md)、[出典と収録範囲](docs/action-catalog-sources.md)を参照してください。訂正・追加のPRを歓迎します。対象OSを特定できる根拠を添えて[貢献ガイド](docs/contributing.md)に従ってください。

Python APIからも同じカタログを使えます。

```python
from shortcutforge import ActionCatalog, IOSVersion

catalog = ActionCatalog.from_package()
actions = catalog.list_actions(IOSVersion.IOS_26, query="calendar")
availability = catalog.get_availability(
    "is.workflow.actions.notification", IOSVersion.IOS_26
)
markdown = catalog.render_markdown(IOSVersion.IOS_26, language="ja")
```

## AIハーネス用Skill

[ShortcutForge Skill](skills/shortcutforge/SKILL.md)はCodexとClaude Codeに対応しています。`python -m pip install .`の後、`skills/shortcutforge`を各ハーネスのSkillディレクトリへコピーまたはリンクしてください。Skillはハーネス自身の推論を使うため、独立したモデルAPIキーは不要です。対象iOSの確認、ビルド、解析を案内し、署名をデータ送信を伴う別工程として扱います。

## コマンド

| コマンド | 用途 |
| --- | --- |
| `shortcutforge build PLAN.json -o FILE` | JSONを検証してBinary PLISTを生成 |
| `shortcutforge build SOURCE.cherri -o FILE` | 別途インストールしたCherriで未署名ビルド |
| `shortcutforge validate FILE` | plist構造を検査（Appleアクションの意味は未検証） |
| `shortcutforge inspect FILE` | 実行せずにワークフロー情報とアクション識別子を表示 |
| `shortcutforge actions list --os VERSION` | 指定iOS版の調査カタログを検索 |
| `shortcutforge sign FILE` | 既定でShortcuty署名。Windowsで使える署名方式はShortcutyのみ |

`shortcutforge COMMAND --help`で詳細を確認できます。対応する非Windows環境ではHubSignまたはApple純正macOSコマンドも選べます。[署名手順](docs/signing-validation.md)を参照してください。

## 制限と検証状況

- JSONの生成スキーマは調査カタログから絞り込んだ一部です。未対応のパラメーター形式を持つ識別子は名前付きアクションとしてビルドできません。
- plistとして有効でも、ショートカットAppが認識・読み込み・実行できることの証明にはなりません。
- Cherriは別プロジェクトです。WindowsではIf/Repeat例をスモークテストしましたが、全機能・全リリースの動作保証ではありません。
- iOS 27の根拠はSimulatorでの観測です。iOS 17・18・26は情報が部分的または不明です。
- 実機iPhoneでの読み込み・実行テストは未実施です。iOS 27への読み込みも未検証です。
- [iOS版別の互換性根拠と検証状況](docs/action-compatibility.md)を参照してください。
- ビルド結果は未署名です。ShortcutyとHubSignはショートカットを外部サービスへ送信し、Apple純正macOS署名も検証のためAppleへコピーを送ります。WindowsではShortcuty以外の署名方式は研究中です。

## 開発

```sh
python -m unittest discover -s tests -v
python -m compileall -q src
```

[アーキテクチャ](docs/architecture.md)、[セキュリティ](docs/security.md)、[貢献ガイド](docs/contributing.md)、[AGENTS.md](AGENTS.md)を確認してください。このPublicリポジトリはGitHubテンプレートでもあります。派生リポジトリ作成前に[テンプレート利用ガイド](docs/template-and-release.md)を参照してください。
